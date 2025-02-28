"""
Command-line interface for the Hello World Pydantic Graph example.

This module provides the command-line interface for running the Hello World graph
example. It handles command-line arguments, uses the services layer to execute the graph,
and displays the results.
"""

import asyncio
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

from hello_world.api.services import generate_hello_world
from hello_world.core.state import MyState

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run the Hello World graph example")
    parser.add_argument('--prefix', type=str, default="", help="Prefix to add to LLM responses")
    parser.add_argument('--use-custom-llm', action='store_true', help="Use the custom LLM client")
    return parser.parse_args()

def display_results(state: MyState) -> None:
    """
    Display the results of running the graph.
    
    Args:
        state: The final state after running the graph.
    """
    print(f"\nExecution results ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):")
    print(f"Generated: {state.hello_text} (took {state.hello_generation_time:.3f}s)")
    print(f"Generated: {state.world_text} (took {state.world_generation_time:.3f}s)")
    print(f"Combined: {state.combined_text} (took {state.combine_generation_time:.3f}s)")
    print(f"Final output: {state.combined_text} (took {state.total_time:.3f}s)")
    
    print("\nState:")
    print(f"  hello_text: {state.hello_text}")
    print(f"  world_text: {state.world_text}")
    print(f"  combined_text: {state.combined_text}")
    
    print("\nNode execution history:")
    for entry in state.node_execution_history:
        print(f"  - {entry}")

async def main() -> None:
    """
    Run the Hello World graph and display the results.
    
    This function is the main entry point for the CLI application. It parses
    command-line arguments, calls the service layer, and displays the results.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Use the services layer to generate hello world
    final_state = await generate_hello_world(
        use_custom_llm=args.use_custom_llm,
        prefix=args.prefix if args.prefix else None
    )
    
    # Display the results
    display_results(final_state)

def cli_entry() -> None:
    """
    Entry point for the console script.
    
    This function is used as the entry point in setup.py for the
    console script. It runs the main async function.
    """
    asyncio.run(main())

if __name__ == "__main__":
    cli_entry()
