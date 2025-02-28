"""
Node definitions for the Hello World graph.

This module defines the nodes used in the Hello World graph, including
the HelloNode, WorldNode, CombineNode, and PrintNode. Each node performs
a specific operation in the graph workflow.
"""

from __future__ import annotations
from dataclasses import dataclass
import time
import functools
from typing import Any, TypeVar, Callable, cast
import asyncio

from pydantic_graph import BaseNode, End, GraphRunContext

from .state import MyState
from .dependencies import GraphDependencies


T = TypeVar('T')


def _measure_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure and print execution time of a node function.
    
    Args:
        func: The async function to measure.
        
    Returns:
        Decorated function that measures and reports execution time.
    """
    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        start_time = time.time()
        result = await func(self, ctx, *args, **kwargs)
        process_time = time.time() - start_time
        print(f"{self._log_prefix}: {self._get_output_text(ctx)} (took {process_time:.3f}s)")
        return result
    return cast(Callable[..., T], wrapper)


@dataclass
class HelloNode(BaseNode[MyState, GraphDependencies, str]):
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
        # Only set hello_text if it's not already set
        if not ctx.state.hello_text:
            # Use the LLM client from dependencies
            ctx.state.hello_text = await ctx.deps.llm_client.generate_text(
                "Generate a greeting word like 'Hello'"
            )
        
        # Add a small delay to simulate processing
        await asyncio.sleep(0.1)
        
        return WorldNode()


@dataclass
class WorldNode(BaseNode[MyState, GraphDependencies, str]):
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
        # Only set world_text if it's not already set
        if not ctx.state.world_text:
            # Use the LLM client from dependencies
            ctx.state.world_text = await ctx.deps.llm_client.generate_text(
                "Generate a noun like 'World'"
            )
        
        # Add a small delay to simulate processing
        await asyncio.sleep(0.2)
        
        return CombineNode()


@dataclass
class CombineNode(BaseNode[MyState, GraphDependencies, str]):
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
        ctx.state.combined_text = f"{ctx.state.hello_text} {ctx.state.world_text}!"
        
        # Add a small delay to simulate processing
        await asyncio.sleep(0.15)
        
        return PrintNode()


@dataclass
class PrintNode(BaseNode[MyState, GraphDependencies, str]):
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
        # Add a small delay to simulate processing
        await asyncio.sleep(0.05)
        
        return End(ctx.state.combined_text) 