"""
Logging configuration and utilities
"""

import logging
import sys
from typing import Optional


def setup_logger(name: str = "watermark", verbose: bool = False) -> logging.Logger:
    """
    Set up logger with appropriate configuration

    Args:
        name: Logger name
        verbose: Enable verbose logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers
    if logger.handlers:
        return logger

    # Set logging level
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    if verbose:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter('%(levelname)s: %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


class LoggerMixin:
    """Mixin class to add logging functionality"""

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger