"""
Main entry point for the Research Agent application.

This module serves as the main entry point for the application,
providing command-line argument parsing and dispatching to the
appropriate interface (CLI or Streamlit).
"""

# Standard library imports
import argparse
import asyncio
import logging
import os
import subprocess
import sys
from typing import List, Optional

from research_agent.cli.commands.gemini import add_gemini_command
from research_agent.cli.commands.ingest import add_ingest_command

# Import local modules
from research_agent.core.logging_config import configure_logging

# Import third-party libraries
# No third-party imports directly in main.py


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments for the application.

    Args:
        args: Command-line arguments to parse. Uses sys.argv if None.

    Returns:
        Parsed arguments.
    """
    # Check if first argument is a direct command (gemini, ingest)
    # This handles the case when the script is called as: research_agent ingest ...
    direct_commands = {"gemini", "ingest"}
    is_direct_command = args and len(args) > 0 and args[0] in direct_commands

    if is_direct_command:
        # Create a parser for direct command invocation
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

        # Parse the arguments
        parsed_args = parser.parse_args(args)
        # Add an interface attribute for compatibility with the rest of the code
        parsed_args.interface = "cli"
        return parsed_args

    # Standard interface-based parsing (cli/ui)
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

    return parser.parse_args(args)


def add_logging_arguments(parser):
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


async def run_cli_async(args: argparse.Namespace) -> int:
    """
    Run the CLI interface asynchronously.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Get the handler for the specified command
    command_handlers = {
        "gemini": "research_agent.cli.commands.gemini.run_gemini_command",
        "ingest": "research_agent.cli.commands.ingest.run_ingest_command",
    }

    handler_path = command_handlers.get(args.command)
    if not handler_path:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        return 1

    # Import the handler dynamically
    module_path, func_name = handler_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[func_name])
    command_handler = getattr(module, func_name)

    # Run the command
    try:
        return await command_handler(args)
    except Exception as e:
        logging.error(f"Error executing command: {e}", exc_info=True)
        return 1


def run_cli(args: argparse.Namespace) -> None:
    """
    Run the CLI interface.

    Args:
        args: Parsed command-line arguments.
    """
    # Set up asyncio for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the async CLI function and exit with its return code
    exit_code = asyncio.run(run_cli_async(args))
    sys.exit(exit_code)


def run_streamlit(args: argparse.Namespace) -> None:
    """
    Run the Streamlit interface.

    Args:
        args: Parsed command-line arguments.
    """
    # Get the path to the Streamlit app
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "research_agent", "ui", "streamlit", "app.py")

    # Check if the file exists
    if not os.path.exists(app_path):
        print(f"Error: Streamlit app file not found at: {app_path}", file=sys.stderr)
        print("Looking for Streamlit files in the project...", file=sys.stderr)

        # Try to find any .py files in the streamlit directory
        streamlit_dir = os.path.join(current_dir, "research_agent", "ui", "streamlit")
        if os.path.exists(streamlit_dir):
            py_files = [
                f for f in os.listdir(streamlit_dir) if f.endswith(".py") and f != "__init__.py"
            ]
            if py_files:
                print(f"Found potential Streamlit files: {', '.join(py_files)}", file=sys.stderr)
                # Prefer app.py if it exists, otherwise fall back to gemini_chat.py
                if "app.py" in py_files:
                    app_path = os.path.join(streamlit_dir, "app.py")
                elif "gemini_chat.py" in py_files:
                    app_path = os.path.join(streamlit_dir, "gemini_chat.py")
                else:
                    app_path = os.path.join(streamlit_dir, py_files[0])
                print(f"Using: {app_path}", file=sys.stderr)
            else:
                print("No Python files found in the Streamlit directory.", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Streamlit directory not found at: {streamlit_dir}", file=sys.stderr)
            sys.exit(1)

    # Run Streamlit using subprocess
    cmd = [
        "streamlit",
        "run",
        app_path,
        "--server.port",
        str(getattr(args, "port", 8501)),
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Streamlit server stopped.")


def main() -> None:
    """Main entry point for the application."""
    args = parse_args()

    # Configure logging based on command-line arguments
    configure_logging(log_level=args.log_level, log_file=args.log_file)

    if args.interface == "cli":
        run_cli(args)
    elif args.interface == "ui":
        run_streamlit(args)
    else:
        print(f"Unknown interface: {args.interface}", file=sys.stderr)
        sys.exit(1)


# Function to be used as a direct entry point for the CLI
def cli_main():
    """Entry point for the CLI when invoked directly as 'research_agent'."""
    # Set up asyncio for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    args = parse_args()
    configure_logging(log_level=args.log_level, log_file=args.log_file)

    # Run the CLI
    if args.interface == "cli":
        exit_code = asyncio.run(run_cli_async(args))
        sys.exit(exit_code)
    else:
        print("Invalid command for CLI entry point", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
