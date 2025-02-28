"""
Services for the Research Agent application.

This module provides service functions that can be used by different interfaces
(CLI, Streamlit, FastAPI) to access the core functionality of the application.
"""

from typing import Any, List, Optional, Tuple

from pydantic_graph import Graph

from research_agent.core.dependencies import GeminiDependencies
from research_agent.core.graph import get_gemini_agent_graph as core_get_gemini_agent_graph
from research_agent.core.graph import run_gemini_agent_graph
from research_agent.core.nodes import GeminiAgentNode
from research_agent.core.state import MyState

# Try to import GraphDeps, or define it if not available
try:
    from pydantic_graph import GraphDeps
except ImportError:
    # Define GraphDeps locally if not available in pydantic_graph
    class GraphDeps:
        """Mock GraphDeps class used when the real one is not available."""

        pass


async def generate_ai_response(user_prompt: str, project_id: Optional[str] = None) -> MyState:
    """
    Generate an AI response using the Gemini model.

    Args:
        user_prompt: The user's prompt to send to the Gemini model.
        project_id: Optional Google Cloud project ID. If None, will try to detect from environment.

    Returns:
        The final state after running the graph.
    """
    # Create dependencies with Gemini configuration
    dependencies = GeminiDependencies(project_id=project_id)

    # Use the run_gemini_agent_graph function
    output, final_state, history = await run_gemini_agent_graph(
        user_prompt=user_prompt, dependencies=dependencies
    )
    return final_state


def get_gemini_agent_graph() -> Graph:
    """
    Get the Gemini agent graph.

    Returns:
        A configured Graph instance.
    """
    # Use the imported function from core module
    return core_get_gemini_agent_graph()
