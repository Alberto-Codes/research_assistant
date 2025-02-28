"""
Test the nodes using pytest fixtures for mocking.

This module demonstrates the recommended way to test nodes
with proper pytest fixtures instead of using the deprecated
MockGeminiLLMClient class.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from pydantic_graph import End
from pydantic_graph.nodes import GraphRunContext

from research_agent.core.dependencies import HelloWorldDependencies, LLMClient
from research_agent.core.nodes import GeminiAgentNode
from research_agent.core.state import MyState


@pytest.fixture
def mock_gemini_for_node():
    """Create a mock Gemini client for testing nodes."""
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="This is a mocked response for the node test.")
    return mock


@pytest.fixture
def state_with_prompt():
    """Create a state with a user prompt for testing."""
    state = MyState()
    state.user_prompt = "Test prompt for Gemini"
    # Initialize the execution history to avoid None errors
    state.node_execution_history = []
    return state


@pytest.mark.asyncio
async def test_gemini_agent_node_with_mock(mock_gemini_for_node, state_with_prompt):
    """Test the GeminiAgentNode with a mock client.

    This test demonstrates the proper way to test a node that depends
    on an external service (Gemini) without using the deprecated
    MockGeminiLLMClient class.
    """
    # Create dependencies with our mock
    deps = HelloWorldDependencies()
    deps.llm_client = mock_gemini_for_node  # Inject our mock client

    # Create the node and context
    node = GeminiAgentNode()
    ctx = GraphRunContext(state=state_with_prompt, deps=deps)

    # Run the node
    result = await node.run(ctx)

    # Verify the mock was called with the correct prompt
    mock_gemini_for_node.generate_text.assert_called_once_with("Test prompt for Gemini")

    # Verify the state was updated correctly
    assert ctx.state.ai_response == "This is a mocked response for the node test."
    assert hasattr(ctx.state, "ai_generation_time")

    # Verify execution history was recorded
    assert len(ctx.state.node_execution_history) > 0
    assert any("GeminiAgentNode" in entry for entry in ctx.state.node_execution_history)

    # Verify the node returned an End instance with the right data
    assert isinstance(result, End)
    assert result.data == "This is a mocked response for the node test."


class MockLLM(LLMClient):
    """A proper mock implementation of the LLMClient protocol for testing."""

    def __init__(self, response="This is a patched response."):
        self.response = response
        self.calls = []

    async def generate_text(self, prompt: str) -> str:
        """Record the call and return a predefined response."""
        self.calls.append(prompt)
        return self.response


@pytest.mark.asyncio
async def test_gemini_agent_node_with_manual_mock(state_with_prompt):
    """Test the GeminiAgentNode using a manual mock implementation.

    This test demonstrates using a class that implements the LLMClient protocol
    for testing, which can be more maintainable than using unittest.mock.
    """
    # Create a mock client
    mock_llm = MockLLM()

    # Create dependencies with our mock
    deps = HelloWorldDependencies()
    deps.llm_client = mock_llm

    # Create the node and context
    node = GeminiAgentNode()
    ctx = GraphRunContext(state=state_with_prompt, deps=deps)

    # Run the node
    result = await node.run(ctx)

    # Verify the mock was called with the correct prompt
    assert len(mock_llm.calls) == 1
    assert mock_llm.calls[0] == "Test prompt for Gemini"

    # Verify the state was updated correctly
    assert ctx.state.ai_response == "This is a patched response."

    # Verify the result
    assert isinstance(result, End)
    assert result.data == "This is a patched response."


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
