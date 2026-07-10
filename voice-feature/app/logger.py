"""
Centralized logging configuration for SafeSphere backend.

Usage:
    from app.logger import get_logger
    logger = get_logger("my_module")
    logger.info("session started | session_id=%s", sid)
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger with a consistent timestamp + level format.
    Multiple calls with the same name return the same logger (Python stdlib behaviour).
    """
    logger = logging.getLogger(f"safesphere.{name}")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        # Prevent log messages propagating to the root logger twice
        logger.propagate = False

    return logger
