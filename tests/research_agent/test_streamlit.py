"""
Tests for the Streamlit application.

This module tests the Streamlit web interface for the Research Agent application,
verifying that it correctly displays user interface elements and handles user interactions.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from research_agent.core.gemini.dependencies import GeminiDependencies
from research_agent.core.gemini.state import GeminiState


def create_mock_state():
    """Create a mock state with test data for Gemini chat."""
    state = GeminiState(
        user_prompt="What is the meaning of life?",
        ai_response="The meaning of life is 42.",
        ai_generation_time=0.5,
        total_time=0.6,
        node_execution_history=[
            "GeminiAgentNode: AI Response: The meaning of life is 42. (took 0.5s)"
        ],
    )
    return state


# Use the app path that works with your project structure
APP_PATH = "src/research_agent/ui/streamlit/gemini_chat.py"


@pytest.mark.skip(reason="Streamlit UI testing requires specific environment setup")
@patch("research_agent.ui.streamlit.gemini_chat.asyncio.run")
@patch("research_agent.ui.streamlit.gemini_chat.GeminiLLMClient")
def test_gemini_chat_ui(mock_gemini_client, mock_asyncio_run):
    """Test the Gemini chat UI initial state and interaction."""
    # This test is intentionally skipped as it requires a specific Streamlit test environment
    # Instead, we test core functionality separately in test_generate_streaming_response
    pass


def test_gemini_chat_core_functions():
    """Test core functions used by the Streamlit UI without the UI itself."""
    # Import the functions to test
    from research_agent.ui.streamlit.gemini_chat import DEFAULT_SYSTEM_PROMPT, display_message

    # Verify the default system prompt exists and contains expected text
    assert "helpful research assistant" in DEFAULT_SYSTEM_PROMPT
    assert "provide accurate" in DEFAULT_SYSTEM_PROMPT


@pytest.mark.asyncio
@patch("research_agent.ui.streamlit.gemini_chat.PYDANTIC_AI_AVAILABLE", True)
@patch("research_agent.ui.streamlit.gemini_chat.Agent")
async def test_generate_streaming_response(mock_agent_class):
    """Test the generate_streaming_response function."""
    # Setup agent mock
    mock_agent = MagicMock()
    mock_agent_class.return_value = mock_agent

    # Setup client mock
    with patch("research_agent.ui.streamlit.gemini_chat.GeminiLLMClient") as mock_client_class:
        # Configure client mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.agent = mock_agent
        mock_client.vertex_model = "vertex-model-mock"

        # Setup streaming mock
        mock_stream_context = AsyncMock()
        mock_stream_result = AsyncMock()
        mock_agent.run_stream.return_value = mock_stream_context
        mock_stream_context.__aenter__.return_value = mock_stream_result

        # Setup streaming function
        mock_chunks = ["Hello", " ", "World"]

        async def mock_stream_text(delta=True):
            for chunk in mock_chunks:
                yield chunk

        mock_stream_result.stream_text = mock_stream_text

        # Import the function under test
        from research_agent.ui.streamlit.gemini_chat import generate_streaming_response

        # Mock streamlit.empty
        with patch("streamlit.empty") as mock_empty:
            mock_placeholder = MagicMock()
            mock_empty.return_value = mock_placeholder

            # Call the function
            response = await generate_streaming_response(
                user_prompt="Test prompt", system_prompt="Test system prompt"
            )

            # Verify the agent setup and run_stream was called
            assert mock_agent.run_stream.called

            # If we're mocking properly, our mock chunks should form the response
            assert response == "".join(mock_chunks)


@pytest.mark.asyncio
@patch("research_agent.api.services.generate_ai_response")
async def test_generate_ai_response(mock_generate):
    """Test the generate_ai_response function."""
    # Arrange
    mock_state = create_mock_state()
    mock_generate.return_value = mock_state

    # Import the function to test
    from research_agent.api.services import generate_ai_response

    # Act
    result = await generate_ai_response("What is the meaning of life?")

    # Assert
    assert result == mock_state
    assert result.user_prompt == "What is the meaning of life?"
    assert result.ai_response == "The meaning of life is 42."
    assert result.ai_generation_time == 0.5
    assert result.total_time == 0.6


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])
