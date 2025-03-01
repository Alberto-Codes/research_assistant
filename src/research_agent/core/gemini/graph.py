"""
Graph definition for the Gemini chat functionality in the Research Agent.

This module defines the graph structure for the Research Agent application,
focusing on the Gemini chat functionality.
"""

from __future__ import annotations

import asyncio
import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

# Try to import from pydantic_graph with a fallback for GraphError
try:
    from pydantic_graph import Graph, GraphError, GraphRunResult
except ImportError:
    from pydantic_graph import Graph, GraphRunResult

    # Define GraphError if it's not available in pydantic_graph
    class GraphError(Exception):
        """Error raised when a graph fails to execute."""

        pass


from research_agent.core.gemini.dependencies import GeminiDependencies
from research_agent.core.gemini.nodes import GeminiAgentNode
from research_agent.core.gemini.state import GeminiState

# Set up logging
logger = logging.getLogger(__name__)


def get_gemini_agent_graph() -> Graph:
    """
    Create a Graph for the Gemini agent.

    This function creates a Graph for running a single node that processes
    a user prompt with the Gemini model.

    Returns:
        A Graph with a GeminiAgentNode.
    """
    # Create and return the graph with the GeminiAgentNode
    node = GeminiAgentNode()
    return Graph(nodes=[node])


async def run_gemini_agent_graph(
    user_prompt: str, dependencies: Optional[GeminiDependencies] = None
) -> Tuple[str, GeminiState, List[Any]]:
    """
    Run the Gemini agent graph with a user prompt.

    This function creates a state with the user prompt, creates a graph,
    and runs it to generate a response.

    Args:
        user_prompt: The user's prompt to process.
        dependencies: Optional dependencies to inject into the graph.
            If None, default dependencies will be created.

    Returns:
        A tuple containing the result string, the final state, and any errors.
    """
    # Create a state with the user prompt
    state = GeminiState(user_prompt=user_prompt)

    # Create dependencies if not provided
    if dependencies is None:
        dependencies = GeminiDependencies()

    # Get the Gemini agent graph
    graph = get_gemini_agent_graph()

    # Start timing
    start_time = datetime.datetime.now()
    logger.info("Starting Gemini agent graph at %s", start_time)

    # Run the graph
    try:
        result = await graph.run(GeminiAgentNode(), state=state, deps=dependencies)
        result_text = result.output
        final_state = result.state
        errors = []

    except GraphError as e:
        # Log the error
        logger.error("Gemini agent graph failed: %s", str(e))

        # Return error information
        result_text = f"Error: {str(e)}"
        final_state = state
        errors = [str(e)]

    # Calculate and log execution time
    end_time = datetime.datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    logger.info("Gemini agent graph completed in %.3f seconds", execution_time)

    return result_text, final_state, errors


def display_results(graph_result: Union[GraphRunResult, Any], verbose: bool = False) -> None:
    """
    Display the results of a graph execution.

    This function takes a GraphRunResult and displays its value,
    state details, and timing information.

    Args:
        graph_result: The result of running a graph.
        verbose: Whether to display verbose information.
    """
    # If it's not a GraphRunResult, just log it and return
    if not isinstance(graph_result, GraphRunResult):
        logger.info(f"Graph result is not a GraphRunResult: {graph_result}")
        return

    # Import DocumentState here to avoid circular imports
    from research_agent.core.document.state import DocumentState

    # Get the output and state from the result
    output = graph_result.output
    state = graph_result.state

    # Handle different state types with appropriate display
    if isinstance(state, GeminiState):
        logger.info(f"Result: {output}")

        if verbose:
            logger.debug(f"State: {state}")

            if graph_result.errors:
                logger.warning("Errors occurred during graph execution")
                for error in graph_result.errors:
                    logger.warning(f"Error: {error}")

    elif isinstance(state, DocumentState):
        doc_count = len(output.get("document_ids", []))
        logger.info(f"Ingested {doc_count} documents")

        if verbose:
            for idx, doc_id in enumerate(output.get("document_ids", [])):
                logger.debug(f"Document {idx+1}: {doc_id}")

        if verbose:
            logger.debug(f"State: {state}")

            if graph_result.errors:
                logger.warning("Errors occurred during graph execution")
                for error in graph_result.errors:
                    logger.warning(f"Error: {error}")
    else:
        logger.info(f"Result: {output}")

        if verbose:
            logger.debug(f"State: {state}")

            if graph_result.errors:
                logger.warning("Errors occurred during graph execution")
                for error in graph_result.errors:
                    logger.warning(f"Error: {error}")

    if verbose and hasattr(state, "execution_history"):
        logger.debug("Execution History:")
        for entry in state.execution_history:
            logger.debug(f"  {entry}")

    if hasattr(state, "total_time"):
        logger.info(f"Total execution time: {state.total_time:.3f} seconds")
