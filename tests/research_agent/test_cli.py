"""
Tests for the CLI interface.

This module tests the command-line interface functionality for the Research Agent application,
including argument parsing, execution, and output handling.
"""

import asyncio
from unittest.mock import ANY, MagicMock, patch

import pytest

from research_agent.api.services import generate_ai_response, generate_hello_world
from research_agent.cli.commands import display_results, main, parse_arguments
from research_agent.core.dependencies import HelloWorldDependencies
from research_agent.core.graph import GraphRunResult
from research_agent.core.state import MyState


@pytest.mark.asyncio
@patch("research_agent.api.services.run_graph")
@patch("research_agent.cli.commands.display_results")
@patch("research_agent.cli.commands.parse_arguments")
async def test_main_with_default_args(mock_parse_args, mock_display_results, mock_run_graph):
    """Test that main runs correctly with default arguments."""
    # Arrange
    mock_args = MagicMock()
    mock_args.command = "hello"
    mock_args.prefix = ""
    mock_parse_args.return_value = mock_args

    mock_state = MyState(combined_text="Hello World!")
    mock_run_graph.return_value = ("Hello World!", mock_state, [])

    # Act
    await main()

    # Assert
    mock_run_graph.assert_called_once()
    mock_display_results.assert_called_once_with(mock_state)


@pytest.mark.asyncio
@patch("research_agent.api.services.run_graph")
@patch("research_agent.cli.commands.display_results")
@patch("research_agent.cli.commands.parse_arguments")
async def test_main_with_custom_args(mock_parse_args, mock_display_results, mock_run_graph):
    """Test that main respects custom command line arguments."""
    # Arrange
    mock_args = MagicMock()
    mock_args.command = "hello"
    mock_args.prefix = "AI"
    mock_parse_args.return_value = mock_args

    mock_state = MyState(combined_text="AI Hello AI World!")
    mock_run_graph.return_value = ("AI Hello AI World!", mock_state, [])

    # Act
    await main()

    # Assert
    mock_run_graph.assert_called_once()
    mock_display_results.assert_called_once_with(mock_state)


@patch("sys.argv", ["__main__.py", "hello"])
@patch("asyncio.run")
def test_cli_entry(mock_asyncio_run):
    """Test that cli_entry correctly calls asyncio.run with main."""
    # Import cli_entry here to avoid issues with sys.argv patching
    from research_agent.cli.commands import cli_entry

    # Act
    cli_entry()

    # Assert
    mock_asyncio_run.assert_called_once_with(ANY)  # We can't check exact coroutine equality
