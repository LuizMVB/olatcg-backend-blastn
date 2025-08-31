from __future__ import annotations
import json
from typing import Callable, Dict
from psycopg2.extras import Json as PgJson

from domain.ports import AnalysisRepository
from domain.exceptions import RepositoryError


class Psycopg2AnalysisRepository(AnalysisRepository):
    def __init__(self, conn_factory: Callable):
        self._conn_factory = conn_factory

    def insert_input(self, created_at, command, analysis_id: int) -> int:
        sql = """
            INSERT INTO core_analysisinput (created_at, command, analysis_id)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        with self._conn_factory() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (created_at, command, analysis_id))
                    input_id = cur.fetchone()[0]
                conn.commit()
                return input_id
            except Exception as e:
                conn.rollback()
                raise RepositoryError("Failed to insert analysis input") from e

    def insert_output(self, created_at, results: Dict, file_path: str, input_id: int) -> None:
        sql = """
            INSERT INTO core_analysisoutput (created_at, results, file, input_id)
            VALUES (%s, %s, %s, %s);
        """
        with self._conn_factory() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (created_at, PgJson(results), file_path, input_id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise RepositoryError("Failed to insert analysis output") from e

    def update_status(self, analysis_id: int, status: str) -> None:
        sql = """
            UPDATE core_analysis
            SET status = %s
            WHERE id = %s
        """
        with self._conn_factory() as conn:
            try:
                with conn.cursor() as cur:
                    cur.execute(sql, (status, analysis_id))
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise RepositoryError("Failed to update analysis status") from e
