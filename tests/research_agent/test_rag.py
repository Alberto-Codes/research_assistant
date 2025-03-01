"""
Tests for the RAG module.

This module tests the functionality of the RAG state and dependencies classes.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from research_agent.core.rag.dependencies import RAGDependencies
from research_agent.core.rag.state import RAGState


@pytest.fixture
def mock_chroma_collection():
    """Provide a mock ChromaDB collection for testing.

    Returns:
        A mock ChromaDB collection instance.
    """
    collection = MagicMock()
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
    """Provide a mock Gemini model for testing.

    Returns:
        A mock Gemini model instance.
    """
    model = MagicMock()
    model.generate = AsyncMock(return_value=MagicMock(text="Model generated response"))
    return model


def test_rag_state_initialization():
    """Test that RAGState can be properly initialized with a query."""
    # Arrange & Act
    state = RAGState(query="How does ChromaDB work?")

    # Assert
    assert state.query == "How does ChromaDB work?"
    assert state.retrieved_documents == []
    assert state.answer is None
    assert state.sources == []
    assert state.generation_time == 0.0
    assert state.retrieval_time == 0.0
    assert state.total_time == 0.0


def test_rag_state_document_addition():
    """Test that documents can be added to RAGState."""
    # Arrange
    state = RAGState(query="Test query")
    test_doc = {"content": "Test content", "metadata": {"source": "test.md"}}

    # Act
    state.retrieved_documents.append(test_doc)
    state.sources.append("test.md")

    # Assert
    assert len(state.retrieved_documents) == 1
    assert state.retrieved_documents[0]["content"] == "Test content"
    assert state.sources[0] == "test.md"


def test_rag_state_repr():
    """Test that RAGState.__repr__ works correctly."""
    # Arrange
    state = RAGState(query="Test query")
    state.answer = "This is the answer"
    state.retrieval_time = 1.123
    state.generation_time = 2.456
    state.total_time = 3.789

    # Act
    repr_str = repr(state)

    # Assert
    assert "query='Test query'" in repr_str
    assert "num_docs=0" in repr_str
    assert "answer_length=18" in repr_str
    assert "retrieval_time=1.123s" in repr_str
    assert "generation_time=2.456s" in repr_str
    assert "total_time=3.789s" in repr_str


def test_rag_dependencies_initialization(mock_chroma_collection, mock_gemini_model):
    """Test that RAGDependencies can be properly initialized with dependencies."""
    # Arrange
    project_id = "test-project"

    # Act
    deps = RAGDependencies(
        chroma_collection=mock_chroma_collection,
        gemini_model=mock_gemini_model,
        project_id=project_id,
    )

    # Assert
    assert deps.chroma_collection is mock_chroma_collection
    assert deps.gemini_model is mock_gemini_model
    assert deps.project_id == "test-project"


def test_rag_dependencies_no_project_id(mock_chroma_collection, mock_gemini_model):
    """Test that RAGDependencies works without a project_id."""
    # Arrange & Act
    deps = RAGDependencies(chroma_collection=mock_chroma_collection, gemini_model=mock_gemini_model)

    # Assert
    assert deps.chroma_collection is mock_chroma_collection
    assert deps.gemini_model is mock_gemini_model
    assert deps.project_id is None


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
