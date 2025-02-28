"""
Tests for the CLI functionality in main.py.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, ANY

from hello_world.state import MyState
from src.main import main, cli_entry, CustomLLMClient


@pytest.mark.asyncio
async def test_custom_llm_client():
    """Test that the CustomLLMClient generates expected responses."""
    # Arrange
    client = CustomLLMClient()
    
    # Act
    hello_response = await client.generate_text("Generate a greeting word like 'Hello'")
    world_response = await client.generate_text("Generate a noun like 'World'")
    other_response = await client.generate_text("Generate something else")
    
    # Assert
    assert hello_response == "Hello"
    assert world_response == "World"
    assert other_response == "Response"


@pytest.mark.asyncio
async def test_custom_llm_client_with_prefix():
    """Test that the CustomLLMClient respects the prefix."""
    # Arrange
    client = CustomLLMClient(prefix="Test")
    
    # Act
    hello_response = await client.generate_text("Generate a greeting word like 'Hello'")
    world_response = await client.generate_text("Generate a noun like 'World'")
    
    # Assert
    assert hello_response == "Test Hello"
    assert world_response == "Test World"


@pytest.mark.asyncio
@patch("src.main.run_graph")
@patch("src.main.display_results")
@patch("argparse.ArgumentParser.parse_args")
async def test_main_with_default_args(mock_parse_args, mock_display_results, mock_run_graph):
    """Test that main runs correctly with default arguments."""
    # Arrange
    mock_args = MagicMock()
    mock_args.hello = ""
    mock_args.world = ""
    mock_args.prefix = ""
    mock_args.use_custom_llm = False
    mock_parse_args.return_value = mock_args
    
    mock_result = ("Hello World!", MyState(), [])
    mock_run_graph.return_value = mock_result
    
    # Act
    await main()
    
    # Assert
    mock_run_graph.assert_called_once()
    assert mock_run_graph.call_args[0][0].hello_text == ""  # Initial state
    assert mock_run_graph.call_args[0][1] is None  # No custom dependencies


@pytest.mark.asyncio
@patch("src.main.run_graph")
@patch("src.main.display_results")
@patch("argparse.ArgumentParser.parse_args")
async def test_main_with_custom_args(mock_parse_args, mock_display_results, mock_run_graph):
    """Test that main respects custom command line arguments."""
    # Arrange
    mock_args = MagicMock()
    mock_args.hello = "Custom Hello"
    mock_args.world = "Custom World"
    mock_args.prefix = "AI"
    mock_args.use_custom_llm = True
    mock_parse_args.return_value = mock_args
    
    mock_result = ("AI Custom Hello AI Custom World!", MyState(), [])
    mock_run_graph.return_value = mock_result
    
    # Act
    await main()
    
    # Assert
    mock_run_graph.assert_called_once()
    
    # Check that initial state was set correctly
    assert mock_run_graph.call_args[0][0].hello_text == "Custom Hello"
    assert mock_run_graph.call_args[0][0].world_text == "Custom World"
    
    # Check that dependencies were created with custom LLM client
    assert mock_run_graph.call_args[0][1] is not None
    assert isinstance(mock_run_graph.call_args[0][1].llm_client, CustomLLMClient)
    

def test_cli_entry():
    """Test that cli_entry correctly calls asyncio.run with main."""
    # We need to patch at the module level where it's used
    with patch("asyncio.run") as mock_asyncio_run:
        with patch("src.main.main") as mock_main:
            # Act
            cli_entry()
            
            # Assert
            mock_asyncio_run.assert_called_once_with(ANY)  # We can't check exact coroutine equality 