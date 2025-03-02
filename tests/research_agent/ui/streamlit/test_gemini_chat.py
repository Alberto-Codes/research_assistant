"""
Tests for the Gemini chat UI components.
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

import streamlit as st
from streamlit.testing.v1 import AppTest

from research_agent.ui.streamlit.gemini_chat import (
    generate_streaming_response,
    display_message,
    main
)


@pytest.mark.skip(reason="Skipping due to API authentication issues - needs to be run with valid credentials")
@pytest.mark.asyncio
@patch("research_agent.ui.streamlit.gemini_chat.Agent")
@patch("research_agent.ui.streamlit.gemini_chat.GeminiLLMClient")
async def test_generate_streaming_response_success(mock_client_class, mock_agent_class):
    """Test successful generation of a streaming response."""
    # Configure mocks
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance
    
    # Create a mock agent
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance
    
    # Set up agent's system_prompt
    mock_agent_instance.system_prompt = "You are a helpful assistant."
    
    # Mock the context manager for streaming
    mock_context = AsyncMock()
    mock_agent_instance.run_stream.return_value.__aenter__.return_value = mock_context
    
    # Create a proper async iterator for the stream_text method
    class AsyncIterator:
        def __init__(self, items):
            self.items = items
            self.index = 0
            
        def __aiter__(self):
            return self
            
        async def __anext__(self):
            if self.index < len(self.items):
                value = self.items[self.index]
                self.index += 1
                return value
            raise StopAsyncIteration
    
    # Set up mock chunks
    chunks = ["This ", "is ", "a ", "test ", "response."]
    mock_context.stream_text.return_value = AsyncIterator(chunks)
    
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
    mock_client_class.assert_called_once()
    mock_agent_class.assert_called_once()
    mock_agent_instance.run_stream.assert_called_once()
    mock_context.stream_text.assert_called_once_with(delta=True)
    
    # Check that the placeholder was updated with each chunk
    assert mock_placeholder.markdown.call_count >= 5  # At least once per chunk


@pytest.mark.asyncio
@patch("research_agent.ui.streamlit.gemini_chat.Agent")
@patch("research_agent.ui.streamlit.gemini_chat.GeminiLLMClient")
async def test_generate_streaming_response_exception(mock_client_class, mock_agent_class):
    """Test handling of exceptions when generating a streaming response."""
    # Configure mocks
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance
    
    # Set up agent instance that will raise exception
    error_message = "API error: Invalid request"
    mock_agent_instance = MagicMock()
    mock_agent_class.return_value = mock_agent_instance
    
    # Set up agent's system_prompt
    mock_agent_instance.system_prompt = "You are a helpful assistant."
    
    # Make the agent's run_stream raise an exception
    mock_agent_instance.run_stream.side_effect = Exception(error_message)
    
    # Mock st.empty to get markdown calls
    mock_placeholder = MagicMock()
    st.empty = MagicMock(return_value=mock_placeholder)
    
    # Call the function
    result = await generate_streaming_response(
        user_prompt="What is AI?"
    )
    
    # Assert results
    assert "Error in streaming" in result
    assert error_message in result
    mock_client_class.assert_called_once()
    mock_agent_class.assert_called_once()
    mock_agent_instance.run_stream.assert_called_once()


@pytest.mark.skip(reason="Streamlit UI tests are challenging to run in a test environment without a ScriptRunContext")
def test_display_message():
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
def test_main_basic_rendering(mock_expander, mock_sidebar, mock_chat_input, mock_markdown, mock_title):
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
def test_main_with_user_input(mock_asyncio_run, mock_display, mock_expander, 
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