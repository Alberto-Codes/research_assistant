"""
Command-line entry point for the Research Agent application.

This module provides the command-line entry point for running the
Research Agent's Gemini chat interface.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_streamlit_script_path(script_name: str) -> str:
    """
    Get the absolute path to a Streamlit script file.

    Args:
        script_name: The name of the script file without the path.

    Returns:
        The absolute path to the script file.
    """
    # Get the directory of this file
    current_dir = Path(__file__).parent.resolve()

    # Construct the path to the Streamlit script
    streamlit_dir = current_dir / "streamlit"
    script_path = streamlit_dir / script_name

    # Check if the file exists
    if not script_path.exists():
        raise FileNotFoundError(f"Could not find Streamlit script at {script_path}")

    return str(script_path)


def run_gemini_chat():
    """Run the Gemini chat Streamlit app."""
    streamlit_path = get_streamlit_script_path("gemini_chat.py")
    subprocess.run(["streamlit", "run", streamlit_path])


def main():
    """Command-line entry point for the Research Agent application.

    This function parses command-line arguments and runs the
    Gemini chat Streamlit application.
    """
    parser = argparse.ArgumentParser(description="Run the Research Agent's Gemini chat interface.")

    # Parse the arguments
    args = parser.parse_args()

    # Run the Gemini chat application
    run_gemini_chat()


if __name__ == "__main__":
    main()
