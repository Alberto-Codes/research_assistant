"""
Command-line interface for the Research Agent application.

This module defines the command-line interface for the Research Agent,
providing a command for running the Gemini AI agent.
"""

import argparse
import asyncio
import logging
import sys
from typing import List, Optional

from research_agent.api.services import generate_ai_response
from research_agent.core.logging_config import configure_logging
from research_agent.core.state import MyState


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.

    Returns:
        An ArgumentParser instance with all commands and arguments defined.
    """
    # Create the main parser
    parser = argparse.ArgumentParser(description="Research Agent - AI Assistant powered by Gemini")
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)

    # Gemini command
    gemini_parser = subparsers.add_parser("gemini", help="Run the Gemini AI agent")
    gemini_parser.add_argument(
        "--prompt", type=str, required=True, help="Prompt to send to the Gemini model"
    )
    gemini_parser.add_argument(
        "--project-id",
        type=str,
        help="Google Cloud project ID (optional, will detect from environment if not provided)",
    )

    # Add logging arguments to gemini command
    add_logging_args(gemini_parser)

    return parser


def add_logging_args(parser: argparse.ArgumentParser) -> None:
    """
    Add logging-related arguments to a parser.

    Args:
        parser: The parser to add arguments to.
    """
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Optional log file path",
    )


async def gemini_command(args: argparse.Namespace) -> None:
    """
    Run the Gemini AI agent.

    Args:
        args: Command-line arguments.
    """
    logger = logging.getLogger(__name__)
    prompt = args.prompt
    project_id = args.project_id

    logger.info("Running Gemini agent with prompt: '%s'", prompt)

    try:
        # Call the service function to generate a response
        state = await generate_ai_response(prompt, project_id=project_id)

        # Display the results
        print(f"\nUser prompt: {state.user_prompt}")
        print(f"AI response: {state.ai_response}")
        print(f"Generation time: {state.ai_generation_time:.3f} seconds")
        print(f"Total time: {state.total_time:.3f} seconds")

    except Exception as e:
        logger.error("Error running Gemini agent: %s", e)
        print(f"Error: {e}")
        sys.exit(1)


async def main_async(args: Optional[List[str]] = None) -> None:
    """
    Main entry point for the CLI (async version).

    Args:
        args: Command-line arguments. If None, sys.argv is used.
    """
    # Parse arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Configure logging based on command-line arguments
    configure_logging(log_level=parsed_args.log_level, log_file=parsed_args.log_file)

    # Run the appropriate command
    if parsed_args.command == "gemini":
        await gemini_command(parsed_args)
    else:
        parser.print_help()


def cli_entry() -> None:
    """
    Main entry point for the CLI.

    This function is used as the entry point in setup.py.
    """
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli_entry()
