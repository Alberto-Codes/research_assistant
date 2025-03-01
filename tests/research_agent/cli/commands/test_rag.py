"""
Tests for the rag command module.

This module tests the functionality of the Retrieval Augmented Generation (RAG) command,
including command setup and execution.
"""

import argparse
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research_agent.cli.commands.rag import add_rag_command, run_rag_command


def test_add_rag_command():
    """Test that add_rag_command correctly adds the RAG command to subparsers."""
    # Arrange
    mock_subparsers = MagicMock()
    mock_parser = MagicMock()
    mock_subparsers.add_parser.return_value = mock_parser

    # Act
    add_rag_command(mock_subparsers)

    # Assert
    mock_subparsers.add_parser.assert_called_once_with(
        "rag",
        help="Query documents using RAG with Gemini",
        description="Use Retrieval Augmented Generation to answer questions based on your documents",
    )

    # Verify arguments are added correctly
    assert mock_parser.add_argument.call_count >= 6  # There are 6 arguments in the RAG command

    # Check query argument
    _, kwargs = mock_parser.add_argument.call_args_list[0]
    assert kwargs["type"] == str
    assert kwargs["required"] is True
    assert "help" in kwargs

    # Check collection argument
    _, kwargs = mock_parser.add_argument.call_args_list[1]
    assert kwargs["type"] == str
    assert kwargs["default"] == "my_docs"
    assert "help" in kwargs

    # Check chroma-dir argument
    _, kwargs = mock_parser.add_argument.call_args_list[2]
    assert kwargs["type"] == str
    assert kwargs["default"] == "./chroma_db"
    assert "help" in kwargs


@pytest.mark.asyncio
@patch("research_agent.cli.commands.rag.run_rag_query")
@patch("research_agent.cli.commands.rag.chromadb.PersistentClient")
@patch("research_agent.cli.commands.rag.VertexAIModel")
@patch("research_agent.cli.commands.rag.Agent")
async def test_run_rag_command_success(
    mock_agent, mock_vertex_model, mock_chroma_client, mock_run_rag_query
):
    """Test that run_rag_command successfully runs with valid arguments."""
    # Arrange
    args = argparse.Namespace(
        query="What is RAG?",
        collection="test_collection",
        chroma_dir="./test_chroma",
        project_id="test-project",
        model="gemini-1.5-pro",
        region="us-central1",
    )

    # Setup mocks
    mock_collection = MagicMock()
    mock_collection.count.return_value = 5  # Simulate 5 documents in collection

    mock_client_instance = MagicMock()
    mock_client_instance.get_collection.return_value = mock_collection
    mock_chroma_client.return_value = mock_client_instance

    mock_model_instance = MagicMock()
    mock_vertex_model.return_value = mock_model_instance

    mock_agent_instance = MagicMock()
    mock_agent.return_value = mock_agent_instance

    # Setup mock response for run_rag_query
    mock_run_rag_query.return_value = {
        "answer": "RAG is Retrieval Augmented Generation...",
        "retrieval_time": 0.5,
        "generation_time": 1.2,
        "total_time": 1.7,
    }

    # Act
    with patch("builtins.print") as mock_print:
        result = await run_rag_command(args)

    # Assert
    assert result == 0
    mock_chroma_client.assert_called_once_with(path="./test_chroma")
    mock_client_instance.get_collection.assert_called_once_with("test_collection")
    mock_vertex_model.assert_called_once_with(
        model_name="gemini-1.5-pro", project_id="test-project", region="us-central1"
    )
    mock_agent.assert_called_once_with(mock_model_instance)
    mock_run_rag_query.assert_called_once_with(
        query="What is RAG?",
        chroma_collection=mock_collection,
        gemini_model=mock_agent_instance,
        project_id="test-project",
    )

    # Check that results were printed
    assert mock_print.call_count >= 5


@pytest.mark.asyncio
@patch("research_agent.cli.commands.rag.chromadb.PersistentClient")
async def test_run_rag_command_collection_not_found(mock_chroma_client):
    """Test that run_rag_command handles the case when collection is not found."""
    # Arrange
    args = argparse.Namespace(
        query="What is RAG?",
        collection="nonexistent_collection",
        chroma_dir="./test_chroma",
        project_id="test-project",
        model="gemini-1.5-pro",
        region="us-central1",
    )

    # Setup mocks to simulate collection not found
    mock_client_instance = MagicMock()
    mock_client_instance.get_collection.side_effect = Exception("Collection not found")
    mock_chroma_client.return_value = mock_client_instance

    # Act
    with patch("builtins.print") as mock_print:
        result = await run_rag_command(args)

    # Assert
    assert result == 1
    mock_chroma_client.assert_called_once_with(path="./test_chroma")
    mock_client_instance.get_collection.assert_called_once_with("nonexistent_collection")

    # Check that error message was printed
    mock_print.assert_called_with(
        "Error: Collection 'nonexistent_collection' not found. Please ingest documents first."
    )


@pytest.mark.asyncio
@patch("research_agent.cli.commands.rag.run_rag_query")
@patch("research_agent.cli.commands.rag.chromadb.PersistentClient")
@patch("research_agent.cli.commands.rag.VertexAIModel")
@patch("research_agent.cli.commands.rag.Agent")
async def test_run_rag_command_general_exception(
    mock_agent, mock_vertex_model, mock_chroma_client, mock_run_rag_query
):
    """Test that run_rag_command handles general exceptions properly."""
    # Arrange
    args = argparse.Namespace(
        query="What is RAG?",
        collection="test_collection",
        chroma_dir="./test_chroma",
        project_id="test-project",
        model="gemini-1.5-pro",
        region="us-central1",
    )

    # Setup mocks to raise an exception
    mock_collection = MagicMock()
    mock_client_instance = MagicMock()
    mock_client_instance.get_collection.return_value = mock_collection
    mock_chroma_client.return_value = mock_client_instance

    # Make run_rag_query raise an exception
    mock_run_rag_query.side_effect = Exception("Something went wrong during RAG query")

    # Act
    with patch("builtins.print") as mock_print:
        result = await run_rag_command(args)

    # Assert
    assert result == 1
    mock_run_rag_query.assert_called_once()
    mock_print.assert_called_with("Error: Something went wrong during RAG query")


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
