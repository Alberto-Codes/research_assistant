"""
Tests for the RAG nodes module.

This module tests the functionality of the RAG graph nodes:
- QueryNode
- RetrieveNode
- AnswerNode
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic_graph import Edge, End, GraphRunContext

from research_agent.core.rag.dependencies import RAGDependencies
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


@pytest.fixture
def mock_empty_collection():
    """Mock ChromaDB collection that returns no results."""
    collection = MagicMock()
    collection.query = AsyncMock(
        return_value={
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "ids": [[]],
        }
    )
    return collection


@pytest.fixture
def mock_failing_collection():
    """Mock ChromaDB collection that raises an exception."""
    collection = MagicMock()
    collection.query = AsyncMock(side_effect=Exception("ChromaDB query failed"))
    return collection


@pytest.fixture
def mock_failing_model():
    """Mock Gemini model that raises an exception."""
    model = MagicMock()
    model.generate = AsyncMock(side_effect=Exception("Gemini model generation failed"))
    return model


@pytest.fixture
def query_context(mock_chroma_collection, mock_gemini_model):
    """Create a context for testing QueryNode."""
    state = RAGState(query="How does ChromaDB work?")
    deps = RAGDependencies(chroma_collection=mock_chroma_collection, gemini_model=mock_gemini_model)
    return GraphRunContext(state=state, deps=deps)


@pytest.fixture
def retrieve_context(mock_chroma_collection, mock_gemini_model):
    """Create a context for testing RetrieveNode."""
    state = RAGState(query="How does ChromaDB work?")
    deps = RAGDependencies(chroma_collection=mock_chroma_collection, gemini_model=mock_gemini_model)
    return GraphRunContext(state=state, deps=deps)


@pytest.fixture
def empty_retrieve_context(mock_empty_collection, mock_gemini_model):
    """Create a context for testing RetrieveNode with empty results."""
    state = RAGState(query="How does ChromaDB work?")
    deps = RAGDependencies(chroma_collection=mock_empty_collection, gemini_model=mock_gemini_model)
    return GraphRunContext(state=state, deps=deps)


@pytest.fixture
def failing_retrieve_context(mock_failing_collection, mock_gemini_model):
    """Create a context for testing RetrieveNode with a failing collection."""
    state = RAGState(query="How does ChromaDB work?")
    deps = RAGDependencies(
        chroma_collection=mock_failing_collection, gemini_model=mock_gemini_model
    )
    return GraphRunContext(state=state, deps=deps)


@pytest.fixture
def answer_context(mock_chroma_collection, mock_gemini_model):
    """Create a context for testing AnswerNode."""
    state = RAGState(query="How does ChromaDB work?")
    state.retrieved_documents = [
        {"content": "Document 1 content", "metadata": {"source": "doc1.md"}},
        {"content": "Document 2 content", "metadata": {"source": "doc2.md"}},
    ]
    state.sources = ["doc1.md", "doc2.md"]

    deps = RAGDependencies(chroma_collection=mock_chroma_collection, gemini_model=mock_gemini_model)

    return GraphRunContext(state=state, deps=deps)


@pytest.fixture
def empty_answer_context(mock_chroma_collection, mock_gemini_model):
    """Create a context for testing AnswerNode with no retrieved documents."""
    state = RAGState(query="How does ChromaDB work?")
    state.retrieved_documents = []
    state.sources = []

    # Create a special mock for the empty document case
    empty_model = MagicMock()
    empty_model.generate = AsyncMock(
        return_value=MagicMock(text="I don't have enough information to answer this question.")
    )

    deps = RAGDependencies(chroma_collection=mock_chroma_collection, gemini_model=empty_model)

    return GraphRunContext(state=state, deps=deps)


@pytest.fixture
def failing_answer_context(mock_chroma_collection, mock_failing_model):
    """Create a context for testing AnswerNode with a failing model."""
    state = RAGState(query="How does ChromaDB work?")
    state.retrieved_documents = [
        {"content": "Document 1 content", "metadata": {"source": "doc1.md"}},
        {"content": "Document 2 content", "metadata": {"source": "doc2.md"}},
    ]
    state.sources = ["doc1.md", "doc2.md"]

    deps = RAGDependencies(
        chroma_collection=mock_chroma_collection, gemini_model=mock_failing_model
    )

    return GraphRunContext(state=state, deps=deps)


@pytest.mark.asyncio
async def test_query_node_run(query_context):
    """Test that QueryNode initializes timing and returns RetrieveNode."""
    # Arrange
    node = QueryNode()

    # Act
    with patch("time.time", return_value=12345.0):
        result = await node.run(query_context)

    # Assert
    assert isinstance(result, RetrieveNode)
    assert query_context.state.total_time == 12345.0


@pytest.mark.asyncio
async def test_retrieve_node_success(retrieve_context):
    """Test that RetrieveNode successfully retrieves documents."""
    # Arrange
    node = RetrieveNode()

    # Act
    with patch("time.time", side_effect=[1000.0, 1002.0]):
        result = await node.run(retrieve_context)

    # Assert
    assert isinstance(result, AnswerNode)
    assert len(retrieve_context.state.retrieved_documents) == 2
    assert retrieve_context.state.sources == ["doc1.md", "doc2.md"]
    assert retrieve_context.state.retrieval_time == 2.0  # 1002 - 1000

    # Verify the collection was queried with the right parameters
    retrieve_context.deps.chroma_collection.query.assert_awaited_once_with(
        query_texts=["How does ChromaDB work?"], n_results=5
    )


@pytest.mark.asyncio
async def test_retrieve_node_empty_results(empty_retrieve_context):
    """Test that RetrieveNode handles empty results gracefully."""
    # Arrange
    node = RetrieveNode()

    # Act
    result = await node.run(empty_retrieve_context)

    # Assert
    assert isinstance(result, AnswerNode)
    assert empty_retrieve_context.state.retrieved_documents == []
    assert empty_retrieve_context.state.sources == []


@pytest.mark.asyncio
async def test_retrieve_node_failure(failing_retrieve_context):
    """Test that RetrieveNode handles exceptions gracefully."""
    # Arrange
    node = RetrieveNode()

    # Act
    result = await node.run(failing_retrieve_context)

    # Assert
    assert isinstance(result, AnswerNode)
    assert failing_retrieve_context.state.retrieved_documents == []
    assert failing_retrieve_context.state.sources == []


@pytest.mark.asyncio
async def test_answer_node_success(answer_context):
    """Test that AnswerNode successfully generates an answer."""
    # Arrange
    node = AnswerNode()

    # Set the initial total_time for the delta calculation
    with patch("time.time", return_value=1000.0):
        answer_context.state.total_time = time.time()

    # Act - mock three time.time() calls: generation_start, generation_end, and total_time calculation
    with patch("time.time", side_effect=[1010.0, 1013.0, 1015.0]):
        result = await node.run(answer_context)

    # Assert
    assert isinstance(result, End)
    assert answer_context.state.answer == "Generated answer based on the documents."
    assert answer_context.state.generation_time == 3.0  # 1013 - 1010
    assert answer_context.state.total_time == 15.0  # 1015 - 1000

    # Check that the result includes sources in the data attribute
    assert "Sources: doc1.md, doc2.md" in result.data

    # Verify the model was called with the expected prompt
    prompt_arg = answer_context.deps.gemini_model.generate.call_args[0][0]
    assert "CONTEXT:" in prompt_arg
    assert "Document 1 (from doc1.md)" in prompt_arg
    assert "Document 2 (from doc2.md)" in prompt_arg
    # Use a more flexible assertion that ignores whitespace
    assert "QUESTION:" in prompt_arg
    assert "How does ChromaDB work?" in prompt_arg


@pytest.mark.asyncio
async def test_answer_node_no_documents(empty_answer_context):
    """Test that AnswerNode handles no retrieved documents gracefully."""
    # Arrange
    node = AnswerNode()

    # Set the initial total_time
    empty_answer_context.state.total_time = time.time()

    # Act
    result = await node.run(empty_answer_context)

    # Assert
    assert isinstance(result, End)
    assert "I don't have enough information" in empty_answer_context.state.answer

    # Verify the model was called with the expected prompt
    prompt_arg = empty_answer_context.deps.gemini_model.generate.call_args[0][0]
    assert "CONTEXT:" in prompt_arg
    assert "No relevant documents found." in prompt_arg


@pytest.mark.asyncio
async def test_answer_node_failure(failing_answer_context):
    """Test that AnswerNode handles model generation failures gracefully."""
    # Arrange
    node = AnswerNode()

    # Set the initial total_time
    failing_answer_context.state.total_time = time.time()

    # Act
    result = await node.run(failing_answer_context)

    # Assert
    assert isinstance(result, End)
    assert "I'm sorry, I encountered an error" in failing_answer_context.state.answer
    assert "Sources: doc1.md, doc2.md" in result.data


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
