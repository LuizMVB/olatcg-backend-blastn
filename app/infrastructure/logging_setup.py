import logging
import os

def setup_logging(level: str = None) -> None:
    level_name = level or os.environ.get("LOG_LEVEL", "INFO")
    lvl = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
