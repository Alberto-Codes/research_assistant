"""
Node definitions for the Gemini chat graph in the Research Agent.

This module defines the nodes used in the Gemini chat graph, primarily
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


from research_agent.core.gemini.dependencies import GeminiDependencies
from research_agent.core.gemini.state import GeminiState

# Set up logging
logger = logging.getLogger(__name__)

# Type variable for the decorator
T = TypeVar("T")


def _measure_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to measure and print execution time of a node function.

    This decorator wraps an async function and measures its execution time.
    It also updates the node_execution_history in the state object.

    Args:
        func: The async function to measure.

    Returns:
        A wrapped function that measures execution time.
    """

    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        """
        Wrapper that measures and logs execution time.

        Args:
            self: The node instance.
            ctx: The graph run context.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.

        Returns:
            The result of the wrapped function.
        """
        # Get the node class name for logging
        node_name = self.__class__.__name__

        # Log the start of execution
        logger.debug("Starting execution of %s", node_name)

        # Record the start time
        start_time = time.time()

        # Execute the wrapped function
        try:
            result = await func(self, ctx, *args, **kwargs)

            # Ensure result is an End object if expected
            if func.__name__ == "run" and not isinstance(result, End):
                raise NodeError(f"Node {node_name} did not return an End object")

            # Calculate and log execution time
            execution_time = time.time() - start_time
            logger.debug("%s completed in %.3f seconds", node_name, execution_time)

            # Add to the execution history if available
            if hasattr(ctx.state, "node_execution_history"):
                output_text = (
                    f"{self._log_prefix}: {self._get_output_text(ctx)}"
                    if hasattr(self, "_log_prefix") and hasattr(self, "_get_output_text")
                    else "completed"
                )
                ctx.state.node_execution_history.append(
                    f"{node_name}: {output_text} (took {execution_time:.3f}s)"
                )

            return result

        except Exception as e:
            # Log the error
            logger.error("Error in %s: %s", node_name, str(e))

            # Add to the execution history if available
            if hasattr(ctx.state, "node_execution_history"):
                ctx.state.node_execution_history.append(f"{node_name}: Error - {str(e)}")

            # Re-raise the exception
            raise

    return wrapper


@dataclass
class GeminiAgentNode(BaseNode[GeminiState, GeminiDependencies, str]):
    """
    Node that processes a user prompt and generates an AI response using Gemini.

    This node takes the user_prompt from the state, sends it to the Gemini model,
    and stores the response in the state.
    """

    _log_prefix = "AI Response"

    def _get_output_text(self, ctx):
        """
        Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        return ctx.state.ai_response

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> End[str]:
        """
        Process the user prompt and generate an AI response.

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

        # Calculate the total execution time
        ctx.state.total_time = ctx.state.ai_generation_time

        # Return an End node with the AI response
        return End(ctx.state.ai_response)
