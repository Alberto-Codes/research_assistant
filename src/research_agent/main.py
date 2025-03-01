"""
Main entry point for the Research Agent application.

This module serves as the primary entry point for the research_agent package,
providing command-line argument parsing and dispatching to the
appropriate interface (CLI or Streamlit UI).
"""

import argparse
import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Import CLI command handlers
from research_agent.cli.commands.gemini import add_gemini_command, run_gemini_command
from research_agent.cli.commands.ingest import add_ingest_command, run_ingest_command
from research_agent.core.logging_config import configure_logging


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser for all application interfaces.

    Returns:
        An ArgumentParser instance with all interfaces and commands defined.
    """
    # Create the main parser
    parser = argparse.ArgumentParser(
        description="Research Agent - AI Research Assistant",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Create main subparsers for interface
    subparsers = parser.add_subparsers(
        dest="interface",
        help="Interface to use",
        required=True,
    )

    # CLI interface
    cli_parser = subparsers.add_parser(
        "cli",
        help="Run the command-line interface",
    )

    # Create CLI command subparsers
    cli_subparsers = cli_parser.add_subparsers(
        dest="command",
        help="CLI command to run",
        required=True,
    )

    # Add all available CLI commands
    add_gemini_command(cli_subparsers)
    add_ingest_command(cli_subparsers)

    # Add common arguments to the CLI parser
    cli_parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help="Prefix to add to LLM responses",
    )

    # Streamlit interface
    streamlit_parser = subparsers.add_parser(
        "ui",
        help="Run the Streamlit user interface",
    )
    streamlit_parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run the Streamlit UI on",
    )

    # Add logging arguments to all parsers
    for p in [parser, cli_parser, streamlit_parser]:
        add_logging_arguments(p)

    return parser


def add_logging_arguments(parser: argparse.ArgumentParser) -> None:
    """Add logging-related command-line arguments to a parser.

    Args:
        parser: The argparse parser or subparser to add arguments to.
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


def get_streamlit_script_path() -> str:
    """
    Get the path to the main Streamlit application.

    Returns:
        The path to the Streamlit application script.
    """
    # Get the directory of the research_agent package
    package_dir = Path(__file__).parent.resolve()

    # Look for app.py first, then fall back to gemini_chat.py
    streamlit_dir = package_dir / "ui" / "streamlit"
    app_path = streamlit_dir / "app.py"
    gemini_chat_path = streamlit_dir / "gemini_chat.py"

    if app_path.exists():
        return str(app_path)
    elif gemini_chat_path.exists():
        return str(gemini_chat_path)
    else:
        # Find any Python file in the streamlit directory
        py_files = list(streamlit_dir.glob("*.py"))
        if py_files:
            return str(py_files[0])

        raise FileNotFoundError(f"No Streamlit application found in {streamlit_dir}")


async def run_cli_async(args: argparse.Namespace) -> int:
    """
    Run the CLI interface asynchronously.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Map of commands to their handler functions
    command_handlers = {
        "gemini": run_gemini_command,
        "ingest": run_ingest_command,
    }

    # Get the handler for the command
    handler = command_handlers.get(args.command)
    if not handler:
        logging.error(f"Unknown command: {args.command}")
        return 1

    # Run the command
    try:
        return await handler(args)
    except Exception as e:
        logging.error(f"Error executing command: {e}", exc_info=True)
        return 1


def run_streamlit(args: argparse.Namespace) -> int:
    """
    Run the Streamlit interface.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    try:
        # Get the path to the Streamlit application
        app_path = get_streamlit_script_path()

        # Build the command to run Streamlit
        cmd = [
            "streamlit",
            "run",
            app_path,
            "--server.port",
            str(args.port),
        ]

        # Run Streamlit
        subprocess.run(cmd, check=True)
        return 0
    except FileNotFoundError as e:
        logging.error(f"Streamlit application not found: {e}")
        return 1
    except subprocess.CalledProcessError as e:
        logging.error(f"Error running Streamlit: {e}")
        return 1
    except KeyboardInterrupt:
        logging.info("Streamlit server stopped.")
        return 0


async def main_async(args: Optional[List[str]] = None) -> int:
    """
    Main async entry point that processes arguments and dispatches to the appropriate interface.

    Args:
        args: Command line arguments. If None, sys.argv[1:] is used.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Parse arguments
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Configure logging
    configure_logging(log_level=parsed_args.log_level, log_file=parsed_args.log_file)

    # Dispatch to the appropriate interface
    if parsed_args.interface == "cli":
        return await run_cli_async(parsed_args)
    elif parsed_args.interface == "ui":
        return run_streamlit(parsed_args)
    else:
        logging.error(f"Unknown interface: {parsed_args.interface}")
        return 1


def main() -> None:
    """
    Main synchronous entry point for the application.
    """
    # Set up asyncio for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the async main function
    exit_code = asyncio.run(main_async())
    sys.exit(exit_code)


def cli_entry() -> None:
    """
    Entry point function for console_scripts.
    This is used when the package is installed and the 'research_agent' command is invoked.
    """
    main()


if __name__ == "__main__":
    main()
