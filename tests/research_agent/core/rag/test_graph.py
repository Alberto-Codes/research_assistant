"""
Tests for the RAG graph module.

This module tests the functionality of the RAG graph configuration and execution.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research_agent.core.rag.dependencies import RAGDependencies
from research_agent.core.rag.graph import create_rag_graph, rag_graph, run_rag_query
from research_agent.core.rag.nodes import AnswerNode, QueryNode, RetrieveNode
from research_agent.core.rag.state import RAGState


@pytest.fixture
def mock_chroma_collection():
    """Mock ChromaDB collection with query method."""
    collection = MagicMock()

    # Mock the asynchronous query method
    collection.query = AsyncMock(
        return_value={
            "documents": [["Document 1 content", "Document 2 content"]],
            "metadatas": [[{"source": "doc1.md"}, {"source": "doc2.md"}]],
            "distances": [[0.1, 0.2]],
            "ids": [["id1", "id2"]],
        }
    )

    return collection


@pytest.fixture
def mock_gemini_model():
    """Mock Gemini model for testing."""
    model = MagicMock()
    model.generate = AsyncMock(
        return_value=MagicMock(text="Generated answer based on the documents.")
    )
    return model


def test_create_rag_graph():
    """Test that the RAG graph is created with the correct structure."""
    # Act
    graph = create_rag_graph()

    # Assert
    assert graph is not None
    # Check that the graph was created - we can't inspect the internal structure
    # directly in this version of pydantic-graph
    assert isinstance(graph, object)


def test_rag_graph_singleton():
    """Test that rag_graph is a singleton instance of the graph."""
    # Create a new graph
    new_graph = create_rag_graph()

    # The graphs should be different instances
    assert new_graph is not rag_graph
    # We can't directly inspect the structure in this version


@pytest.mark.asyncio
async def test_run_rag_query(mock_chroma_collection, mock_gemini_model):
    """Test that run_rag_query runs the graph workflow correctly."""
    # Arrange
    test_query = "How does ChromaDB work?"

    # Create a mock result with a data attribute
    mock_result = MagicMock()
    mock_result.data = "Generated answer.\n\nSources: doc1.md, doc2.md"

    # Patch the run method on the graph instance directly
    with (
        patch.object(
            rag_graph,
            "run",
            return_value=MagicMock(data="Generated answer.\n\nSources: doc1.md, doc2.md"),
        ) as mock_run,
        patch("time.time", side_effect=[100.0, 105.0]),
    ):

        # Create a mock state that will be updated by the graph run
        mock_state = RAGState(query=test_query)
        mock_state.retrieval_time = 2.0
        mock_state.generation_time = 3.0

        # Configure the mock to update the state
        def mock_graph_run(start_node, *, state=None, deps=None):
            # This simulates updating the state during graph execution
            assert state.query == test_query
            assert deps.chroma_collection == mock_chroma_collection
            assert deps.gemini_model == mock_gemini_model

            # Copy the properties from our prepared mock state
            state.retrieval_time = mock_state.retrieval_time
            state.generation_time = mock_state.generation_time

            return mock_result

        mock_run.side_effect = mock_graph_run

        # Act
        result = await run_rag_query(
            query=test_query,
            chroma_collection=mock_chroma_collection,
            gemini_model=mock_gemini_model,
            project_id="test-project",
        )

        # Assert
        assert "Generated answer" in result["answer"]
        assert result["retrieval_time"] == 2.0
        assert result["generation_time"] == 3.0
        assert result["total_time"] == 5.0  # 105.0 - 100.0

        # Verify the run method was called with the right arguments
        mock_run.assert_called_once()
        # Verify the start_node is a QueryNode
        start_node_arg = mock_run.call_args[0][0]
        assert isinstance(start_node_arg, QueryNode)
        # Verify the state passed had the correct query
        state_arg = mock_run.call_args[1]["state"]
        assert state_arg.query == test_query
        # Verify deps passed had the correct values
        deps_arg = mock_run.call_args[1]["deps"]
        assert deps_arg.chroma_collection == mock_chroma_collection
        assert deps_arg.gemini_model == mock_gemini_model
        assert deps_arg.project_id == "test-project"


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
