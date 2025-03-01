"""
Streamlit interface for the Gemini Chat application.

This module provides a Streamlit web interface for users to interact with
the Gemini LLM through the pydantic-graph implementation.
"""

import asyncio
import json
import logging
import time
import traceback
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import nest_asyncio
import streamlit as st

# Set up logger
logger = logging.getLogger(__name__)

# Apply nest_asyncio to allow nested event loops
try:
    nest_asyncio.apply()
except Exception as e:
    st.warning(f"Could not apply nest_asyncio: {e}")

# Import directly from core modules
from research_agent.core.gemini.dependencies import GeminiDependencies, GeminiLLMClient
from research_agent.core.gemini.graph import run_gemini_agent_graph
from research_agent.core.gemini.state import GeminiState

# Try to import pydantic-ai message parts
try:
    from pydantic_ai.agent import Agent
    from pydantic_ai.messages import (
        ModelMessage,
        ModelRequest,
        ModelResponse,
        SystemPromptPart,
        TextPart,
        ToolCallPart,
        ToolReturnPart,
        UserPromptPart,
    )

    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    st.warning("pydantic_ai.messages modules not available. Streaming may not work as expected.")

# Only set page config when running this file directly, not when imported
if __name__ == "__main__":
    # Set up the Streamlit page configuration
    st.set_page_config(
        page_title="Research Agent - Gemini Chat",
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="expanded",
    )

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """You are a helpful research assistant powered by Gemini.
Your goal is to provide accurate, informative, and helpful responses.
You should be concise but thorough, and always strive to answer the user's question directly.
If you don't know the answer to something, admit it rather than making up information."""


async def generate_streaming_response(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    message_history: Optional[List[Dict]] = None,
) -> str:
    """
    Generate a streaming response and display it in the Streamlit UI.

    Args:
        user_prompt: The user's prompt to respond to.
        system_prompt: Optional system prompt to configure the model behavior.
        message_history: Optional list of previous messages for context.

    Returns:
        The complete generated response.
    """
    # Create a message placeholder for streaming
    message_placeholder = st.empty()
    full_response = ""

    try:
        # Create a Gemini LLM client
        gemini_client = GeminiLLMClient()

        # Convert message history to pydantic-ai format if available
        pydantic_ai_messages = []
        if PYDANTIC_AI_AVAILABLE and message_history:
            for msg in message_history:
                if msg["role"] == "user":
                    pydantic_ai_messages.append(
                        ModelRequest(parts=[UserPromptPart(content=msg["content"])])
                    )
                elif msg["role"] == "assistant":
                    pydantic_ai_messages.append(
                        ModelResponse(parts=[TextPart(content=msg["content"])])
                    )

        # Set the system prompt
        system_prompt_text = system_prompt or DEFAULT_SYSTEM_PROMPT
        if system_prompt_text != gemini_client.agent.system_prompt:
            gemini_client.agent = Agent(
                gemini_client.vertex_model, system_prompt=system_prompt_text
            )

        # Stream the response using the context manager
        async with gemini_client.agent.run_stream(
            user_prompt, message_history=pydantic_ai_messages
        ) as result:
            # Initialize flag to track if we received any content
            received_content = False

            # Stream chunks of text
            async for chunk in result.stream_text(delta=True):
                if chunk:  # Only process non-empty chunks
                    received_content = True
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")

            # If we didn't receive any content, provide a friendly message
            if not received_content:
                full_response = "I'm not sure how to respond to that. Could you please provide more context or ask a specific question?"
                message_placeholder.markdown(full_response)

        # Clear the placeholder when done streaming
        message_placeholder.empty()
        return full_response

    except Exception as e:
        # Log detailed error information
        # Check for specific error types
        if "without content or tool calls" in str(e):
            # This is the specific empty response error
            error_message = "I couldn't generate a response to that message. Could you try asking something else?"
        elif "rate limit" in str(e).lower():
            # Rate limit error
            error_message = "I've hit a rate limit. Please wait a moment before trying again."
        elif "permission" in str(e).lower() or "access" in str(e).lower():
            # Permission/authentication error
            error_message = "There seems to be an authentication issue with the AI service. Please check your credentials."
        else:
            # Generic error
            error_message = f"Error in streaming: {str(e)}"

        logger.error(f"Exception details: {traceback.format_exc()}")

        # Update the placeholder with the error
        message_placeholder.empty()
        return error_message


# Function to display chat messages
def display_message(role, content, avatar=None):
    """Display a chat message with the specified role and content."""
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def main():
    """Main Streamlit application function."""
    st.title("Research Agent - Gemini Chat")
    st.markdown(
        """
    This application allows you to chat with Google's Gemini LLM through the Research Agent framework.
    """
    )

    # Initialize the chat history in session state if it doesn't exist
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Initialize other session state variables
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

    if "use_memory" not in st.session_state:
        st.session_state.use_memory = True

    # Set up the sidebar
    with st.sidebar:
        st.header("Chat Configuration")

        # System prompt configuration
        st.session_state.system_prompt = st.text_area(
            "System Prompt",
            value=st.session_state.system_prompt,
            height=150,
            help="This prompt sets the behavior and role of the AI assistant.",
        )

        # Memory toggle
        st.session_state.use_memory = st.toggle(
            "Use Chat History",
            value=st.session_state.use_memory,
            help="When enabled, the AI will remember previous messages in the conversation.",
        )

        # Add a button to clear the chat history
        if st.button("Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()

        # Display warning if pydantic_ai is not available
        if not PYDANTIC_AI_AVAILABLE:
            st.warning(
                "pydantic_ai.messages module not available. Streaming functionality is limited."
            )

        # About section
        st.header("About")
        st.markdown(
            """
        This chat interface uses the Research Agent framework to communicate with Google's Gemini LLM.
        
        The application is built on:
        - Pydantic Graph for workflow management
        - Vertex AI for model access via pydantic-ai
        - Streamlit for the user interface
        """
        )

    # Show system prompt as a special message at the top (collapsible)
    with st.expander("System Prompt (Click to view)", expanded=False):
        with st.chat_message("system", avatar="⚙️"):
            st.markdown(st.session_state.system_prompt)

    # Display the chat history
    for message in st.session_state.chat_history:
        display_message(
            role=message["role"], content=message["content"], avatar=message.get("avatar")
        )

    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add the user message to the chat history and display it
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()}
        )

        # Display the user message
        display_message("user", prompt)

        # Generate a streaming response
        with st.chat_message("assistant", avatar="🧠"):
            start_time = time.time()

            # Get the message history for context
            message_history = None
            if "chat_history" in st.session_state and st.session_state.get("use_memory", True):
                # Skip the last user message as we're already sending it directly
                message_history = (
                    st.session_state.chat_history[:-1] if st.session_state.chat_history else []
                )

            # Use asyncio.run to properly manage the event loop
            try:
                full_response = asyncio.run(
                    generate_streaming_response(
                        prompt,
                        system_prompt=st.session_state.system_prompt,
                        message_history=message_history,
                    )
                )

                # Display the full response
                st.markdown(full_response)

                # Calculate generation time
                total_time = time.time() - start_time

                # Display debug information in an expander
                with st.expander("Response details", expanded=False):
                    st.markdown(f"**Total response time:** {total_time:.3f}s")

                    # Show whether memory was used
                    memory_status = "Enabled" if st.session_state.use_memory else "Disabled"
                    st.markdown(f"**Chat memory:** {memory_status}")

                    # Show conversation length
                    st.markdown(
                        f"**Conversation length:** {len(st.session_state.chat_history)} messages"
                    )

                # Add the assistant's response to the chat history
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": full_response,
                        "timestamp": datetime.now().isoformat(),
                        "avatar": "🧠",
                    }
                )
            except Exception as e:
                error_message = f"Failed to generate response: {str(e)}"
                st.error(error_message)
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "timestamp": datetime.now().isoformat(),
                        "avatar": "🧠",
                    }
                )

        # Provide an option to save the conversation
        if len(st.session_state.chat_history) > 2:  # Only show after at least one exchange
            with st.expander("Save conversation", expanded=False):
                conversation_json = json.dumps(st.session_state.chat_history, indent=2)
                st.download_button(
                    label="Download conversation as JSON",
                    data=conversation_json,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                )
                st.code(conversation_json, language="json")


if __name__ == "__main__":
    main()
