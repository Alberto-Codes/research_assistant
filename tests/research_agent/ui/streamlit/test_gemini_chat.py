"""
Tests for the Gemini chat UI components.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from research_agent.ui.streamlit.gemini_chat import (
    generate_streaming_response,
    display_message,
    main
)


class TestGeminiChat(unittest.TestCase):
    """Tests for the Gemini chat UI components."""

    @pytest.mark.asyncio
    @patch("research_agent.ui.streamlit.gemini_chat.GeminiLLMClient")
    async def test_generate_streaming_response_success(self, mock_client):
        """Test successful generation of a streaming response."""
        # Configure mocks
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Create a mock agent
        mock_agent = MagicMock()
        mock_client_instance.agent = mock_agent
        mock_client_instance.vertex_model = MagicMock()
        
        # Mock the context manager for streaming
        mock_context = AsyncMock()
        mock_agent.run_stream.return_value.__aenter__.return_value = mock_context
        
        # Mock the generator to return chunks
        async def mock_generator():
            yield "This "
            yield "is "
            yield "a "
            yield "test "
            yield "response."
        
        # Set up the mock result to stream text
        mock_context.stream_text.return_value = mock_generator()
        
        # Mock st.empty to get markdown calls
        mock_placeholder = MagicMock()
        st.empty = MagicMock(return_value=mock_placeholder)
        
        # Call the function
        result = await generate_streaming_response(
            user_prompt="What is AI?",
            system_prompt="You are a helpful assistant."
        )
        
        # Assert results
        assert result == "This is a test response."
        mock_client.assert_called_once()
        mock_agent.run_stream.assert_called_once()
        mock_context.stream_text.assert_called_once_with(delta=True)
        
        # Check that the placeholder was updated with each chunk
        assert mock_placeholder.markdown.call_count >= 5  # At least once per chunk
        
        # Explicitly return None to avoid deprecation warning
        return None

    @pytest.mark.asyncio
    @patch("research_agent.ui.streamlit.gemini_chat.GeminiLLMClient")
    async def test_generate_streaming_response_exception(self, mock_client):
        """Test handling of exceptions when generating a streaming response."""
        # Configure mocks
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Create a mock agent that raises an exception
        mock_agent = MagicMock()
        mock_client_instance.agent = mock_agent
        mock_client_instance.vertex_model = MagicMock()
        
        # Make the agent's run_stream raise an exception
        mock_agent.run_stream.side_effect = Exception("API error")
        
        # Mock st.empty to get markdown calls
        mock_placeholder = MagicMock()
        st.empty = MagicMock(return_value=mock_placeholder)
        
        # Call the function
        result = await generate_streaming_response(
            user_prompt="What is AI?"
        )
        
        # Assert results
        assert "Error in streaming" in result
        assert "API error" in result
        mock_client.assert_called_once()
        mock_agent.run_stream.assert_called_once()
        
        # Explicitly return None to avoid deprecation warning
        return None

    @pytest.mark.skip(reason="Streamlit UI tests are challenging to run in a test environment without a ScriptRunContext")
    def test_display_message(self):
        """Test the display_message function."""
        # Mock the st.chat_message context manager
        mock_chat_message = MagicMock()
        mock_markdown = MagicMock()
        
        # Create a context manager effect
        mock_chat_message.__enter__.return_value = mock_markdown
        
        # Mock the streamlit functions
        st.chat_message = MagicMock(return_value=mock_chat_message)
        
        # Call the function
        display_message("user", "Hello, world!", avatar="👤")
        
        # Check the calls
        st.chat_message.assert_called_once_with("user", avatar="👤")
        mock_markdown.markdown.assert_called_once_with("Hello, world!")

    @pytest.mark.skip(reason="Streamlit UI tests are challenging to run in a test environment without a ScriptRunContext")
    @patch("research_agent.ui.streamlit.gemini_chat.st.title")
    @patch("research_agent.ui.streamlit.gemini_chat.st.markdown")
    @patch("research_agent.ui.streamlit.gemini_chat.st.chat_input")
    @patch("research_agent.ui.streamlit.gemini_chat.st.sidebar")
    @patch("research_agent.ui.streamlit.gemini_chat.st.expander")
    def test_main_basic_rendering(self, mock_expander, mock_sidebar, mock_chat_input, mock_markdown, mock_title):
        """Test the basic rendering of the main function."""
        # Set up session state
        if not hasattr(st, "session_state"):
            class SessionState:
                pass
            st.session_state = SessionState()
        
        # Set session state values
        st.session_state.chat_history = []
        st.session_state.system_prompt = "You are a helpful assistant."
        st.session_state.use_memory = True
        
        # Configure mocks
        mock_chat_input.return_value = None  # No user input
        
        # Mock the sidebar context manager
        mock_sidebar_context = MagicMock()
        mock_sidebar.return_value = mock_sidebar_context
        
        # Mock the expander context manager
        mock_expander_context = MagicMock()
        mock_expander.return_value = mock_expander_context
        
        # Call the main function
        main()
        
        # Check the basic UI elements were created
        mock_title.assert_called_once()
        assert mock_title.call_args[0][0] == "Research Agent - Gemini Chat"
        mock_markdown.assert_called_once()
        mock_chat_input.assert_called_once()
        mock_sidebar.assert_called_once()
        mock_expander.assert_called_once()

    @pytest.mark.skip(reason="Streamlit UI tests are challenging to run in a test environment without a ScriptRunContext")
    @patch("research_agent.ui.streamlit.gemini_chat.st.title")
    @patch("research_agent.ui.streamlit.gemini_chat.st.markdown") 
    @patch("research_agent.ui.streamlit.gemini_chat.st.chat_input")
    @patch("research_agent.ui.streamlit.gemini_chat.st.sidebar")
    @patch("research_agent.ui.streamlit.gemini_chat.st.expander")
    @patch("research_agent.ui.streamlit.gemini_chat.display_message")
    @patch("research_agent.ui.streamlit.gemini_chat.asyncio.run")
    def test_main_with_user_input(self, mock_asyncio_run, mock_display, mock_expander, 
                                 mock_sidebar, mock_chat_input, mock_markdown, mock_title):
        """Test the main function with user input."""
        # Set up session state
        if not hasattr(st, "session_state"):
            class SessionState:
                pass
            st.session_state = SessionState()
        
        # Set session state values
        st.session_state.chat_history = []
        st.session_state.system_prompt = "You are a helpful assistant."
        st.session_state.use_memory = True
        
        # Configure mocks
        mock_chat_input.return_value = "What is AI?"  # User input
        mock_asyncio_run.return_value = "AI stands for Artificial Intelligence."
        
        # Mock the sidebar context manager
        mock_sidebar_context = MagicMock()
        mock_sidebar.return_value = mock_sidebar_context
        
        # Mock the expander context manager
        mock_expander_context = MagicMock()
        mock_expander.return_value = mock_expander_context
        
        # Call the main function
        main()
        
        # Check chat input was processed
        mock_chat_input.assert_called_once()
        mock_display.assert_any_call("user", "What is AI?")
        
        # Check asyncio.run was called to generate a response
        mock_asyncio_run.assert_called_once()
        
        # Check the assistant response was displayed
        mock_display.assert_any_call("assistant", "AI stands for Artificial Intelligence.")
        
        # Check chat history was updated
        assert len(st.session_state.chat_history) == 2
        assert st.session_state.chat_history[0]["role"] == "user"
        assert st.session_state.chat_history[0]["content"] == "What is AI?"
        assert st.session_state.chat_history[1]["role"] == "assistant"
        assert st.session_state.chat_history[1]["content"] == "AI stands for Artificial Intelligence." 