import logging
import os
from pythonjsonlogger import json as jsonlogger

_SENSITIVE_KEYS = {"tollbitkey", "tollbit-token"}

LOG_LEVEL_ENV_VAR = "TOLLBIT_PYSDK_LOG_LEVEL"
REDACT_DISABLED_ENV_VAR = "TOLLBIT_PYSDK_LOG_REDACT_DISABLE_DANGEROUS_DANGEROUS"


class TollbitAuthHeadersFilter(logging.Filter):

    def filter(self, record: logging.LogRecord) -> bool:
        # Sanitize extra fields
        if hasattr(record, "__dict__"):
            headers = record.__dict__.get("headers")
            if headers and isinstance(headers, dict):
                headers_copy = headers.copy()
                for key in list(headers_copy.keys()):
                    if key.lower() in _SENSITIVE_KEYS:
                        headers_copy[key] = "[REDACTED]"
                record.__dict__["headers"] = headers_copy
        return True


def _build_sdk_root_logger(name: str) -> logging.Logger:
    """Return the root logger for the SDK."""
    logger = logging.getLogger(SDK_LOGGER_NAME)
    level_name = os.getenv("TOLLBIT_PYSDK_LOG_LEVEL", "WARNING")
    redact_sensitive = os.getenv(REDACT_DISABLED_ENV_VAR, "false").lower() != "true"
    level = getattr(logging, level_name.upper(), logging.WARNING)
    logger.setLevel(level)

    tb_filter = TollbitAuthHeadersFilter()
    # Add a StreamHandler if no handlers are present
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        handler.setFormatter(formatter)
        if redact_sensitive:
            handler.addFilter(tb_filter)
        logger.addHandler(handler)
    else:
        if redact_sensitive:
            for existing_handler in logger.handlers:
                existing_handler.addFilter(tb_filter)  # Scrub out sensitive info

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
