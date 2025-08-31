from __future__ import annotations
import gzip
import os
import shutil
import tempfile
from typing import Final

from domain.exceptions import StorageError
from domain.ports import StorageService


class FileSystemStorage(StorageService):
    def __init__(self, storage_root: str) -> None:
        self._root: Final[str] = storage_root

    def store_compressed(self, file_path: str, analysis_id: int, file_type: str) -> str:
        if not os.path.exists(file_path):
            raise StorageError(f"Source file not found: {file_path}")

        out_dir = os.path.join(self._root, f"analysis_{analysis_id}")
        os.makedirs(out_dir, exist_ok=True)
        out_gz = os.path.join(out_dir, f"{file_type}.txt.gz")

        try:
            with open(file_path, "rb") as f_in, gzip.open(out_gz, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            raise StorageError(f"Failed to store compressed file at {out_gz}") from e

        if not os.path.exists(out_gz):
            raise StorageError(f"Compressed file was not created at {out_gz}")

        return out_gz

    def decompress_to_temp(self, gzip_path: str, suffix: str) -> str:
        if not os.path.exists(gzip_path):
            raise StorageError(f"GZip file not found: {gzip_path}")
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix).name
        try:
            with gzip.open(gzip_path, "rb") as f_in, open(tmp, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception as e:
            raise StorageError(f"Failed to decompress {gzip_path}") from e
        return tmp
