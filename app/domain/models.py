from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AnalysisInput:
    analysis_id: int
    sequences: List[str]
    database: str
    evalue: float
    gap_open: Optional[int] = None
    gap_extend: Optional[int] = None
    penalty: Optional[int] = None


@dataclass
class Hit:
    subject_id: str
    tax_id: Optional[str]
    lineage: str
    percent_identity: float
    alignment_length: int
    query_length: int
    subject_length: int
    score: float
    evalue: float
    query_sequence: str
    subject_sequence: str


@dataclass
class QueryResult:
    query_id: str
    query_title: str
    query_len: int
    hits: List[Hit] = field(default_factory=list)


@dataclass
class HomologyResults:
    results: Dict[str, QueryResult]  # keyed by query_id


@dataclass
class TaxonomyNodes:
    parent_by_id: Dict[str, str]     # tax_id -> parent_id
    rank_by_id: Dict[str, str]       # tax_id -> rank


@dataclass
class TaxonomyNames:
    scientific_by_id: Dict[str, str] # tax_id -> scientific name
