"""
Centralized logger using loguru.
All modules import get_logger() from here.
"""

import sys
from loguru import logger


def get_logger(name: str):
    """Return a named logger with structured formatting."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan> | {message}",
        level="INFO",
        colorize=True,
    )
    logger.add(
        f"logs/{name}.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
    )
    return logger.bind(name=name)