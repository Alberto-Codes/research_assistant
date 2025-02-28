"""
Services for the Hello World application.

This module provides service functions that can be used by different interfaces
(CLI, Streamlit, FastAPI) to access the core functionality of the application.
"""
from typing import Optional, Tuple, List, Any

from hello_world.core.dependencies import HelloWorldDependencies
from hello_world.core.graph import get_hello_world_graph, run_graph
from hello_world.core.state import MyState
from pydantic_graph import Graph, GraphDeps
from concurrent.futures import ProcessPoolExecutor
from pydantic_graph.nodes import BaseNode, GraphRunContext
from dataclasses import dataclass


async def generate_hello_world(use_custom_llm: bool = False, prefix: Optional[str] = None) -> MyState:
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
    output, final_state, history = await run_graph(initial_state=MyState(), dependencies=dependencies)
    return final_state


def get_hello_world_graph() -> Graph:
    """
    Get the Hello World graph.
    
    Returns:
        A configured Graph instance.
    """
    # Define our graph with nodes only (no dependencies in constructor)
    graph = Graph(
        nodes=[HelloNode, WorldNode, CombineNode, PrintNode],
    )
    
    return graph


async def run_graph(initial_state: Optional[MyState] = None, 
                   dependencies: Optional[HelloWorldDependencies] = None) -> Tuple[str, MyState, List[Any]]:
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


@dataclass
class HelloNode(BaseNode[MyState, HelloWorldDependencies]):
    async def run(self, ctx: GraphRunContext[MyState, HelloWorldDependencies]) -> WorldNode:
        # Access dependencies via ctx.deps
        llm_client = ctx.deps.llm_client
        prefix = ctx.deps.prefix
        
        # Use dependencies to do work
        # ... 