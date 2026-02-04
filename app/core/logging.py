"""
Logging configuration using Loguru.
Provides structured logging with different outputs for dev/prod.
"""

import sys
from pathlib import Path

from loguru import logger

from .config import settings


def setup_logging() -> None:
    """
    Configure application logging.
    Sets up console and file logging based on environment.
    """
    # Remove default handler
    logger.remove()

    # Log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Simple format for production
    simple_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
    )

    # Console handler
    logger.add(
        sys.stdout,
        format=log_format if settings.is_development else simple_format,
        level=settings.log_level,
        colorize=settings.is_development,
    )

    # File handler for production
    if settings.is_production:
        log_path = Path("logs")
        log_path.mkdir(exist_ok=True)

        # Error log
        logger.add(
            log_path / "error.log",
            format=simple_format,
            level="ERROR",
            rotation="10 MB",
            retention="30 days",
            compression="gz",
        )

        # General log
        logger.add(
            log_path / "app.log",
            format=simple_format,
            level="INFO",
            rotation="50 MB",
            retention="14 days",
            compression="gz",
        )

    logger.info(f"Logging configured - Level: {settings.log_level}")


def get_logger(name: str):
    """
    Get a logger instance with a custom name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logger.bind(name=name)
