from __future__ import annotations
import json
import logging
from typing import Any

from application.use_cases import PerformHomologyAnalysis
from domain.models import AnalysisInput
from domain.exceptions import DomainError
from infrastructure.config import AppConfig
from infrastructure.logging_setup import setup_logging
from infrastructure.storage import FileSystemStorage
from infrastructure.blast import BlastPlusExecutor
from infrastructure.taxonomy import FileTaxonomyRepository
from infrastructure.db import connection_factory
from infrastructure.repositories import Psycopg2AnalysisRepository

logger = logging.getLogger(__name__)

# We keep the exact signature to be drop-in with your RabbitMQ consumer
def blastn_callback(ch, method, properties, body) -> None:
    cfg = AppConfig.from_env()
    setup_logging(cfg.log_level)

    logger.info("Started processing BLASTN job...")

    # Wire dependencies
    storage = FileSystemStorage(cfg.storage_root)
    blast = BlastPlusExecutor(storage)
    tax_repo = FileTaxonomyRepository(cfg.taxid_map_file, cfg.nodes_file, cfg.names_file)
    conn_factory = connection_factory(cfg.db_name, cfg.db_user, cfg.db_pass, cfg.db_host)
    analysis_repo = Psycopg2AnalysisRepository(conn_factory)
    use_case = PerformHomologyAnalysis(storage, blast, tax_repo, analysis_repo)

    try:
        data = json.loads(body)
        inp = AnalysisInput(
            analysis_id=int(data["analysis_id"]),
            sequences=list(data["parameters"]["sequences"]),
            database=data["parameters"]["database"],
            evalue=float(data["parameters"]["evalue"]),
            gap_open=data["parameters"].get("gap_open"),
            gap_extend=data["parameters"].get("gap_extend"),
            penalty=data["parameters"].get("penalty"),
        )

        results = use_case.execute(inp)
        logger.info("Finished processing BLASTN job. %d queries parsed.", len(results))

    except DomainError as de:
        logger.exception("Domain error in BLASTN job: %s", de)
        # best-effort update status to FAILED
        try:
            analysis_repo.update_status(int(json.loads(body).get("analysis_id")), "FAILED")
        except Exception:
            logger.exception("Failed to set FAILED status")
    except Exception as e:
        logger.exception("Unhandled error in BLASTN job: %s", e)
        try:
            analysis_repo.update_status(int(json.loads(body).get("analysis_id")), "FAILED")
        except Exception:
            logger.exception("Failed to set FAILED status")
    finally:
        # Always ack the message
        if hasattr(ch, "basic_ack"):
            ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Job completed and acknowledged.")
