from __future__ import annotations
import datetime
import logging
import os
import tempfile
from typing import Dict, List

from domain.models import AnalysisInput, HomologyResults, QueryResult, Hit
from domain.ports import StorageService, BlastExecutor, TaxonomyRepository, AnalysisRepository
from domain.exceptions import InvalidInputError

logger = logging.getLogger(__name__)


class PerformHomologyAnalysis:
    """Use case orchestrating the BLASTN homology analysis."""

    def __init__(
        self,
        storage: StorageService,
        blast: BlastExecutor,
        taxonomy_repo: TaxonomyRepository,
        analysis_repo: AnalysisRepository,
    ) -> None:
        self.storage = storage
        self.blast = blast
        self.taxonomy_repo = taxonomy_repo
        self.analysis_repo = analysis_repo

    def execute(self, analysis_input: AnalysisInput) -> Dict:
        if not analysis_input.sequences:
            raise InvalidInputError("No sequences provided.")

        query_titles: Dict[str, str] = {}
        # 1) Build a temporary FASTA with >query_N headers
        query_tmp = self._build_temp_query_fasta(analysis_input.sequences, query_titles)
        try:
            # 2) Persist compressed query in shared storage
            query_gz_path = self.storage.store_compressed(query_tmp, analysis_input.analysis_id, "blastn_input")
        finally:
            self._safe_remove(query_tmp)

        # 3) Load taxonomy (in-memory maps)
        taxid_map = self.taxonomy_repo.get_taxid_map()
        nodes = self.taxonomy_repo.get_nodes()
        names = self.taxonomy_repo.get_names()

        # 4) Run BLAST+ and get compressed archive (format 11)
        archive_gz = self.blast.run_archive(
            query_gzip_path=query_gz_path,
            analysis_id=analysis_input.analysis_id,
            db=analysis_input.database,
            evalue=analysis_input.evalue,
            gapopen=analysis_input.gap_open,
            gapextend=analysis_input.gap_extend,
            penalty=analysis_input.penalty,
        )

        # 5) Convert archive to tabular fmt6 (gz), parse, and persist outputs
        fmt6_gz = self.blast.archive_to_fmt6(archive_gz, analysis_input.analysis_id)
        results = self._parse_fmt6(fmt6_gz, query_titles, taxid_map, nodes.parent_by_id, names.scientific_by_id)

        # 6) Persist input/output metadata
        init_dt = datetime.datetime.now()
        input_id = self.analysis_repo.insert_input(init_dt, command=None, analysis_id=analysis_input.analysis_id)

        finish_dt = datetime.datetime.now()
        self.analysis_repo.insert_output(finish_dt, results, archive_gz, input_id)
        self.analysis_repo.update_status(analysis_input.analysis_id, "SUCCEEDED")

        return results

    # ---------- helpers ----------

    def _build_temp_query_fasta(self, sequences: List[str], query_titles: Dict[str, str]) -> str:
        fd, path = tempfile.mkstemp(suffix=".fasta")
        with os.fdopen(fd, "wb") as fh:
            idx = 0
            for seq in sequences:
                if not seq:
                    continue
                idx += 1
                qid = f"query_{idx}"
                query_titles[qid] = qid
                fh.write(f">{qid} {qid}\n{seq}\n".encode())
        size = os.path.getsize(path)
        if size == 0:
            raise InvalidInputError("Error - No valid sequences provided.")
        logger.info("Created temp query FASTA at %s (size=%d)", path, size)
        return path

    def _parse_fmt6(self, fmt6_gz_path: str, query_titles: Dict[str, str],
                    taxid_map: Dict[str, str], parent_by_id: Dict[str, str], names_by_id: Dict[str, str]) -> Dict:
        # Decompress to a temp file for parsing
        tmp_txt = self.storage.decompress_to_temp(fmt6_gz_path, suffix=".txt")
        try:
            parsed: Dict[str, Dict] = {}
            with open(tmp_txt, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, start=1):
                    cols = line.rstrip("\n").split("\t")
                    if len(cols) < 10:
                        logger.warning("Skipping line %d: expected >=10 columns, got %d", line_no, len(cols))
                        continue

                    query_id = cols[0]
                    if query_id in parsed:
                        # keep first/best hit only (max_target_seqs=1 already enforces)
                        continue

                    # defensive subject parsing
                    subj_parts = cols[1].split('|')
                    subject_id = subj_parts[1] if len(subj_parts) > 1 else cols[1]

                    tx = taxid_map.get(subject_id)  # may be None
                    lineage = self._build_lineage(subject_id, tx, parent_by_id, names_by_id)

                    hit = {
                        'subject_id': cols[1],
                        'tax_id': tx,
                        'lineage': lineage,
                        'percent_identity': float(cols[2]),
                        'alignment_length': int(cols[3]),
                        'query_length': int(cols[4]),
                        'subject_length': int(cols[5]),
                        'score': float(cols[6]),
                        'evalue': float(cols[7]),
                        'query_sequence': cols[8],
                        'subject_sequence': cols[9],
                    }

                    parsed[query_id] = {
                        'query_id': query_id,
                        'query_title': query_titles.get(query_id, ''),
                        'query_len': hit['query_length'],
                        'hits': [hit],
                    }
            return parsed
        finally:
            self._safe_remove(tmp_txt)

    def _build_lineage(self, subject_id: str, tax_id: str | None,
                       parent_by_id: Dict[str, str], names_by_id: Dict[str, str]) -> str:
        if not tax_id:
            return 'unknown'

        lineage: List[str] = []
        current = tax_id
        # Traverse up until root '1' or missing node
        while current and current != '1':
            name = names_by_id.get(current, 'unknown')
            lineage.append(name)
            current = parent_by_id.get(current)
            if not current:
                break
        return '; '.join(reversed(lineage))

    def _safe_remove(self, path: str) -> None:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except Exception:  # best-effort cleanup
            logger.exception("Failed to remove temp file %s", path)
