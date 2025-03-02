"""
Tests for the RAG search UI components.
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock

import chromadb
import streamlit as st
from streamlit.testing.v1 import AppTest

from research_agent.ui.streamlit.rag_search import (
    list_collections,
    execute_rag_query,
    render_rag_search_ui
)


@patch("chromadb.PersistentClient")
def test_list_collections_success(mock_client):
    """Test successful listing of collections."""
    # Mock the client's list_collections method
    mock_instance = mock_client.return_value
    mock_instance.list_collections.return_value = ["collection1", "collection2"]

    # Call the function
    result = list_collections("./test_chroma_db")

    # Assert results
    assert result == ["collection1", "collection2"]
    mock_client.assert_called_once_with(path="./test_chroma_db")
    mock_instance.list_collections.assert_called_once()


@patch("chromadb.PersistentClient")
def test_list_collections_exception(mock_client):
    """Test handling of exceptions when listing collections."""
    # Mock the client to raise an exception
    mock_instance = mock_client.return_value
    mock_instance.list_collections.side_effect = Exception("Test error")

    # Call the function
    result = list_collections("./test_chroma_db")

    # Assert results
    assert result == []
    mock_client.assert_called_once_with(path="./test_chroma_db")
    mock_instance.list_collections.assert_called_once()


@pytest.mark.asyncio
@patch("research_agent.ui.streamlit.rag_search.run_rag_query")
@patch("research_agent.ui.streamlit.rag_search.VertexAIModel")
@patch("research_agent.ui.streamlit.rag_search.Agent")
@patch("chromadb.PersistentClient")
async def test_execute_rag_query_success(mock_client, mock_agent, mock_vertex, mock_run_query):
    """Test successful execution of RAG query."""
    # Set up our mocks
    mock_instance = mock_client.return_value
    mock_collection = MagicMock()
    mock_instance.get_collection.return_value = mock_collection
    mock_collection.count.return_value = 5
    
    mock_vertex_instance = mock_vertex.return_value
    mock_agent_instance = mock_agent.return_value
    
    # Set up the mock for run_rag_query
    expected_result = {
        "answer": "Test answer",
        "retrieval_time": 0.5,
        "generation_time": 1.0,
        "total_time": 1.5
    }
    mock_run_query.return_value = expected_result
    
    # Execute the function
    result = await execute_rag_query(
        query="test query",
        collection_name="test_collection",
        chroma_dir="./test_chroma_db",
        project_id="test-project",
        model_name="gemini-1.5-pro",
        region="us-central1"
    )
    
    # Assert results
    assert result == expected_result
    mock_client.assert_called_once_with(path="./test_chroma_db")
    mock_instance.get_collection.assert_called_once_with("test_collection")
    mock_vertex.assert_called_once_with(
        model_name="gemini-1.5-pro", 
        project_id="test-project", 
        region="us-central1"
    )
    mock_agent.assert_called_once_with(mock_vertex_instance)
    mock_run_query.assert_called_once_with(
        query="test query",
        chroma_collection=mock_collection,
        gemini_model=mock_agent_instance,
        project_id="test-project"
    )


@pytest.mark.asyncio
@patch("research_agent.ui.streamlit.rag_search.run_rag_query")
@patch("chromadb.PersistentClient")
async def test_execute_rag_query_exception(mock_client, mock_run_query):
    """Test handling of exceptions when executing RAG query."""
    # Mock the client to raise an exception
    mock_instance = mock_client.return_value
    mock_instance.get_collection.side_effect = Exception("Test error")
    
    # Execute the function
    result = await execute_rag_query(
        query="test query",
        collection_name="test_collection"
    )
    
    # Assert results
    assert "Error" in result["answer"]
    assert result["retrieval_time"] == 0
    assert result["generation_time"] == 0
    assert result["total_time"] == 0


@patch("research_agent.ui.streamlit.rag_search.list_collections")
def test_render_rag_search_ui_basic(mock_list_collections):
    """Test the basic rendering of the RAG search UI."""
    # Mock the list_collections function to return test data
    mock_list_collections.return_value = ["test_collection", "sample_collection"]
    
    # Create a test app instance with the render function
    app_script = """
import streamlit as st
from research_agent.ui.streamlit.rag_search import render_rag_search_ui

render_rag_search_ui()
"""
    at = AppTest.from_string(app_script)
    
    # Run the app and check if it rendered correctly
    at.run()
    
    # Verify no exceptions occurred
    assert not at.exception
    
    # Check that the title is rendered correctly
    assert "Document Search with RAG" in at.title[0].value
    
    # Check that the selectbox for collections is present with our mock collections
    assert "test_collection" in at.selectbox[0].options
    assert "sample_collection" in at.selectbox[0].options
    
    # Check that the text area for entering a query is present
    assert "Enter your question about the documents:" in at.text_area[0].label


@pytest.mark.skip(reason="Streamlit UI tests are challenging to run in a test environment without a ScriptRunContext")
@patch("research_agent.ui.streamlit.rag_search.list_collections")
@patch("research_agent.ui.streamlit.rag_search.asyncio.run")
def test_render_rag_search_ui_with_query(mock_asyncio_run, mock_list_collections):
    """Test the RAG search UI with a query submission."""
    # Mock the list_collections function to return test data
    mock_list_collections.return_value = ["test_collection"]
    
    # Mock the asyncio.run function to return a test result
    mock_asyncio_run.return_value = {
        "answer": "This is a test answer.",
        "retrieval_time": 0.5,
        "generation_time": 1.0,
        "total_time": 1.5
    }
    
    # Create a test app instance
    app_script = """
import streamlit as st
from research_agent.ui.streamlit.rag_search import render_rag_search_ui

render_rag_search_ui()
"""
    at = AppTest.from_string(app_script)
    
    # Run the app initially
    at.run()
    
    # Enter a query in the text area
    at.text_area[0].input("What information is in the documents?")
    at.run()
    
    # Check that a search button appears
    assert at.button[0].label == "Search Documents"
    
    # Click the search button to simulate a search
    at.button[0].click().run()
    
    # Check that the answer is displayed
    assert "This is a test answer." in at.markdown[1].value
    
    # Check that the metrics are displayed
    assert "Retrieval Time" in at.metric[0].label
    assert "Generation Time" in at.metric[1].label
    assert "Total Time" in at.metric[2].label 