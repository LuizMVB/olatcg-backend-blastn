from __future__ import annotations
from typing import Dict
from domain.models import TaxonomyNodes, TaxonomyNames
from domain.ports import TaxonomyRepository
from domain.exceptions import TaxonomyError


class FileTaxonomyRepository(TaxonomyRepository):
    def __init__(self, taxid_map_file: str, nodes_file: str, names_file: str) -> None:
        self._taxid_map_file = taxid_map_file
        self._nodes_file = nodes_file
        self._names_file = names_file

    def get_taxid_map(self) -> Dict[str, str]:
        if not self._taxid_map_file:
            raise TaxonomyError("TAXID_MAP_FILE not set")
        mapping: Dict[str, str] = {}
        with open(self._taxid_map_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    mapping[parts[0]] = parts[1]
        return mapping

    def get_nodes(self) -> TaxonomyNodes:
        if not self._nodes_file:
            raise TaxonomyError("NODES_FILE not set")
        parent_by_id = {}
        rank_by_id = {}
        with open(self._nodes_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    tax_id, parent_id, rank = parts[0], parts[1], parts[2]
                    parent_by_id[tax_id] = parent_id
                    rank_by_id[tax_id] = rank
        return TaxonomyNodes(parent_by_id=parent_by_id, rank_by_id=rank_by_id)

    def get_names(self) -> TaxonomyNames:
        if not self._names_file:
            raise TaxonomyError("NAMES_FILE not set")
        scientific_by_id = {}
        with open(self._names_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4 and parts[3] == "scientific name":
                    scientific_by_id[parts[0]] = parts[1]
        return TaxonomyNames(scientific_by_id=scientific_by_id)
