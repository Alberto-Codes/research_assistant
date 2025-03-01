"""
Tests for the ingest command module.

This module tests the functionality of the document ingestion command,
including command setup and execution.
"""

import argparse
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research_agent.cli.commands.ingest import add_ingest_command, run_ingest_command


def test_add_ingest_command():
    """Test that add_ingest_command correctly adds the ingest command to subparsers."""
    # Arrange
    mock_subparsers = MagicMock()
    mock_parser = MagicMock()
    mock_subparsers.add_parser.return_value = mock_parser

    # Act
    add_ingest_command(mock_subparsers)

    # Assert
    mock_subparsers.add_parser.assert_called_once_with(
        "ingest",
        help="Ingest documents into ChromaDB",
        description="Ingest documents from a directory into a ChromaDB collection",
    )

    # Verify arguments are added correctly
    assert mock_parser.add_argument.call_count == 3

    # Check data-dir argument
    _, kwargs = mock_parser.add_argument.call_args_list[0]
    assert kwargs["type"] == str
    assert kwargs["default"] == "./data"
    assert "help" in kwargs

    # Check collection argument
    _, kwargs = mock_parser.add_argument.call_args_list[1]
    assert kwargs["type"] == str
    assert kwargs["default"] == "default_collection"
    assert "help" in kwargs

    # Check chroma-dir argument
    _, kwargs = mock_parser.add_argument.call_args_list[2]
    assert kwargs["type"] == str
    assert kwargs["default"] == "./chroma_db"
    assert "help" in kwargs


@pytest.mark.asyncio
@patch("research_agent.cli.commands.ingest.os.path.exists")
@patch("research_agent.cli.commands.ingest.os.path.isdir")
@patch("research_agent.cli.commands.ingest.load_documents_from_directory")
@patch("research_agent.cli.commands.ingest.run_document_ingestion_graph")
@patch("research_agent.cli.commands.ingest.os.makedirs")
async def test_run_ingest_command_success(
    mock_makedirs, mock_run_graph, mock_load_docs, mock_isdir, mock_exists
):
    """Test that run_ingest_command successfully runs with valid arguments."""
    # Arrange
    args = argparse.Namespace(
        data_dir="./test_data", collection="test_collection", chroma_dir="./test_chroma"
    )

    # Setup mocks
    mock_exists.return_value = True
    mock_isdir.return_value = True

    test_docs = [
        {"content": "Doc 1 content", "metadata": {"filename": "doc1.txt", "file_size": 100}},
        {"content": "Doc 2 content", "metadata": {"filename": "doc2.txt", "file_size": 150}},
    ]
    mock_load_docs.return_value = test_docs

    # Mock the graph execution
    mock_result = MagicMock()
    mock_state = MagicMock()
    mock_state.total_time = 1.234
    mock_run_graph.return_value = (mock_result, mock_state, [])

    # Act
    with patch("builtins.print") as mock_print:
        result = await run_ingest_command(args)

    # Assert
    assert result == 0
    mock_exists.assert_called_once_with("./test_data")
    mock_isdir.assert_called_once_with("./test_data")
    mock_load_docs.assert_called_once_with("./test_data")
    mock_makedirs.assert_called_once_with("./test_chroma", exist_ok=True)

    # Verify run_document_ingestion_graph was called with correct arguments
    mock_run_graph.assert_called_once()
    call_args = mock_run_graph.call_args[1]
    assert call_args["documents"] == ["Doc 1 content", "Doc 2 content"]
    assert call_args["collection_name"] == "test_collection"
    assert len(call_args["document_ids"]) == 2
    assert call_args["document_ids"][0].startswith("doc_0_doc1.txt")
    assert call_args["document_ids"][1].startswith("doc_1_doc2.txt")
    assert call_args["metadata"] == [
        {"filename": "doc1.txt", "file_size": 100},
        {"filename": "doc2.txt", "file_size": 150},
    ]
    assert call_args["persist_directory"] == "./test_chroma"

    # Check output was printed
    assert mock_print.call_count >= 5  # Multiple prints for results


@pytest.mark.asyncio
@patch("research_agent.cli.commands.ingest.os.path.exists")
@patch("research_agent.cli.commands.ingest.os.path.isdir")
async def test_run_ingest_command_invalid_directory(mock_isdir, mock_exists):
    """Test that run_ingest_command handles an invalid data directory."""
    # Arrange
    args = argparse.Namespace(
        data_dir="./nonexistent_dir", collection="test_collection", chroma_dir="./test_chroma"
    )

    # Setup mocks to indicate the directory doesn't exist
    mock_exists.return_value = False
    mock_isdir.return_value = False

    # Act
    result = await run_ingest_command(args)

    # Assert
    assert result == 1
    mock_exists.assert_called_once_with("./nonexistent_dir")


@pytest.mark.asyncio
@patch("research_agent.cli.commands.ingest.os.path.exists")
@patch("research_agent.cli.commands.ingest.os.path.isdir")
@patch("research_agent.cli.commands.ingest.load_documents_from_directory")
async def test_run_ingest_command_no_documents(mock_load_docs, mock_isdir, mock_exists):
    """Test that run_ingest_command handles the case when no documents are found."""
    # Arrange
    args = argparse.Namespace(
        data_dir="./empty_dir", collection="test_collection", chroma_dir="./test_chroma"
    )

    # Setup mocks
    mock_exists.return_value = True
    mock_isdir.return_value = True
    mock_load_docs.return_value = []  # No documents found

    # Act
    result = await run_ingest_command(args)

    # Assert
    assert result == 1
    mock_exists.assert_called_once_with("./empty_dir")
    mock_isdir.assert_called_once_with("./empty_dir")
    mock_load_docs.assert_called_once_with("./empty_dir")


@pytest.mark.asyncio
@patch("research_agent.cli.commands.ingest.os.path.exists")
@patch("research_agent.cli.commands.ingest.os.path.isdir")
@patch("research_agent.cli.commands.ingest.load_documents_from_directory")
@patch("research_agent.cli.commands.ingest.run_document_ingestion_graph")
@patch("research_agent.cli.commands.ingest.os.makedirs")
async def test_run_ingest_command_with_errors(
    mock_makedirs, mock_run_graph, mock_load_docs, mock_isdir, mock_exists
):
    """Test that run_ingest_command handles errors from the ingestion graph."""
    # Arrange
    args = argparse.Namespace(
        data_dir="./test_data", collection="test_collection", chroma_dir="./test_chroma"
    )

    # Setup mocks
    mock_exists.return_value = True
    mock_isdir.return_value = True

    test_docs = [
        {"content": "Doc 1 content", "metadata": {"filename": "doc1.txt", "file_size": 100}},
    ]
    mock_load_docs.return_value = test_docs

    # Mock the graph execution with errors
    mock_result = MagicMock()
    mock_state = MagicMock()
    errors = ["Error 1: File not processable", "Error 2: Invalid content"]
    mock_run_graph.return_value = (mock_result, mock_state, errors)

    # Act
    result = await run_ingest_command(args)

    # Assert
    assert result == 1
    mock_exists.assert_called_once_with("./test_data")
    mock_isdir.assert_called_once_with("./test_data")
    mock_load_docs.assert_called_once_with("./test_data")
    mock_makedirs.assert_called_once_with("./test_chroma", exist_ok=True)
    mock_run_graph.assert_called_once()


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
