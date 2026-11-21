import logging

from agentos.config import settings


def configure_logging() -> None:
    log_level = getattr(logging, settings.log_level)

    logging.basicConfig(
        level=log_level,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.getLogger("agentos").setLevel(log_level)
