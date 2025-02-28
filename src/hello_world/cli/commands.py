"""
Command-line interface for the Hello World Pydantic Graph example.

This module provides the command-line interface for running the Hello World graph
example. It handles command-line arguments, uses the services layer to execute the graph,
and displays the results.
"""

import asyncio
import argparse
import sys
import warnings
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

from hello_world.api.services import generate_hello_world, generate_ai_response
from hello_world.core.state import MyState

def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        The parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Hello World Pydantic Graph example."
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Hello World command
    hello_parser = subparsers.add_parser("hello", help="Run the Hello World graph")
    hello_parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix to add to the generated text"
    )
    hello_parser.add_argument(
        "--use-custom-llm",
        action="store_true",
        help="Use the custom LLM client instead of the mock one"
    )
    
    # Gemini agent command
    gemini_parser = subparsers.add_parser("gemini", help="Run the Gemini AI agent")
    gemini_parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="User prompt to send to the Gemini model"
    )
    gemini_parser.add_argument(
        "--project-id",
        type=str,
        default=None,
        help="Google Cloud project ID (optional, will try to detect from environment if not provided)"
    )
    gemini_parser.add_argument(
        "--use-mock-gemini",
        action="store_true",
        help="[DEPRECATED] Use the mock Gemini client (for local testing). "
             "This flag is deprecated and will be removed in a future version."
    )
    
    return parser.parse_args()

def display_results(state: MyState) -> None:
    """Display the results of a graph run.
    
    Args:
        state: The final state after running the graph.
    """
    print("\n=== Execution Results ===")
    
    # Display differently depending on whether we're showing AI results or Hello World results
    if state.ai_response:
        print(f"User Prompt: {state.user_prompt}")
        print(f"AI Response: {state.ai_response}")
        print(f"Generation Time: {state.ai_generation_time:.3f}s")
        print(f"Total Time: {state.total_time:.3f}s")
    else:
        print(f"Hello Text: {state.hello_text}")
        print(f"World Text: {state.world_text}")
        print(f"Combined Text: {state.combined_text}")
        print(f"Hello Gen Time: {state.hello_generation_time:.3f}s")
        print(f"World Gen Time: {state.world_generation_time:.3f}s")
        print(f"Combine Time: {state.combine_generation_time:.3f}s")
        print(f"Total Time: {state.total_time:.3f}s")
    
    if hasattr(state, 'node_execution_history') and state.node_execution_history:
        print("\nNode Execution History:")
        for i, item in enumerate(state.node_execution_history):
            print(f"  {i+1}. {item}")
    
    print("==========================\n")

async def main() -> None:
    """Main entry point for the CLI.
    
    This function parses arguments, runs the appropriate graph,
    and displays the results.
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    try:
        if args.command == "gemini":
            # Check for deprecated mock flag
            use_mock_gemini = False
            if hasattr(args, 'use_mock_gemini') and args.use_mock_gemini:
                warnings.warn(
                    "The --use-mock-gemini flag is deprecated and will be removed in a future version. "
                    "For testing, use pytest fixtures instead.",
                    DeprecationWarning
                )
                print("\nWARNING: The --use-mock-gemini flag is deprecated. For proper testing, "
                      "use pytest fixtures and mocks instead.")
                use_mock_gemini = True
            
            # Run the Gemini agent
            state = await generate_ai_response(
                user_prompt=args.prompt,
                project_id=args.project_id,
                use_mock_gemini=use_mock_gemini
            )
        else:  # Default to hello command
            # Run the Hello World graph
            state = await generate_hello_world(
                use_custom_llm=args.use_custom_llm if hasattr(args, 'use_custom_llm') else False,
                prefix=args.prefix if hasattr(args, 'prefix') else None
            )
        
        # Display the results
        display_results(state)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def cli_entry() -> None:
    """Entry point for the console script."""
    asyncio.run(main())

if __name__ == "__main__":
    cli_entry()
