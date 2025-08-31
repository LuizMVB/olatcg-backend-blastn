from __future__ import annotations
import psycopg2
from typing import Callable


def connection_factory(dbname: str, user: str, password: str, host: str, port: int = 5432) -> Callable[[], "psycopg2.extensions.connection"]:
    def factory():
        return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )
    return factory
