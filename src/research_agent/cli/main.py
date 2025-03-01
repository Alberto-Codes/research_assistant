"""
Main command-line interface for Research Agent.

This module provides the main entry point for the Research Agent CLI,
coordinating all available commands.

DEPRECATED: This module is kept for backward compatibility.
Please use the top-level main.py module instead.
"""

import argparse
import asyncio
import logging
import sys
import warnings
from typing import List, Optional

from research_agent.cli.commands.gemini import add_gemini_command
from research_agent.cli.commands.ingest import add_ingest_command
from research_agent.core.logging_config import configure_logging

# Show deprecation warning
warnings.warn(
    "The research_agent.cli.main module is deprecated. "
    "Please use the top-level main module instead.",
    DeprecationWarning,
    stacklevel=2,
)


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser with all available commands.

    Returns:
        An ArgumentParser instance with all commands and arguments defined.
    """
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Research Agent - AI Research Assistant",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run", required=True)

    # Add all available commands
    add_gemini_command(subparsers)
    add_ingest_command(subparsers)

    # Add common arguments to the main parser
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Write logs to a file instead of stdout",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix to add to LLM responses",
    )

    return parser


async def main_async(args: Optional[List[str]] = None) -> int:
    """
    Main asynchronous function that parses arguments and runs the appropriate command.

    Args:
        args: Command line arguments to parse. If None, sys.argv[1:] is used.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Parse command line arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Configure logging
    configure_logging(
        log_level=parsed_args.log_level,
        log_file=parsed_args.log_file,
    )

    # Get the handler for the specified command
    command_handlers = {
        "gemini": "research_agent.cli.commands.gemini.run_gemini_command",
        "ingest": "research_agent.cli.commands.ingest.run_ingest_command",
    }

    handler_path = command_handlers.get(parsed_args.command)
    if not handler_path:
        parser.print_help()
        return 1

    # Import the handler dynamically
    module_path, func_name = handler_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[func_name])
    command_handler = getattr(module, func_name)

    # Run the command
    try:
        return await command_handler(parsed_args)
    except Exception as e:
        logging.error(f"Error executing command: {e}", exc_info=True)
        return 1


def cli_entry() -> None:
    """
    Entry point for the CLI.
    """
    # Set up asyncio for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the main function and exit with its return code
    exit_code = asyncio.run(main_async())
    sys.exit(exit_code)


if __name__ == "__main__":
    cli_entry()
