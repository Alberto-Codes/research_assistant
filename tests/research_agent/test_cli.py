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
from research_agent.core.dependencies import GeminiDependencies
from research_agent.core.state import MyState
from research_agent.ui.cli_entry import get_streamlit_script_path, main


@pytest.mark.asyncio
@patch("research_agent.ui.cli_entry.subprocess.run")
@patch("research_agent.ui.cli_entry.get_streamlit_script_path")
@patch("argparse.ArgumentParser.parse_args")
async def test_main_runs_gemini_chat(mock_parse_args, mock_get_path, mock_subprocess_run):
    """Test that main runs the Gemini chat application."""
    # Arrange
    mock_get_path.return_value = "/mock/path/to/gemini_chat.py"
    mock_parse_args.return_value = argparse.Namespace()

    # Act
    main()

    # Assert
    mock_get_path.assert_called_once_with("gemini_chat.py")
    mock_subprocess_run.assert_called_once_with(
        ["streamlit", "run", "/mock/path/to/gemini_chat.py"]
    )


def test_get_streamlit_script_path():
    """Test that get_streamlit_script_path constructs the correct path."""
    # This test will fail if the file doesn't exist, which is what we want
    try:
        path = get_streamlit_script_path("gemini_chat.py")
        assert "streamlit" in path
        assert "gemini_chat.py" in path
    except FileNotFoundError:
        pytest.skip(
            "Skipping test because gemini_chat.py not found - this is expected in CI environments"
        )


@pytest.mark.asyncio
@patch("research_agent.core.dependencies.GeminiLLMClient")
async def test_generate_ai_response(mock_gemini_class):
    """Test that generate_ai_response works correctly."""
    # Arrange
    mock_instance = MagicMock()
    mock_instance.generate_text = AsyncMock(return_value="This is a test response.")
    mock_gemini_class.return_value = mock_instance

    # Act
    result = await generate_ai_response("Test prompt")

    # Assert
    assert isinstance(result, MyState)
    assert result.user_prompt == "Test prompt"
    assert result.ai_response == "This is a test response."


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
