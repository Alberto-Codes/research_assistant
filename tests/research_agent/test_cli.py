"""
Tests for the CLI interface.

This module tests the command-line interface functionality for the Research Agent application,
including argument parsing, execution, and output handling.
"""

import argparse
import asyncio
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from research_agent.api.services import generate_ai_response
from research_agent.core.gemini.dependencies import GeminiDependencies
from research_agent.core.gemini.state import GeminiState
from research_agent.main import (
    get_streamlit_script_path,
    main,
    main_async,
    run_cli_async,
    run_streamlit,
)


@pytest.mark.asyncio
@patch("research_agent.main.run_streamlit")
@patch("research_agent.main.run_cli_async")
@patch("research_agent.main.configure_logging")
@patch("research_agent.main.create_parser")
async def test_main_async_calls_correct_interface(
    mock_create_parser, mock_configure_logging, mock_run_cli_async, mock_run_streamlit
):
    """Test that main_async calls the correct interface handler based on args."""
    # Arrange
    mock_parser = MagicMock()
    mock_create_parser.return_value = mock_parser

    # Test CLI interface
    cli_args = MagicMock()
    cli_args.interface = "cli"
    cli_args.log_level = "INFO"
    cli_args.log_file = None
    mock_parser.parse_args.return_value = cli_args
    mock_run_cli_async.return_value = 0

    # Act
    result = await main_async(["cli", "gemini"])

    # Assert
    mock_configure_logging.assert_called_once_with(log_level="INFO", log_file=None)
    mock_run_cli_async.assert_called_once_with(cli_args)
    assert result == 0

    # Reset mocks
    mock_parser.parse_args.reset_mock()
    mock_run_cli_async.reset_mock()
    mock_configure_logging.reset_mock()

    # Test UI interface
    ui_args = MagicMock()
    ui_args.interface = "ui"
    ui_args.log_level = "DEBUG"
    ui_args.log_file = "test.log"
    mock_parser.parse_args.return_value = ui_args
    mock_run_streamlit.return_value = 0

    # Act
    result = await main_async(["ui"])

    # Assert
    mock_configure_logging.assert_called_once_with(log_level="DEBUG", log_file="test.log")
    mock_run_streamlit.assert_called_once_with(ui_args)
    assert result == 0


@pytest.mark.asyncio
@patch("research_agent.main.run_gemini_command")
@patch("research_agent.main.run_ingest_command")
async def test_run_cli_async(mock_run_ingest_command, mock_run_gemini_command):
    """Test that run_cli_async calls the correct command handler."""
    # Arrange
    args = MagicMock()
    args.command = "gemini"
    mock_run_gemini_command.return_value = 0

    # Act - test with gemini command
    result = await run_cli_async(args)

    # Assert
    mock_run_gemini_command.assert_called_once_with(args)
    mock_run_ingest_command.assert_not_called()
    assert result == 0

    # Reset mocks
    mock_run_gemini_command.reset_mock()

    # Test with ingest command
    args.command = "ingest"
    mock_run_ingest_command.return_value = 0

    # Act
    result = await run_cli_async(args)

    # Assert
    mock_run_ingest_command.assert_called_once_with(args)
    mock_run_gemini_command.assert_not_called()
    assert result == 0

    # Test with unknown command
    args.command = "unknown"

    # Act
    result = await run_cli_async(args)

    # Assert
    assert result == 1  # Should return error code


@patch("research_agent.main.subprocess.run")
@patch("research_agent.main.get_streamlit_script_path")
def test_run_streamlit(mock_get_path, mock_subprocess_run):
    """Test that run_streamlit launches the Streamlit application."""
    # Arrange
    mock_get_path.return_value = "/mock/path/to/app.py"
    args = MagicMock()
    args.port = 8501

    # Act
    result = run_streamlit(args)

    # Assert
    mock_get_path.assert_called_once()
    mock_subprocess_run.assert_called_once_with(
        ["streamlit", "run", "/mock/path/to/app.py", "--server.port", "8501"], check=True
    )
    assert result == 0


@patch("research_agent.main.subprocess.run")
@patch("research_agent.main.get_streamlit_script_path")
def test_run_streamlit_file_not_found(mock_get_path, mock_subprocess_run):
    """Test that run_streamlit handles FileNotFoundError."""
    # Arrange
    mock_get_path.side_effect = FileNotFoundError("No Streamlit application found")
    args = MagicMock()
    args.port = 8501

    # Act
    result = run_streamlit(args)

    # Assert
    assert result == 1
    mock_subprocess_run.assert_not_called()


def test_get_streamlit_script_path():
    """Test that get_streamlit_script_path finds an appropriate script."""
    try:
        path = get_streamlit_script_path()
        assert path is not None
        assert isinstance(path, str)
        assert "streamlit" in path
        assert path.endswith(".py")
    except FileNotFoundError:
        pytest.skip(
            "Skipping test because Streamlit app not found - this is expected in CI environments"
        )


@pytest.mark.asyncio
@patch("research_agent.core.gemini.dependencies.GeminiLLMClient")
async def test_generate_ai_response(mock_gemini_class):
    """Test that generate_ai_response works correctly."""
    # Arrange
    mock_instance = MagicMock()
    mock_instance.generate_text = AsyncMock(return_value="This is a test response.")
    mock_gemini_class.return_value = mock_instance

    # Act
    result = await generate_ai_response("Test prompt")

    # Assert
    assert isinstance(result, GeminiState)
    assert result.user_prompt == "Test prompt"
    assert result.ai_response == "This is a test response."


@patch("research_agent.main.asyncio.run")
@patch("research_agent.main.main_async")
@patch("research_agent.main.sys.exit")
def test_main(mock_sys_exit, mock_main_async, mock_asyncio_run):
    """Test that main() sets up asyncio and exits with the correct code."""
    # Arrange
    mock_asyncio_run.return_value = 42  # arbitrary exit code

    # Act
    main()

    # Assert
    mock_main_async.assert_called_once()
    mock_asyncio_run.assert_called_once()
    mock_sys_exit.assert_called_once_with(42)


@patch("research_agent.main.main")
def test_cli_entry(mock_main):
    """Test that cli_entry() calls main()."""
    # Act
    from research_agent.main import cli_entry

    cli_entry()

    # Assert
    mock_main.assert_called_once()


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
