"""
Streamlit interface for the Gemini Chat application.

This module provides a Streamlit web interface for users to interact with
the Gemini LLM through the pydantic-graph implementation.
"""

import asyncio
import time
import json
from typing import Optional, List, Any, Tuple, AsyncGenerator, Dict
from datetime import datetime

import streamlit as st
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
try:
    nest_asyncio.apply()
except Exception as e:
    print(f"Warning: Could not apply nest_asyncio: {e}")

# Import directly from core modules
from hello_world.core.dependencies import HelloWorldDependencies, GeminiLLMClient
from hello_world.core.graph import run_gemini_agent_graph
from hello_world.core.state import MyState

# Try to import pydantic-ai message parts
try:
    from pydantic_ai.messages import (
        ModelMessage,
        ModelRequest,
        ModelResponse,
        SystemPromptPart,
        UserPromptPart,
        TextPart,
        ToolCallPart,
        ToolReturnPart,
    )
    from pydantic_ai.agent import Agent
    PYDANTIC_AI_AVAILABLE = True
except ImportError:
    PYDANTIC_AI_AVAILABLE = False
    print("Warning: pydantic_ai.messages modules not available. Streaming may not work as expected.")

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


def run_async(coroutine):
    """
    Helper function to run async code in Streamlit.
    
    Args:
        coroutine: The coroutine to run.
        
    Returns:
        The result of the coroutine.
    """
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            # Create a new event loop if the current one is closed
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)
    except RuntimeError:
        # If there's no event loop in this thread, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coroutine)


async def generate_gemini_response(user_prompt: str) -> Tuple[str, MyState, List[Any]]:
    """
    Generate a response using the Gemini agent.
    
    Args:
        user_prompt: The user's input prompt.
        
    Returns:
        A tuple of (output, final_state, history).
    """
    # Create dependencies with Gemini enabled
    dependencies = HelloWorldDependencies(use_gemini=True)
    
    # Run the graph with the user prompt
    output, final_state, history = await run_gemini_agent_graph(
        user_prompt=user_prompt,
        dependencies=dependencies
    )
    
    return output, final_state, history


async def generate_streaming_response(
    user_prompt: str, 
    system_prompt: Optional[str] = None,
    message_history: Optional[List[Dict]] = None
) -> AsyncGenerator[str, None]:
    """
    Generate a streaming response using the Gemini agent directly.
    This bypasses the graph for a more responsive streaming experience.
    
    Args:
        user_prompt: The user's input prompt.
        system_prompt: Optional system prompt to configure the model behavior.
        message_history: Optional list of previous message objects to provide context.
        
    Yields:
        Chunks of the response text as they are generated.
    """
    # Create a Gemini LLM client directly
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
    
    # If streaming is supported with the available client
    if hasattr(gemini_client, 'agent') and hasattr(gemini_client.agent, 'run_stream'):
        try:
            # Get the system prompt
            system_prompt_text = system_prompt or DEFAULT_SYSTEM_PROMPT
            
            # If we're using a custom system prompt, update it in the agent
            if system_prompt_text != gemini_client.agent.system_prompt:
                # Create a new agent with the updated system prompt
                gemini_client.agent = Agent(
                    gemini_client.vertex_model,
                    system_prompt=system_prompt_text
                )
            
            # Use the agent's streaming capability from pydantic-ai
            async with gemini_client.agent.run_stream(
                user_prompt,
                message_history=pydantic_ai_messages
            ) as result:
                async for chunk in result.stream_text(delta=True):
                    yield chunk
        except Exception as e:
            yield f"Error in streaming: {str(e)}"
    else:
        # Fall back to non-streaming response
        try:
            response = await gemini_client.generate_text(user_prompt)
            yield response
        except Exception as e:
            yield f"Error generating response: {str(e)}"


# Function to display chat messages
def display_message(role, content, avatar=None):
    """Display a chat message with the specified role and content."""
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def stream_response_sync(prompt: str, system_prompt: Optional[str] = None):
    """
    Synchronous wrapper for the async stream_response function.
    This helps manage the event loop properly in Streamlit.
    
    Args:
        prompt: The user's prompt to respond to.
        system_prompt: Optional system prompt to configure the model behavior.
        
    Returns:
        The full generated response.
    """
    async def _stream_with_fallback():
        try:
            # Message placeholder setup
            message_placeholder = st.empty()
            full_response = ""
            
            # Get the message history for context
            message_history = None
            if "chat_history" in st.session_state and st.session_state.get("use_memory", True):
                # Skip the last user message as we're already sending it directly
                message_history = st.session_state.chat_history[:-1] if st.session_state.chat_history else []
            
            # Use our streaming response generator
            try:
                async for chunk in generate_streaming_response(
                    prompt, 
                    system_prompt=system_prompt,
                    message_history=message_history
                ):
                    full_response += chunk
                    # Update the placeholder with the growing response
                    message_placeholder.markdown(full_response + "▌")
            except Exception as e:
                # Catch streaming errors and append to the response
                error_message = f"\n\nError during streaming: {str(e)}"
                full_response += error_message
                message_placeholder.markdown(full_response)
            
            # Replace the placeholder with the final response
            message_placeholder.empty()
            
            return full_response
        except Exception as outer_e:
            # Catch any other errors in the streaming process
            return f"Failed to generate response: {str(outer_e)}"
    
    # Use the run_async helper to manage the event loop
    return run_async(_stream_with_fallback())


async def stream_response(prompt: str, system_prompt: Optional[str] = None):
    """
    Stream the AI response to the Streamlit UI.
    
    Args:
        prompt: The user's prompt to respond to.
        system_prompt: Optional system prompt to configure the model behavior.
        
    Returns:
        The full generated response.
    """
    message_placeholder = st.empty()
    full_response = ""
    
    # Get the message history for context
    message_history = None
    if "chat_history" in st.session_state and st.session_state.get("use_memory", True):
        # Skip the last user message as we're already sending it directly
        message_history = st.session_state.chat_history[:-1] if st.session_state.chat_history else []
    
    # Use our streaming response generator
    async for chunk in generate_streaming_response(
        prompt, 
        system_prompt=system_prompt,
        message_history=message_history
    ):
        full_response += chunk
        # Update the placeholder with the growing response
        message_placeholder.markdown(full_response + "▌")
    
    # Replace the placeholder with a chat message
    message_placeholder.empty()
    
    # Return the full response
    return full_response


def main():
    """Main Streamlit application function."""
    st.title("Research Agent - Gemini Chat")
    st.markdown("""
    This application allows you to chat with Google's Gemini LLM through the Research Agent framework.
    """)
    
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
            help="This prompt sets the behavior and role of the AI assistant."
        )
        
        # Memory toggle
        st.session_state.use_memory = st.toggle(
            "Use Chat History", 
            value=st.session_state.use_memory,
            help="When enabled, the AI will remember previous messages in the conversation."
        )
        
        # Add a button to clear the chat history
        if st.button("Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()
        
        # Display warning if pydantic_ai is not available
        if not PYDANTIC_AI_AVAILABLE:
            st.warning("pydantic_ai.messages module not available. Streaming functionality is limited.")
        
        # About section
        st.header("About")
        st.markdown("""
        This chat interface uses the Research Agent framework to communicate with Google's Gemini LLM.
        
        The application is built on:
        - Pydantic Graph for workflow management
        - Vertex AI for model access via pydantic-ai
        - Streamlit for the user interface
        """)
    
    # Show system prompt as a special message at the top (collapsible)
    with st.expander("System Prompt (Click to view)", expanded=False):
        with st.chat_message("system", avatar="⚙️"):
            st.markdown(st.session_state.system_prompt)
    
    # Display the chat history
    for message in st.session_state.chat_history:
        display_message(
            role=message["role"],
            content=message["content"],
            avatar=message.get("avatar")
        )
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add the user message to the chat history and display it
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
        
        # Display the user message
        display_message("user", prompt)
        
        # Generate a streaming response
        with st.chat_message("assistant", avatar="🧠"):
            start_time = time.time()
            
            # Use the synchronous wrapper for streaming
            full_response = stream_response_sync(
                prompt, 
                system_prompt=st.session_state.system_prompt
            )
            
            # Display the full response (the streaming already showed it, this ensures it stays visible)
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
                st.markdown(f"**Conversation length:** {len(st.session_state.chat_history)} messages")
        
        # Add the assistant's response to the chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.now().isoformat(),
            "avatar": "🧠"
        })
        
        # Provide an option to save the conversation
        if len(st.session_state.chat_history) > 2:  # Only show after at least one exchange
            with st.expander("Save conversation", expanded=False):
                conversation_json = json.dumps(st.session_state.chat_history, indent=2)
                st.download_button(
                    label="Download conversation as JSON",
                    data=conversation_json,
                    file_name=f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.code(conversation_json, language="json")


if __name__ == "__main__":
    main() 