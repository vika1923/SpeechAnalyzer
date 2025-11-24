"""
Unified logging configuration for SpeechAnalyzer backend.
This module provides a centralized logger that can be imported by all other modules.
"""

import logging
import os
from typing import Optional


class UnifiedLogger:
    """Singleton logger class to ensure consistent logging configuration across the application."""

    _instance: Optional["UnifiedLogger"] = None
    _initialized = False

    def __new__(cls) -> "UnifiedLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            UnifiedLogger._initialized = True

    def _setup_logging(self):
        """Configure the root logger with file and console handlers."""
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Configure root logger
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/api_server.log", mode="a"),
                logging.StreamHandler(),  # Console output
            ],
            force=True,  # Override any existing configuration
        )

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance for the specified module name."""
        return logging.getLogger(name)


# Initialize the unified logger
_unified_logger = UnifiedLogger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module name.

    Args:
        name: The name of the module requesting the logger (typically __name__)

    Returns:
        A configured logger instance
    """
    return _unified_logger.get_logger(name)


# For backward compatibility, create a default logger
logger = get_logger(__name__)
