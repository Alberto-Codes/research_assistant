"""
Tests for the graph implementation.

This module tests the Research Agent graph functionality, including initialization,
execution with various state and dependency configurations, and result processing.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from research_agent.core.dependencies import GeminiDependencies
from research_agent.core.graph import (
    display_results,
    get_gemini_agent_graph,
    run_gemini_agent_graph,
)
from research_agent.core.state import MyState


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
    with patch("research_agent.core.dependencies.GeminiLLMClient") as MockGeminiClass:
        # Configure the mock
        mock_instance = AsyncMock()
        mock_instance.generate_text = AsyncMock(return_value="The meaning of life is 42.")
        MockGeminiClass.return_value = mock_instance

        # Run the graph
        result_text, state, errors = await run_gemini_agent_graph(user_prompt)

    # Assert
    assert result_text == "The meaning of life is 42."
    assert isinstance(state, MyState)
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
    assert isinstance(state, MyState)
    assert state.user_prompt == user_prompt
    assert state.ai_response == "This is a test response from the mock."
    assert mock_gemini_client.generate_text.called
    assert len(errors) == 0


@pytest.mark.asyncio
async def test_get_gemini_agent_graph():
    """Test that the Gemini agent graph is created correctly."""
    # Act
    graph = get_gemini_agent_graph()

    # Assert
    assert graph is not None
    assert hasattr(graph, "run")


class MockGraphRunResult:
    """Mock GraphRunResult for testing display_results."""

    def __init__(self, value, state):
        """Initialize with output and state."""
        self.output = value
        self.state = state


def test_display_results(capsys):
    """Test that display_results outputs the expected information."""
    # Arrange
    state = MyState(
        user_prompt="Test prompt",
        ai_response="Test response",
        ai_generation_time=0.5,
        total_time=1.0,
        node_execution_history=["GeminiAgentNode: Generated response to 'Test prompt'"],
    )
    result = MockGraphRunResult("Test response", state)

    # Act
    display_results(result)

    # Assert
    captured = capsys.readouterr()
    assert "Result: Test response" in captured.out
    assert "State: " in captured.out
    assert "Execution History:" in captured.out
    assert "GeminiAgentNode: Generated response to 'Test prompt'" in captured.out
    assert "Total execution time: 1.000 seconds" in captured.out


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
