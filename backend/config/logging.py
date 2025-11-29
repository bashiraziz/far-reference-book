"""
Logging configuration for the application.
"""

import logging
import sys
from backend.config.settings import settings


def configure_logging():
    """Configure application-wide logging."""

    # Create logger
    logger = logging.getLogger("backend")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.log_level.upper()))

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    logger.info(f"Logging configured with level: {settings.log_level}")

    return logger


# Configure logging on import
logger = configure_logging()
