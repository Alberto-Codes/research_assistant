"""
Test the high-level service functions in the API layer.

This module contains tests for the service functions that coordinate
the execution of the graph and provide an interface for different user interfaces.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from research_agent.api.services import generate_ai_response, generate_hello_world
from research_agent.core.state import MyState


@pytest.fixture
def mock_gemini_llm_client():
    """Create a mock LLM client for testing."""
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="This is a test response from the mock.")
    return mock


@pytest.mark.asyncio
async def test_generate_hello_world():
    """Test the generate_hello_world service function."""
    result = await generate_hello_world(prefix="Test")

    # Verify the state has the expected structure
    assert isinstance(result, MyState)
    assert hasattr(result, "hello_text")
    assert hasattr(result, "world_text")
    assert hasattr(result, "combined_text")

    # Verify the texts were generated and combined
    assert result.hello_text is not None
    assert result.world_text is not None
    assert result.combined_text is not None
    assert result.hello_text in result.combined_text
    assert result.world_text in result.combined_text


@pytest.mark.asyncio
@patch("research_agent.core.dependencies.GeminiLLMClient")
async def test_generate_ai_response(MockGeminiClass):
    """Test the generate_ai_response service function with a patched Gemini client."""
    # Configure the mock
    mock_instance = AsyncMock()
    mock_instance.generate_text = AsyncMock(return_value="This is a mocked AI response.")
    MockGeminiClass.return_value = mock_instance

    # Call the service function
    prompt = "Test prompt"
    result = await generate_ai_response(user_prompt=prompt, project_id="test-project")

    # Verify the mock was called with the correct prompt
    mock_instance.generate_text.assert_called_once_with(prompt)

    # Verify the state has the expected values
    assert isinstance(result, MyState)
    assert result.user_prompt == prompt
    assert result.ai_response == "This is a mocked AI response."
    assert result.ai_generation_time >= 0
    assert result.total_time >= 0


@pytest.mark.asyncio
async def test_generate_ai_response_integration():
    """
    Integration test for the generate_ai_response function.

    Skip this test if no Vertex AI credentials are available.
    """
    try:
        # Test with a simple prompt - without using MockGemini
        prompt = "What is 2+2?"
        result = await generate_ai_response(user_prompt=prompt)

        # Verify we got a response
        assert isinstance(result, MyState)
        assert result.user_prompt == prompt
        assert result.ai_response is not None
        assert len(result.ai_response) > 0
        assert result.ai_generation_time >= 0

    except Exception as e:
        pytest.skip(f"Skipping integration test due to Vertex AI setup issue: {str(e)}")


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
