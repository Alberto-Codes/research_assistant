"""
Node definitions for the Hello World graph.

This module defines the nodes used in the Hello World graph, including
the HelloNode, WorldNode, CombineNode, and PrintNode. Each node performs
a specific operation in the graph workflow.
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


from hello_world.core.dependencies import HelloWorldDependencies
from hello_world.core.state import MyState

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
class HelloNode(BaseNode[MyState, HelloWorldDependencies, str]):
    """First node that generates the 'Hello' text.

    This node uses the LLM client from dependencies to generate
    a greeting word if it's not already set in the state.
    """

    _log_prefix = "Generated"

    def _get_output_text(self, ctx):
        """Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        return ctx.state.hello_text

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> WorldNode:
        """Set the hello_text in the state and return the next node.

        Args:
            ctx: The graph run context containing state and dependencies.

        Returns:
            The next node to run in the graph.
        """
        # Record the start time
        start_time = time.time()

        # Only set hello_text if it's not already set
        if not ctx.state.hello_text:
            # Use the LLM client from dependencies
            ctx.state.hello_text = await ctx.deps.llm_client.generate_text(
                "Generate a greeting word like 'Hello'"
            )

        # Add a small delay to simulate processing
        await asyncio.sleep(0.1)

        # Record the generation time
        ctx.state.hello_generation_time = time.time() - start_time

        # Add to execution history
        if "node_execution_history" not in ctx.state.__dict__:
            ctx.state.node_execution_history = []
        ctx.state.node_execution_history.append(f"HelloNode: Generated '{ctx.state.hello_text}'")

        return WorldNode()


@dataclass
class WorldNode(BaseNode[MyState, HelloWorldDependencies, str]):
    """Second node that generates the 'World' text.

    This node uses the LLM client from dependencies to generate
    a noun if it's not already set in the state.
    """

    _log_prefix = "Generated"

    def _get_output_text(self, ctx):
        """Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        return ctx.state.world_text

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> CombineNode:
        """Set the world_text in the state and return the next node.

        Args:
            ctx: The graph run context containing state and dependencies.

        Returns:
            The next node to run in the graph.
        """
        # Record the start time
        start_time = time.time()

        # Only set world_text if it's not already set
        if not ctx.state.world_text:
            # Use the LLM client from dependencies
            ctx.state.world_text = await ctx.deps.llm_client.generate_text(
                "Generate a noun like 'World'"
            )

        # Add a small delay to simulate processing
        await asyncio.sleep(0.2)

        # Record the generation time
        ctx.state.world_generation_time = time.time() - start_time

        # Add to execution history
        ctx.state.node_execution_history.append(f"WorldNode: Generated '{ctx.state.world_text}'")

        return CombineNode()


@dataclass
class CombineNode(BaseNode[MyState, HelloWorldDependencies, str]):
    """Third node that combines the hello and world texts.

    This node combines the hello_text and world_text from the state
    to create a combined message.
    """

    _log_prefix = "Combined"

    def _get_output_text(self, ctx):
        """Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        return ctx.state.combined_text

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> PrintNode:
        """Combine the hello_text and world_text and return the next node.

        Args:
            ctx: The graph run context containing state and dependencies.

        Returns:
            The next node to run in the graph.
        """
        # Record the start time
        start_time = time.time()

        ctx.state.combined_text = f"{ctx.state.hello_text} {ctx.state.world_text}!"

        # Add a small delay to simulate processing
        await asyncio.sleep(0.15)

        # Record the generation time
        ctx.state.combine_generation_time = time.time() - start_time

        # Add to execution history
        ctx.state.node_execution_history.append(
            f"CombineNode: Combined '{ctx.state.combined_text}'"
        )

        return PrintNode()


@dataclass
class PrintNode(BaseNode[MyState, HelloWorldDependencies, str]):
    """Final node that prints the combined text and ends the graph.

    This node takes the combined_text from the state, prints it,
    and returns an End object to end the graph execution.
    """

    _log_prefix = "Final output"

    def _get_output_text(self, ctx):
        """Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        return ctx.state.combined_text

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> End[str]:
        """Print the final output and end the graph execution.

        Args:
            ctx: The graph run context containing state and dependencies.

        Returns:
            An End object containing the combined text.
        """
        # Record the start time
        start_time = time.time()

        # Add a small delay to simulate processing
        await asyncio.sleep(0.05)

        # Calculate the total execution time
        ctx.state.total_time = (
            time.time()
            - start_time
            + ctx.state.hello_generation_time
            + ctx.state.world_generation_time
            + ctx.state.combine_generation_time
        )

        # Add to execution history
        ctx.state.node_execution_history.append(
            f"PrintNode: Final output '{ctx.state.combined_text}'"
        )

        return End(ctx.state.combined_text)


@dataclass
class GeminiAgentNode(BaseNode[MyState, HelloWorldDependencies, str]):
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

        return End(ctx.state.ai_response)
