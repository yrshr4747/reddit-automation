"""
utils/logger.py
===============
Centralized logging configuration for the Reddit Automation API.

- Logs to both console and a rotating log file (logs/app.log)
- Timestamps every log entry
- Log level configurable via LOG_LEVEL environment variable
"""

import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance.

    Args:
        name (str): Logger name (typically __name__ from the calling module)

    Returns:
        logging.Logger: Configured logger with console + file handlers
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # Avoid adding duplicate handlers

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler (max 5MB per file, keep 3 backups)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
