"""
Test the nodes using pytest fixtures for mocking.

This module demonstrates how to test the GeminiAgentNode
with proper pytest fixtures.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from pydantic_graph import End
from pydantic_graph.nodes import GraphRunContext

from research_agent.core.gemini.dependencies import GeminiDependencies, LLMClient
from research_agent.core.gemini.nodes import GeminiAgentNode
from research_agent.core.gemini.state import GeminiState


@pytest.fixture
def mock_gemini_for_node():
    """Create a mock Gemini client for testing nodes."""
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="This is a mocked response for the node test.")
    return mock


@pytest.fixture
def state_with_prompt():
    """Create a state with a user prompt for testing."""
    return GeminiState(user_prompt="What is the meaning of life?")


@pytest.mark.asyncio
async def test_gemini_agent_node_with_mock(mock_gemini_for_node, state_with_prompt):
    """Test the GeminiAgentNode using a mock for the generate_text method."""
    # Create the node
    node = GeminiAgentNode()

    # Create the dependencies with our mock client
    deps = GeminiDependencies(llm_client=mock_gemini_for_node)

    # Create a run context
    ctx = GraphRunContext(state=state_with_prompt, deps=deps)

    # Run the node
    result = await node.run(ctx)

    # Verify the result is an End node
    assert isinstance(result, End)
    assert ctx.state.ai_response == "This is a mocked response for the node test."

    # Verify the AI response was set on the state
    assert ctx.state.ai_response == "This is a mocked response for the node test."

    # Verify the mock was called with the correct prompt
    mock_gemini_for_node.generate_text.assert_called_once_with("What is the meaning of life?")

    # Verify the execution history was updated
    assert len(ctx.state.node_execution_history) == 1
    assert "GeminiAgentNode: AI Response" in ctx.state.node_execution_history[0]

    # Verify the timing was recorded
    assert ctx.state.ai_generation_time > 0
    assert ctx.state.total_time > 0


class MockLLM(LLMClient):
    """A manual implementation of the LLMClient protocol for testing."""

    def __init__(self, response="This is a patched response."):
        """Initialize with an optional custom response."""
        self.response = response

    async def generate_text(self, prompt: str) -> str:
        """Generate text by just returning the preset response."""
        return self.response


@pytest.mark.asyncio
async def test_gemini_agent_node_with_manual_mock(state_with_prompt):
    """Test the GeminiAgentNode using a manually created mock implementation."""
    # Create the node
    node = GeminiAgentNode()

    # Create the dependencies with our manual mock client
    deps = GeminiDependencies(llm_client=MockLLM())

    # Create a run context
    ctx = GraphRunContext(state=state_with_prompt, deps=deps)

    # Run the node
    result = await node.run(ctx)

    # Verify the result is an End node
    assert isinstance(result, End)
    assert ctx.state.ai_response == "This is a patched response."

    # Verify the AI response was set on the state
    assert ctx.state.ai_response == "This is a patched response."


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
