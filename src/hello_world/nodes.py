"""
Node definitions for the Hello World graph.
"""

from __future__ import annotations
from dataclasses import dataclass
import time
from typing import Any
import asyncio

from pydantic_graph import BaseNode, End, GraphRunContext

from .state import MyState
from .dependencies import GraphDependencies


@dataclass
class HelloNode(BaseNode[MyState, GraphDependencies, str]):
    """First node that generates the 'Hello' text."""
    
    async def run(self, ctx: GraphRunContext) -> WorldNode:
        """Set the hello_text in the state and return the next node."""
        # Measure processing time
        start_time = time.time()
        
        # Only set hello_text if it's not already set
        if not ctx.state.hello_text:
            # Use the LLM client from dependencies
            ctx.state.hello_text = await ctx.deps.llm_client.generate_text("Generate a greeting word like 'Hello'")
        
        # Add a small delay to simulate processing
        await asyncio.sleep(0.1)
        
        # Calculate processing time
        process_time = time.time() - start_time
        print(f"Generated: {ctx.state.hello_text} (took {process_time:.3f}s)")
        
        return WorldNode()


@dataclass
class WorldNode(BaseNode[MyState, GraphDependencies, str]):
    """Second node that generates the 'World' text."""
    
    async def run(self, ctx: GraphRunContext) -> CombineNode:
        """Set the world_text in the state and return the next node."""
        # Measure processing time
        start_time = time.time()
        
        # Only set world_text if it's not already set
        if not ctx.state.world_text:
            # Use the LLM client from dependencies
            ctx.state.world_text = await ctx.deps.llm_client.generate_text("Generate a noun like 'World'")
        
        # Add a small delay to simulate processing
        await asyncio.sleep(0.2)
        
        # Calculate processing time
        process_time = time.time() - start_time
        print(f"Generated: {ctx.state.world_text} (took {process_time:.3f}s)")
        
        return CombineNode()


@dataclass
class CombineNode(BaseNode[MyState, GraphDependencies, str]):
    """Third node that combines the hello and world texts."""
    
    async def run(self, ctx: GraphRunContext) -> PrintNode:
        """Combine the hello_text and world_text and return the next node."""
        # Measure processing time
        start_time = time.time()
        
        ctx.state.combined_text = f"{ctx.state.hello_text} {ctx.state.world_text}!"
        
        # Add a small delay to simulate processing
        await asyncio.sleep(0.15)
        
        # Calculate processing time
        process_time = time.time() - start_time
        print(f"Combined: {ctx.state.combined_text} (took {process_time:.3f}s)")
        
        return PrintNode()


@dataclass
class PrintNode(BaseNode[MyState, GraphDependencies, str]):
    """Final node that prints the combined text and ends the graph."""
    
    async def run(self, ctx: GraphRunContext) -> End[str]:
        """Print the final output and end the graph execution."""
        # Measure processing time
        start_time = time.time()
        
        # Add a small delay to simulate processing
        await asyncio.sleep(0.05)
        
        # Calculate processing time
        process_time = time.time() - start_time
        print(f"Final output: {ctx.state.combined_text} (took {process_time:.3f}s)")
        
        return End(ctx.state.combined_text) 