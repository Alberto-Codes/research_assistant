"""
Node definitions for the Research Agent graph.

This module defines the nodes used in the Research Agent graph, primarily
the GeminiAgentNode for chat interactions.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar, cast

# Import what's available from pydantic_graph
from pydantic_graph import BaseNode, End, GraphRunContext


# Define NodeError if it's not available in pydantic_graph
class NodeError(Exception):
    """Error raised when a node fails to execute."""

    pass


from research_agent.core.dependencies import GeminiDependencies
from research_agent.core.state import MyState

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for the decorator
T = TypeVar("T")


def _measure_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure and print execution time of a node function.

    Args:
        func: The async function to measure.

    Returns:
        Decorated function that measures and reports execution time.

    Raises:
        NodeError: If there's an error during node execution
    """

    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        start_time = time.time()
        try:
            # Call the original function
            result = await func(self, ctx, *args, **kwargs)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log the result
            logger.info(
                "%s: %s (took %.3fs)", self._log_prefix, self._get_output_text(ctx), process_time
            )
            print(f"{self._log_prefix}: {self._get_output_text(ctx)} (took {process_time:.3f}s)")

            # Ensure we're returning a valid node
            if result is None:
                logger.error(
                    "Node %s returned None instead of a valid node", self.__class__.__name__
                )
                raise NodeError(
                    f"Node {self.__class__.__name__} returned None instead of a valid node"
                )

            return result

        except Exception as e:
            # Calculate time even for failures
            process_time = time.time() - start_time

            # Log the error
            logger.error(
                "Error in %s node after %.3fs: %s", self.__class__.__name__, process_time, str(e)
            )

            # Reraise as NodeError if it's not already
            if not isinstance(e, NodeError):
                raise NodeError(f"Node execution failed: {str(e)}") from e
            raise

    return cast(Callable[..., T], wrapper)


@dataclass
class GeminiAgentNode(BaseNode[MyState, GeminiDependencies, str]):
    """Node that processes a user prompt and generates an AI response using Gemini.

    This node takes the user_prompt from the state, sends it to the Gemini model,
    and stores the response in the state.
    """

    _log_prefix = "AI Response"

    def _get_output_text(self, ctx):
        """Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        return ctx.state.ai_response

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> End[str]:
        """Process the user prompt and generate an AI response.

        Args:
            ctx: The graph run context containing state and dependencies.

        Returns:
            An End object containing the AI response.
        """
        # Record the start time
        start_time = time.time()

        # Only generate response if we have a user prompt
        if ctx.state.user_prompt:
            # Use the LLM client from dependencies
            ctx.state.ai_response = await ctx.deps.llm_client.generate_text(ctx.state.user_prompt)
        else:
            ctx.state.ai_response = "No prompt provided. Please enter a question or prompt."

        # Record the generation time
        ctx.state.ai_generation_time = time.time() - start_time

        # Add to execution history
        if "node_execution_history" not in ctx.state.__dict__:
            ctx.state.node_execution_history = []
        ctx.state.node_execution_history.append(
            f"GeminiAgentNode: Generated response to '{ctx.state.user_prompt}'"
        )

        # Calculate the total execution time
        ctx.state.total_time = ctx.state.ai_generation_time

        # Return an End node with the AI response
        return End(ctx.state.ai_response)
