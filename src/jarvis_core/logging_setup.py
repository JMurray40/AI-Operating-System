"""Structured, side-effect-free logging setup (no sensitive content)."""
from __future__ import annotations

import logging

from jarvis_core.config import LogLevel

_CONFIGURED = False


def configure_logging(level: LogLevel = LogLevel.INFO) -> logging.Logger:
    """Configure the package logger once and return it."""
    global _CONFIGURED
    logger = logging.getLogger("jarvis_core")
    if not _CONFIGURED:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        _CONFIGURED = True
    logger.setLevel(level.value)
    return logger


def get_logger() -> logging.Logger:
    """Return the package logger."""
    return logging.getLogger("jarvis_core")
