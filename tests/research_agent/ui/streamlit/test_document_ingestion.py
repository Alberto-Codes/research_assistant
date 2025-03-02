"""
Tests for the document ingestion UI components.
"""

import asyncio
import os
import pytest
from unittest.mock import patch, MagicMock, mock_open, AsyncMock

import streamlit as st
from streamlit.testing.v1 import AppTest

from research_agent.ui.streamlit.document_ingestion import (
    render_document_ingestion_ui,
    ingest_uploaded_files
)


@pytest.mark.asyncio
@patch("research_agent.ui.streamlit.document_ingestion.ingest_documents_from_directory")
@patch("research_agent.ui.streamlit.document_ingestion.tempfile.TemporaryDirectory")
@patch("builtins.open", new_callable=mock_open)
async def test_ingest_uploaded_files_success(mock_file_open, mock_temp_dir, mock_ingest):
    """Test successful document ingestion."""
    # Configure mocks
    mock_temp_dir.return_value.__enter__.return_value = "/tmp/test_dir"
    
    # Mock the ingest result
    mock_ingest.return_value = {
        "success": True,
        "state": {
            "documents_count": 3,
            "collection_name": "test_collection",
            "total_time": 2.5
        },
        "result": {
            "ids": ["doc1", "doc2", "doc3"]
        }
    }
    
    # Mock file data
    uploaded_files = [
        MagicMock(name="file1"),
        MagicMock(name="file2")
    ]
    uploaded_files[0].name = "test1.txt"
    uploaded_files[0].getvalue.return_value = b"Test content 1"
    uploaded_files[1].name = "test2.txt"
    uploaded_files[1].getvalue.return_value = b"Test content 2"
    
    # Call the function
    result = await ingest_uploaded_files(
        uploaded_files=uploaded_files,
        collection_name="test_collection",
        persist_directory="./test_chroma_db"
    )
    
    # Assert results
    assert result["success"] is True
    assert result["state"]["documents_count"] == 3
    assert result["state"]["total_time"] == 2.5
    mock_ingest.assert_called_once_with(
        directory_path="/tmp/test_dir",
        collection_name="test_collection",
        persist_directory="./test_chroma_db"
    )
    
    # Verify that files were written to the temporary directory using os.path.join
    # to handle platform-specific path separators
    expected_path1 = os.path.join("/tmp/test_dir", "test1.txt")
    expected_path2 = os.path.join("/tmp/test_dir", "test2.txt")
    calls = mock_file_open.call_args_list
    paths = [call[0][0] for call in calls]
    
    assert expected_path1 in paths
    assert expected_path2 in paths


@pytest.mark.skip(reason="Streamlit UI tests are challenging to run in a test environment without a ScriptRunContext")
@patch("research_agent.ui.streamlit.document_ingestion.asyncio.run")
@patch("research_agent.ui.streamlit.document_ingestion.os.makedirs")
def test_render_document_ingestion_ui_basic(mock_makedirs, mock_asyncio_run):
    """Test the basic rendering of the document ingestion UI."""
    # Create a test app instance with the render function
    app_script = """
import streamlit as st
from research_agent.ui.streamlit.document_ingestion import render_document_ingestion_ui

render_document_ingestion_ui()
"""
    at = AppTest.from_string(app_script)
    
    # Run the app and check if it rendered correctly
    at.run()
    
    # Verify no exceptions occurred
    assert not at.exception
    
    # Check that the title is rendered correctly
    assert "Document Ingestion" in at.header[0].value
    
    # Check that the file uploader is present
    assert "Upload documents" in at.file_uploader[0].label
    
    # Check that the text input for collection name is present
    assert "Collection Name" in at.text_input[0].label
    
    # Check that the ChromaDB directory input is present
    assert "ChromaDB Directory" in at.text_input[1].label


@pytest.mark.skip(reason="Streamlit UI tests are challenging to run in a test environment without a ScriptRunContext")
@patch("research_agent.ui.streamlit.document_ingestion.asyncio.run")
@patch("research_agent.ui.streamlit.document_ingestion.os.makedirs")
def test_render_document_ingestion_ui_with_files(mock_makedirs, mock_asyncio_run):
    """Test the document ingestion UI with file uploads."""
    # Configure mocks
    mock_asyncio_run.return_value = {
        "success": True,
        "state": {
            "documents_count": 2,
            "collection_name": "test_collection",
            "total_time": 1.5
        },
        "result": {
            "ids": ["doc1", "doc2"]
        }
    }
    
    # Create a test app instance
    app_script = """
import streamlit as st
from research_agent.ui.streamlit.document_ingestion import render_document_ingestion_ui

render_document_ingestion_ui()
"""
    at = AppTest.from_string(app_script)
    
    # Run the app initially
    at.run()
    
    # Simulate file upload (note: this doesn't actually upload files in the test,
    # but mocks the process)
    uploaded_files = [MagicMock(), MagicMock()]
    at.file_uploader[0].set_value(uploaded_files).run()
    
    # Enter a collection name
    at.text_input[0].input("test_collection").run()
    
    # Check that an ingest button appears
    assert "Ingest Documents" in at.button[0].label
    
    # Click the ingest button
    at.button[0].click().run()
    
    # Verify our mocks were called
    mock_asyncio_run.assert_called_once()
    mock_makedirs.assert_called_once_with("./chroma_db", exist_ok=True)
    
    # Check that success message is displayed
    assert "Successfully ingested" in at.success[0].value 