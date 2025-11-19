import logging
import os
from pythonjsonlogger import json as jsonlogger


def _build_sdk_root_logger(name: str) -> logging.Logger:
    """Return the root logger for the SDK."""
    logger = logging.getLogger(SDK_LOGGER_NAME)
    level_name = os.getenv("TOLLBIT_PYSDK_LOG_LEVEL", "WARNING")
    level = getattr(logging, level_name.upper(), logging.WARNING)
    logger.setLevel(level)

    # Add a StreamHandler if no handlers are present
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


SDK_LOGGER_NAME = "tollbit.python-sdk"
_logger = _build_sdk_root_logger(SDK_LOGGER_NAME)


def get_sdk_logger(name: str) -> logging.Logger:
    """Return a logger configured like the SDK root logger."""
    new_logger = logging.getLogger(f"{SDK_LOGGER_NAME}.{name}")

    parent_logger = _logger  # our root SDK logger

    # Copy handlers (defensive: avoid duplicates if called multiple times)
    new_logger.handlers.clear()
    for h in parent_logger.handlers:
        new_logger.addHandler(h)

    # Copy level and propagation behavior
    new_logger.setLevel(parent_logger.level)
    new_logger.propagate = parent_logger.propagate
    return new_logger
