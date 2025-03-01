"""
Main entry point for the Hello World application.

This module serves as the main entry point for the application,
providing command-line argument parsing and dispatching to the
appropriate interface (CLI or Streamlit).
"""

# Standard library imports
import argparse
import os
import subprocess
import sys
from typing import List, Optional

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
    parser = argparse.ArgumentParser(
        description="Hello World Graph Application",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Check if the first argument is 'cli' or 'ui'
    if args and len(args) > 0 and args[0] in ["cli", "ui"]:
        # New-style command-line arguments with subcommands
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
        cli_parser.add_argument(
            "--prefix",
            type=str,
            default="",
            help="Prefix to add to LLM responses",
        )

        # Add logging arguments to both parsers
        for p in [cli_parser]:
            add_logging_arguments(p)

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

        # Add logging arguments
        add_logging_arguments(streamlit_parser)
    else:
        # Old-style command-line arguments (for backward compatibility)
        parser.add_argument(
            "--prefix",
            type=str,
            default="",
            help="Prefix to add to LLM responses",
        )
        # Hidden argument for interface, defaulting to 'cli'
        parser.add_argument(
            "--interface",
            type=str,
            default="cli",
            help=argparse.SUPPRESS,
        )

        # Add logging arguments
        add_logging_arguments(parser)

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


def run_cli(args: argparse.Namespace) -> None:
    """
    Run the CLI interface.

    Args:
        args: Parsed command-line arguments.
    """
    # Import the CLI entry point
    from research_agent.cli.commands import cli_entry

    # Set the args in sys.argv for the CLI to parse
    cli_args = []
    if args.prefix:
        cli_args.extend(["--prefix", args.prefix])

    # Save the original argv
    original_argv = sys.argv.copy()

    try:
        # Replace argv with our args
        sys.argv = [sys.argv[0]] + cli_args

        # Run the CLI
        cli_entry()
    finally:
        # Restore the original argv
        sys.argv = original_argv


def run_streamlit(args: argparse.Namespace) -> None:
    """
    Run the Streamlit interface.

    Args:
        args: Parsed command-line arguments.
    """
    # Get the path to the Streamlit app
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "research_agent", "ui", "streamlit", "app.py")

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


if __name__ == "__main__":
    main()
