"""
Services for the Hello World application.

This module provides service functions that can be used by different interfaces
(CLI, Streamlit, FastAPI) to access the core functionality of the application.
"""

from typing import Any, List, Optional, Tuple

from pydantic_graph import Graph

from hello_world.core.dependencies import HelloWorldDependencies
from hello_world.core.graph import get_gemini_agent_graph as core_get_gemini_agent_graph
from hello_world.core.graph import get_hello_world_graph as core_get_hello_world_graph
from hello_world.core.graph import run_gemini_agent_graph, run_graph
from hello_world.core.nodes import CombineNode, GeminiAgentNode, HelloNode, PrintNode, WorldNode
from hello_world.core.state import MyState

# Try to import GraphDeps, or define it if not available
try:
    from pydantic_graph import GraphDeps
except ImportError:
    # Define GraphDeps locally if not available in pydantic_graph
    class GraphDeps:
        """Mock GraphDeps class used when the real one is not available."""

        pass


from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

from pydantic_graph.nodes import BaseNode, GraphRunContext


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

    # Use our local run_graph function
    output, final_state, history = await run_graph(
        initial_state=MyState(), dependencies=dependencies
    )
    return final_state


async def generate_ai_response(
    user_prompt: str, project_id: Optional[str] = None, use_mock_gemini: bool = False
) -> MyState:
    """
    Generate an AI response using the Gemini model.

    Args:
        user_prompt: The user's prompt to send to the Gemini model.
        project_id: Optional Google Cloud project ID. If None, will try to detect from environment.
        use_mock_gemini: Whether to use the mock Gemini client for local testing.

    Returns:
        The final state after running the graph.
    """
    # Create dependencies with Gemini configuration
    dependencies = HelloWorldDependencies(
        use_gemini=True, project_id=project_id, use_mock_gemini=use_mock_gemini
    )

    # Use our local run_gemini_agent_graph function
    output, final_state, history = await run_gemini_agent_graph(
        user_prompt=user_prompt, dependencies=dependencies
    )
    return final_state


def get_hello_world_graph() -> Graph:
    """
    Get the Hello World graph.

    Returns:
        A configured Graph instance.
    """
    # Use the imported function from core module instead of duplicating
    return core_get_hello_world_graph()


def get_gemini_agent_graph() -> Graph:
    """
    Get the Gemini agent graph.

    Returns:
        A configured Graph instance.
    """
    # Use the imported function from core module
    return core_get_gemini_agent_graph()


async def run_graph(
    initial_state: Optional[MyState] = None, dependencies: Optional[HelloWorldDependencies] = None
) -> Tuple[str, MyState, List[Any]]:
    """
    Run the Hello World graph.

    Args:
        initial_state: Optional initial state. If not provided, a new MyState will be created.
        dependencies: Optional dependencies. If not provided, default dependencies will be used.

    Returns:
        A tuple of (output, final_state, history)
    """
    # Create a new state if none is provided
    state = initial_state or MyState()

    # Create dependencies if none are provided
    deps = dependencies or HelloWorldDependencies()

    # Get the graph
    graph = get_hello_world_graph()

    # Run the graph with state and deps
    # Pass the dependencies directly to run
    graph_result = await graph.run(HelloNode(), state=state, deps=deps)

    return graph_result.output, graph_result.state, graph_result.history
