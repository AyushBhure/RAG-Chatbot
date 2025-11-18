"""Application-wide logging configuration."""

import logging
from logging.config import dictConfig


def configure_logging() -> None:
    """Configure structured logging for the service."""

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "level": "INFO",
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                }
            },
            "loggers": {
                "": {"handlers": ["default"], "level": "INFO"},
                "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            },
        }
    )


configure_logging()

logger = logging.getLogger("rag_chatbot")

