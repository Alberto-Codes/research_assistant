"""
Tests for the logging_config module.

This module tests the functionality of the logging configuration utilities.
"""

import io
import logging
import os
import sys
import tempfile
from unittest.mock import patch

import pytest

from research_agent.core.logging_config import configure_logging


def test_configure_logging_default():
    """Test that configure_logging works with default parameters."""
    # Arrange
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level

    # Act
    with patch("logging.info") as mock_info:
        configure_logging()

    # Assert
    assert mock_info.called
    assert mock_info.call_args[0][0] == "Logging configured at %s level"
    assert mock_info.call_args[0][1] == "INFO"

    # Check that handlers were added
    assert len(root_logger.handlers) >= 1

    # Cleanup
    root_logger.handlers = original_handlers
    root_logger.setLevel(original_level)


def test_configure_logging_custom_level():
    """Test that configure_logging works with a custom log level."""
    # Arrange
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level

    # Act
    with patch("logging.info") as mock_info:
        configure_logging(log_level="DEBUG")

    # Assert
    assert root_logger.level == logging.DEBUG
    assert mock_info.called
    assert mock_info.call_args[0][0] == "Logging configured at %s level"
    assert mock_info.call_args[0][1] == "DEBUG"

    # Cleanup
    root_logger.handlers = original_handlers
    root_logger.setLevel(original_level)


def test_configure_logging_with_file():
    """Test that configure_logging works with a log file."""
    # Arrange
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level

    # Create a temporary file for logging
    temp_dir = tempfile.mkdtemp()
    log_file = os.path.join(temp_dir, "test_log.log")

    try:
        # Act
        with patch("logging.info") as mock_info:
            configure_logging(log_file=log_file)

        # Assert
        assert mock_info.called
        assert os.path.exists(log_file)

        # Check that a file handler was added
        file_handlers = [h for h in root_logger.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) >= 1
        assert file_handlers[0].baseFilename == log_file

        # Close all file handlers to prevent file locks
        for handler in file_handlers:
            handler.close()
            root_logger.removeHandler(handler)

    finally:
        # Cleanup
        root_logger.handlers = original_handlers
        root_logger.setLevel(original_level)

        # Clean up the temp directory
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
            os.rmdir(temp_dir)
        except (PermissionError, OSError):
            pass  # Ignore errors in cleanup


def test_configure_logging_no_timestamp():
    """Test that configure_logging works without timestamps."""
    # Arrange
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level

    # Act
    with patch("logging.info") as mock_info:
        configure_logging(include_timestamp=False)

    # Assert
    assert mock_info.called

    # Check formatter pattern (should not contain asctime)
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            formatter_pattern = handler.formatter._fmt
            assert "%(asctime)s" not in formatter_pattern
            assert "%(levelname)s" in formatter_pattern

    # Cleanup
    root_logger.handlers = original_handlers
    root_logger.setLevel(original_level)


def test_configure_logging_removes_existing_handlers():
    """Test that configure_logging removes existing handlers."""
    # Arrange
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers.copy()
    original_level = root_logger.level

    # Add a test handler
    test_handler = logging.StreamHandler(io.StringIO())
    root_logger.addHandler(test_handler)

    # Act
    with patch("logging.info") as mock_info:
        configure_logging()

    # Assert
    assert mock_info.called
    assert test_handler not in root_logger.handlers

    # Cleanup
    root_logger.handlers = original_handlers
    root_logger.setLevel(original_level)


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
