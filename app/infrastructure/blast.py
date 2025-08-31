from __future__ import annotations
import os
import subprocess
import tempfile
from domain.exceptions import BlastError
from domain.ports import BlastExecutor, StorageService


class BlastPlusExecutor(BlastExecutor):
    def __init__(self, storage: StorageService) -> None:
        self.storage = storage

    def run_archive(self, query_gzip_path: str, analysis_id: int, db: str, evalue: float,
                    gapopen, gapextend, penalty) -> str:
        # Decompress query
        query_tmp = self.storage.decompress_to_temp(query_gzip_path, suffix=".fasta")
        out_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".out").name

        cmd = [
            "blastn",
            "-query", query_tmp,
            "-db", db,
            "-evalue", str(evalue),
            "-outfmt", "11",
            "-max_target_seqs", "1",
            "-out", out_tmp,
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise BlastError(f"blastn failed: {result.stderr}")
        finally:
            # no stdout piping to file, ensure file exists from -out
            try:
                os.remove(query_tmp)
            except Exception:
                pass

        # store compressed archive
        archive_gz = self.storage.store_compressed(out_tmp, analysis_id, "blastn_output_fmt_11")
        try:
            os.remove(out_tmp)
        except Exception:
            pass
        return archive_gz

    def archive_to_fmt6(self, archive_gzip_path: str, analysis_id: int) -> str:
        archive_tmp = self.storage.decompress_to_temp(archive_gzip_path, suffix=".archive")
        out_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name

        cmd = [
            "blast_formatter",
            "-archive", archive_tmp,
            "-outfmt", "6 qseqid sseqid pident length qlen slen score evalue qseq sseq",
            "-out", out_tmp,
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise BlastError(f"blast_formatter failed: {result.stderr}")
        finally:
            try:
                os.remove(archive_tmp)
            except Exception:
                pass

        fmt6_gz = self.storage.store_compressed(out_tmp, analysis_id, "blastn_output_fmt_6")
        try:
            os.remove(out_tmp)
        except Exception:
            pass
        return fmt6_gz
