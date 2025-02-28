"""
Main entry point for the Hello World Pydantic Graph example.
"""

import asyncio
import argparse
import sys
from typing import Dict, Any

from hello_world import run_graph
from hello_world.state import MyState
from hello_world.graph import display_results
from pydantic_graph import GraphRunResult


async def main() -> None:
    """Run the Hello World graph and display the results."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the Hello World graph example")
    parser.add_argument('--hello', type=str, default="Hello", help="Text to use for 'Hello'")
    parser.add_argument('--world', type=str, default="World", help="Text to use for 'World'")
    args = parser.parse_args()
    
    # Create initial state with custom hello/world values if provided
    initial_state = MyState()
    if args.hello != "Hello":
        initial_state.hello_text = args.hello
    if args.world != "World":
        initial_state.world_text = args.world
        
    # Run the graph
    graph_result = await run_graph(initial_state)
    
    # Import the display_results function from graph.py
    from hello_world.graph import display_results
    
    # Convert tuple result to GraphRunResult for display
    class GraphResultAdapter:
        def __init__(self, output, state, history):
            self.output = output
            self.state = state
            self.history = history
    
    # Adapt the output from run_graph to display_results
    output, state, history = graph_result
    adapter = GraphResultAdapter(output, state, history)
    
    # Display the results using the function from graph.py
    display_results(adapter)


def cli_entry() -> None:
    """Entry point for the console script."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_entry()
