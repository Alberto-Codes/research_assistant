"""
Logging configuration for the Research Agent application.

This module sets up centralized logging configuration that can be imported
and used by all other modules in the application.
"""

import logging
import os
import sys
from typing import Optional


def configure_logging(
    log_level: str = "INFO", log_file: Optional[str] = None, include_timestamp: bool = True
) -> None:
    """Configure logging for the entire application.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to a log file. If None, logs only to console.
        include_timestamp: Whether to include timestamps in log messages.
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create format string based on preferences
    log_format = "%(levelname)s - %(name)s - %(message)s"
    if include_timestamp:
        log_format = "%(asctime)s - " + log_format

    # Basic configuration
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)

    # File handler if specified
    if log_file:
        # Ensure directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates when reconfiguring
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add all handlers
    for handler in handlers:
        root_logger.addHandler(handler)

    # Set levels for specific modules if needed
    # For example, to make third-party libraries less verbose:
    # logging.getLogger("some_verbose_library").setLevel(logging.WARNING)

    # Log that configuration is complete
    logging.info("Logging configured at %s level", log_level)


# Default configuration to use if this module is imported directly
if __name__ == "__main__":
    configure_logging()
