"""
Main entry point for the Hello World Pydantic Graph example.

This module provides the command-line interface for running the Hello World graph
example. It handles command-line arguments, sets up dependencies, runs the graph,
and displays the results.
"""

import asyncio
import argparse
import sys
from typing import Dict, Any, Optional, Tuple, List, NamedTuple
from dataclasses import dataclass

from hello_world import run_graph
from hello_world.state import MyState
from hello_world.graph import display_results
from hello_world.dependencies import GraphDependencies, LLMClient
from pydantic_graph import GraphRunResult


class CustomLLMClient:
    """A custom LLM client implementation that could be replaced with a real API client.
    
    This is an example showing how you could swap in different LLM implementations
    through dependency injection. In a real application, this would be replaced
    with a client that connects to an actual LLM API.
    
    Attributes:
        prefix: An optional prefix to add to each generated response.
    """
    
    def __init__(self, prefix: str = ""):
        """Initialize the custom LLM client with an optional prefix.
        
        Args:
            prefix: A prefix string to add to all generated responses.
        """
        self.prefix = prefix
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text based on the prompt, adding the custom prefix if set.
        
        Args:
            prompt: The text prompt to generate from.
            
        Returns:
            The generated text, with prefix if set.
        """
        # In a real implementation, this would call an LLM API
        if "hello" in prompt.lower():
            result = "Hello"
        elif "world" in prompt.lower():
            result = "World"
        else:
            result = "Response"
            
        # Add the prefix if one is set
        if self.prefix:
            result = f"{self.prefix} {result}"
            
        return result


@dataclass
class GraphResultAdapter:
    """Adapter to make run_graph output compatible with display_results.
    
    Attributes:
        output: The final output string from the graph.
        state: The final state object.
        history: The execution history.
    """
    output: str
    state: MyState
    history: List[Any]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Run the Hello World graph example")
    parser.add_argument('--hello', type=str, default="", help="Text to use for 'Hello'")
    parser.add_argument('--world', type=str, default="", help="Text to use for 'World'")
    parser.add_argument('--prefix', type=str, default="", help="Prefix to add to LLM responses")
    parser.add_argument('--use-custom-llm', action='store_true', help="Use the custom LLM client")
    return parser.parse_args()


def create_initial_state(args: argparse.Namespace) -> MyState:
    """Create the initial state from command-line arguments.
    
    Args:
        args: The parsed command-line arguments.
        
    Returns:
        A MyState instance initialized with values from args.
    """
    initial_state = MyState()
    if args.hello:
        initial_state.hello_text = args.hello
    if args.world:
        initial_state.world_text = args.world
    return initial_state


def create_dependencies(args: argparse.Namespace) -> Optional[GraphDependencies]:
    """Create dependencies based on command-line arguments.
    
    Args:
        args: The parsed command-line arguments.
        
    Returns:
        A GraphDependencies instance if custom LLM is requested, None otherwise.
    """
    if not args.use_custom_llm:
        return None
        
    # Create an instance of our custom LLM client
    custom_llm = CustomLLMClient(prefix=args.prefix)
    return GraphDependencies(llm_client=custom_llm)


async def main() -> None:
    """Run the Hello World graph and display the results.
    
    This function is the main entry point for the application. It parses
    command-line arguments, sets up the initial state and dependencies,
    runs the graph, and displays the results.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Create initial state with custom hello/world values if provided
    initial_state = create_initial_state(args)
    
    # Create dependencies with custom LLM client if specified
    dependencies = create_dependencies(args)
        
    # Run the graph
    output, state, history = await run_graph(initial_state, dependencies)
    
    # Adapt the output from run_graph to display_results
    adapter = GraphResultAdapter(output, state, history)
    
    # Display the results using the function from graph.py
    display_results(adapter)


def cli_entry() -> None:
    """Entry point for the console script.
    
    This function is used as the entry point in setup.py for the
    console script. It runs the main async function.
    """
    asyncio.run(main())


if __name__ == "__main__":
    cli_entry()
