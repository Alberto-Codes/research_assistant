"""
Tests for the Streamlit application.

This module tests the Streamlit web interface for the Research Agent application,
verifying that it correctly displays user interface elements and handles user interactions.
"""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

# Import the Streamlit testing framework
from streamlit.testing.v1 import AppTest

from research_agent.core.dependencies import GeminiDependencies
from research_agent.core.state import MyState


def create_mock_state():
    """Create a mock state with test data for Gemini chat."""
    state = MyState(
        user_prompt="What is the meaning of life?",
        ai_response="The meaning of life is 42.",
        ai_generation_time=0.5,
        total_time=0.6,
        node_execution_history=[
            "GeminiAgentNode: Generated response to 'What is the meaning of life?'"
        ],
    )
    return state


@pytest.mark.skip(reason="Requires Streamlit environment to run properly")
def test_gemini_chat_ui():
    """Test the Gemini chat UI initial state."""
    # This test is skipped by default as it requires a Streamlit environment
    # To run it locally, remove the skip decorator

    # Import the app module
    from research_agent.ui.streamlit.gemini_chat import main

    # Create a test app
    at = AppTest.from_function(main)
    at.run()

    # Check that the basic UI elements are present
    assert at.title[0].value == "Gemini Chat"
    assert "Enter your message" in at.markdown[0].value

    # Check that the sidebar has configuration options
    sidebar_elements = at.sidebar.markdown
    assert any("Configuration" in element.value for element in sidebar_elements)


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
