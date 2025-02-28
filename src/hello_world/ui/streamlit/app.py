"""
Streamlit interface for the Hello World application.

This module provides a Streamlit web interface for the Hello World
graph example, allowing users to interact with the application through a GUI.
"""

import asyncio
import time
from typing import Optional

import streamlit as st

# Import directly from core modules instead of services
from hello_world.core.dependencies import HelloWorldDependencies
from hello_world.core.graph import get_hello_world_graph, run_graph
from hello_world.core.state import MyState

st.set_page_config(
    page_title="Hello World Graph",
    page_icon="👋",
    layout="centered",
    initial_sidebar_state="expanded",
)


def run_async(coroutine):
    """
    Helper function to run async code in Streamlit.

    Args:
        coroutine: The coroutine to run.

    Returns:
        The result of the coroutine.
    """
    return asyncio.run(coroutine)


async def generate_hello_world(
    use_custom_llm: bool = False, prefix: Optional[str] = None
) -> MyState:
    """
    Generate a hello world message using the graph.

    Args:
        use_custom_llm: Whether to use a custom LLM client.
        prefix: Optional prefix to add to the generated text.

    Returns:
        The final state after running the graph.
    """
    # Create dependencies with the specified configuration
    dependencies = HelloWorldDependencies(use_custom_llm=use_custom_llm, prefix=prefix)

    # Run the graph directly with the dependencies
    output, final_state, history = await run_graph(
        initial_state=MyState(), dependencies=dependencies
    )
    return final_state


def main():
    """Main Streamlit application function."""
    st.title("Hello World Graph")
    st.markdown(
        """
    This application demonstrates a simple graph-based workflow using Pydantic Graph.
    You can choose to use a custom LLM client and add a prefix to the generated text.
    """
    )

    # Create a sidebar for configuration options
    st.sidebar.header("Configuration")
    use_custom_llm = st.sidebar.checkbox("Use Custom LLM Client", value=True)
    prefix = st.sidebar.text_input("Prefix for generated text", value="")

    # Use empty prefix as None for the service
    prefix_param: Optional[str] = prefix if prefix else None

    # Create a button to generate
    if st.button("Generate Hello World", type="primary"):
        with st.spinner("Generating..."):
            # Create a placeholder for the result
            result_container = st.container()

            # Call the service
            start_time = time.time()
            final_state = run_async(
                generate_hello_world(use_custom_llm=use_custom_llm, prefix=prefix_param)
            )
            total_time = time.time() - start_time

            # Display the results
            with result_container:
                st.success(f"Final output: {final_state.combined_text}")

                # Display timing information
                st.subheader("Timing Information")
                st.markdown(f"- Hello generation: **{final_state.hello_generation_time:.3f}s**")
                st.markdown(f"- World generation: **{final_state.world_generation_time:.3f}s**")
                st.markdown(f"- Combine operation: **{final_state.combine_generation_time:.3f}s**")
                st.markdown(f"- Total graph execution: **{final_state.total_time:.3f}s**")
                st.markdown(f"- Total app time: **{total_time:.3f}s**")

                # Display the state
                st.subheader("Final State")
                st.json(
                    {
                        "hello_text": final_state.hello_text,
                        "world_text": final_state.world_text,
                        "combined_text": final_state.combined_text,
                    }
                )

                # Display execution history
                st.subheader("Execution History")
                for entry in final_state.node_execution_history:
                    st.markdown(f"- {entry}")


# Call the main function directly when this script is run by Streamlit
main()
