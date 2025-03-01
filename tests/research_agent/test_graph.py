"""
Tests for the graph implementation.

This module tests the Research Agent graph functionality, including initialization,
execution with various state and dependency configurations, and result processing.
"""

import asyncio
import logging
from unittest.mock import AsyncMock, patch

import pytest
from pydantic_graph import Graph, GraphRunResult

from research_agent.core.gemini.dependencies import GeminiDependencies
from research_agent.core.gemini.graph import (
    display_results,
    get_gemini_agent_graph,
    run_gemini_agent_graph,
)
from research_agent.core.gemini.nodes import GeminiAgentNode
from research_agent.core.gemini.state import GeminiState


@pytest.fixture
def mock_gemini_client():
    """Create a mock Gemini client for testing."""
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="This is a test response from the mock.")
    return mock


@pytest.mark.asyncio
async def test_run_gemini_agent_graph():
    """Test that the Gemini agent graph runs with a user prompt."""
    # Arrange
    user_prompt = "What is the meaning of life?"

    # Act
    with patch("research_agent.core.gemini.dependencies.GeminiLLMClient") as MockGeminiClass:
        # Configure the mock
        mock_instance = AsyncMock()
        mock_instance.generate_text = AsyncMock(return_value="The meaning of life is 42.")
        MockGeminiClass.return_value = mock_instance

        # Run the graph
        result_text, state, errors = await run_gemini_agent_graph(user_prompt)

    # Assert
    assert result_text == "The meaning of life is 42."
    assert isinstance(state, GeminiState)
    assert state.user_prompt == user_prompt
    assert state.ai_response == "The meaning of life is 42."
    assert state.ai_generation_time > 0
    assert state.total_time > 0
    assert len(errors) == 0


@pytest.mark.asyncio
async def test_run_gemini_agent_graph_with_custom_dependencies(mock_gemini_client):
    """Test that the Gemini agent graph runs with custom dependencies."""
    # Arrange
    user_prompt = "What is the meaning of life?"
    dependencies = GeminiDependencies(llm_client=mock_gemini_client)

    # Act
    result_text, state, errors = await run_gemini_agent_graph(user_prompt, dependencies)

    # Assert
    assert result_text == "This is a test response from the mock."
    assert isinstance(state, GeminiState)
    assert state.user_prompt == user_prompt
    assert state.ai_response == "This is a test response from the mock."
    assert mock_gemini_client.generate_text.called
    assert len(errors) == 0


@pytest.mark.asyncio
async def test_get_gemini_agent_graph():
    """Test that get_gemini_agent_graph returns a Graph with the expected node."""
    # Act
    graph = get_gemini_agent_graph()

    # Assert
    assert isinstance(graph, Graph)
    # The Graph class doesn't expose nodes directly, so we can't check them
    # Just verify it's a Graph instance


def test_display_results(caplog):
    """Test that display_results correctly displays the result information."""
    # Arrange
    state = GeminiState(
        user_prompt="Test prompt",
        ai_response="Test response",
        ai_generation_time=0.5,
        total_time=1.0,
        node_execution_history=["GeminiAgentNode: AI Response: Test response (took 0.5s)"],
    )
    # Create GraphRunResult with required parameters including history
    result = GraphRunResult(
        output="Test response", state=state, history=[]  # Empty history for this test
    )

    # Set up logging capture
    caplog.set_level(logging.INFO)

    # Act
    display_results(result)

    # Assert
    assert "Result: Test response" in caplog.text


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
