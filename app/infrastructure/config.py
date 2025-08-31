from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    db_name: str
    db_user: str
    db_pass: str
    db_host: str
    storage_root: str
    taxid_map_file: str
    nodes_file: str
    names_file: str
    log_level: str = "INFO"

    @staticmethod
    def from_env() -> "AppConfig":
        return AppConfig(
            db_name=os.environ.get("DB_NAME", ""),
            db_user=os.environ.get("DB_USER", ""),
            db_pass=os.environ.get("DB_PASS", ""),
            db_host=os.environ.get("DB_HOST", "localhost"),
            storage_root=os.environ.get("STORAGE_FILE", "/mnt/data/blastn_storage"),
            taxid_map_file=os.environ.get("TAXID_MAP_FILE", ""),
            nodes_file=os.environ.get("NODES_FILE", ""),
            names_file=os.environ.get("NAMES_FILE", ""),
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )
