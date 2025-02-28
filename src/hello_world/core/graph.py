"""
Graph definition for the Hello World example.

This module defines the graph structure for the Hello World application,
including the nodes and their dependencies.
"""

from __future__ import annotations
import asyncio
import datetime
import logging
from typing import Dict, List, Tuple, Any, Optional

from pydantic_graph import Graph, GraphRunResult, GraphError

from hello_world.core.nodes import HelloNode, WorldNode, CombineNode, PrintNode
from hello_world.core.state import MyState
from hello_world.core.dependencies import HelloWorldDependencies


# Set up logging
logger = logging.getLogger(__name__)


def get_hello_world_graph(dependencies: Optional[HelloWorldDependencies] = None) -> Graph:
    """
    Get the Hello World graph with optional dependencies.
    
    Args:
        dependencies: Optional dependencies to inject into the graph. If not provided,
                      default dependencies will be used.
                      
    Returns:
        A configured Graph instance.
    """
    # Create default dependencies if none are provided
    deps = dependencies or HelloWorldDependencies()
    
    # Define our graph with nodes and dependencies
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
        
    Raises:
        GraphError: If there's an error during graph execution
        ValueError: If invalid inputs are provided
    """
    try:
        # Create a new state if none is provided
        if initial_state is not None and not isinstance(initial_state, MyState):
            raise ValueError("initial_state must be an instance of MyState or None")
            
        state = initial_state or MyState()
        
        # Create dependencies if none are provided
        deps = dependencies or HelloWorldDependencies()
        
        # Get the graph
        graph = get_hello_world_graph()
        
        # Run the graph with state and deps
        logger.debug("Starting graph execution with state: %s", state)
        graph_result = await graph.run(HelloNode(), state=state, deps=deps)
        logger.debug("Graph execution completed successfully")
        
        return graph_result.output, graph_result.state, graph_result.history
    
    except GraphError as e:
        logger.error("Graph execution failed: %s", str(e))
        raise
    except Exception as e:
        logger.error("Unexpected error during graph execution: %s", str(e))
        raise


def display_results(graph_result: GraphRunResult) -> None:
    """
    Display the results of a graph run in a nice format.
    
    Args:
        graph_result: The GraphRunResult object from a graph run
    """
    if not isinstance(graph_result, GraphRunResult):
        raise TypeError("graph_result must be a GraphRunResult instance")
        
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n=== Graph Execution Results ===")
    print(f"Time: {current_time}")
    print(f"Result: {graph_result.output}")
    print(f"Final state: {graph_result.state}")
    
    print("\nNode execution history:")
    for i, item in enumerate(graph_result.history):
        print(f"  {i+1}. {item.__class__.__name__}")
    print("==============================\n") 