"""
Main entry point for the Hello World Pydantic Graph example.
"""

import asyncio
import argparse
import sys
from typing import Dict, Any, Optional

from hello_world import run_graph
from hello_world.state import MyState
from hello_world.graph import display_results
from hello_world.dependencies import GraphDependencies, LLMClient
from pydantic_graph import GraphRunResult


class CustomLLMClient:
    """
    A custom LLM client implementation that could be replaced with a real API client.
    
    This is an example showing how you could swap in different LLM implementations
    through dependency injection.
    """
    
    def __init__(self, prefix: str = ""):
        """Initialize the custom LLM client with an optional prefix."""
        self.prefix = prefix
    
    async def generate_text(self, prompt: str) -> str:
        """Generate text based on the prompt, adding the custom prefix if set."""
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


async def main() -> None:
    """Run the Hello World graph and display the results."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Run the Hello World graph example")
    parser.add_argument('--hello', type=str, default="", help="Text to use for 'Hello'")
    parser.add_argument('--world', type=str, default="", help="Text to use for 'World'")
    parser.add_argument('--prefix', type=str, default="", help="Prefix to add to LLM responses")
    parser.add_argument('--use-custom-llm', action='store_true', help="Use the custom LLM client")
    args = parser.parse_args()
    
    # Create initial state with custom hello/world values if provided
    initial_state = MyState()
    if args.hello:
        initial_state.hello_text = args.hello
    if args.world:
        initial_state.world_text = args.world
    
    # Create dependencies with custom LLM client if specified
    dependencies = None
    if args.use_custom_llm:
        # Create an instance of our custom LLM client
        custom_llm = CustomLLMClient(prefix=args.prefix)
        dependencies = GraphDependencies(llm_client=custom_llm)
        
    # Run the graph
    graph_result = await run_graph(initial_state, dependencies)
    
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
