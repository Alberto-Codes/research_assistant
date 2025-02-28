"""
Graph definition and runner for the Hello World example.
"""

from __future__ import annotations
import asyncio
import datetime
from typing import Dict, List, Tuple, Any, Optional

from pydantic_graph import Graph, GraphRunResult

from .nodes import HelloNode, WorldNode, CombineNode, PrintNode
from .state import MyState
from .dependencies import GraphDependencies


# Define our graph
hello_world_graph = Graph(nodes=[HelloNode, WorldNode, CombineNode, PrintNode])


async def run_graph(initial_state: Optional[MyState] = None, 
                   dependencies: Optional[GraphDependencies] = None) -> Tuple[str, MyState, List[Any]]:
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
    deps = dependencies or GraphDependencies()
    
    # Run the graph and get the GraphRunResult object
    graph_result = await hello_world_graph.run(HelloNode(), state=state, deps=deps)
    
    return graph_result.output, graph_result.state, graph_result.history


def display_results(graph_result: GraphRunResult) -> None:
    """
    Display the results of a graph run in a nice format.
    
    Args:
        graph_result: The GraphRunResult object from a graph run
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n=== Graph Execution Results ===")
    print(f"Time: {current_time}")
    print(f"Result: {graph_result.output}")
    print(f"Final state: {graph_result.state}")
    
    print("\nNode execution history:")
    for i, item in enumerate(graph_result.history):
        print(f"  {i+1}. {item.__class__.__name__}")
    print("==============================\n") 