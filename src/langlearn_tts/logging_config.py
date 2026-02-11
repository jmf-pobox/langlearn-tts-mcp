"""Logging configuration for langlearn-tts."""

from __future__ import annotations

import logging.config
from pathlib import Path

_LOG_DIR = Path.home() / ".langlearn-tts" / "logs"
_LOG_FILE = _LOG_DIR / "langlearn-tts.log"

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_MAX_BYTES = 5_242_880  # 5 MB
_BACKUP_COUNT = 5


def configure_logging(*, stderr_level: str = "WARNING") -> None:
    """Configure logging with rotating file and stderr handlers.

    File handler is always active at INFO level.
    Stderr handler level is controlled by the caller.
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": _FORMAT,
                    "datefmt": _DATE_FORMAT,
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": str(_LOG_FILE),
                    "maxBytes": _MAX_BYTES,
                    "backupCount": _BACKUP_COUNT,
                    "formatter": "standard",
                    "level": "INFO",
                },
                "stderr": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                    "formatter": "standard",
                    "level": stderr_level,
                },
            },
            "root": {
                "level": "DEBUG",
                "handlers": ["file", "stderr"],
            },
            "loggers": {
                "boto3": {"level": "WARNING"},
                "botocore": {"level": "WARNING"},
                "urllib3": {"level": "WARNING"},
                "s3transfer": {"level": "WARNING"},
            },
        }
    )
