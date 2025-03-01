"""
Test the high-level service functions in the API layer.

This module contains tests for the service functions that coordinate
the execution of the graph and provide an interface for different user interfaces.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from research_agent.api.services import generate_ai_response
from research_agent.core.gemini.state import GeminiState


@pytest.fixture
def mock_gemini_llm_client():
    """Create a mock LLM client for testing."""
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="This is a test response from the mock.")
    return mock


@pytest.mark.asyncio
@patch("research_agent.core.gemini.dependencies.GeminiLLMClient")
async def test_generate_ai_response(mock_gemini_class, mock_gemini_llm_client):
    """Test the generate_ai_response function with a mock LLM client."""
    # Set up mock instance
    mock_gemini_class.return_value = mock_gemini_llm_client
    mock_gemini_llm_client.generate_text.return_value = "This is a test response from the mock."

    # Call the service function
    result = await generate_ai_response("What is the meaning of life?")

    # Verify the mock was called with the correct prompt
    mock_gemini_llm_client.generate_text.assert_called_once_with("What is the meaning of life?")

    # Verify the state has the expected structure
    assert isinstance(result, GeminiState)
    assert result.user_prompt == "What is the meaning of life?"
    assert result.ai_response == "This is a test response from the mock."
    assert result.ai_generation_time > 0


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
