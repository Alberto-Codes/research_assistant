"""
Gemini command implementation.

This module defines the gemini command for the Research Agent CLI,
which allows running the Gemini AI agent with a specified prompt.
"""

import argparse
import asyncio
import logging
from typing import Any, Dict, Optional

from research_agent.api.services import generate_ai_response
from research_agent.core.state import MyState


def add_gemini_command(subparsers: "argparse._SubParsersAction") -> None:
    """
    Add the gemini command to the CLI subparsers.

    Args:
        subparsers: The subparsers object to add the command to.
    """
    gemini_parser = subparsers.add_parser(
        "gemini",
        help="Run the Gemini AI agent with a prompt",
        description="Run the Gemini AI agent and get a response to your prompt",
    )

    gemini_parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Prompt to send to the Gemini model",
    )

    gemini_parser.add_argument(
        "--project-id",
        type=str,
        help="Google Cloud project ID (optional, will detect from environment if not provided)",
    )

    # Add advanced model options
    gemini_parser.add_argument(
        "--model",
        type=str,
        default="gemini-1.5-pro",
        help="Gemini model to use",
    )

    gemini_parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for generating responses (0.0-1.0)",
    )


async def run_gemini_command(args: argparse.Namespace) -> int:
    """
    Run the gemini command with the specified arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    logger = logging.getLogger(__name__)
    logger.info("Running Gemini AI agent")

    # Extract parameters from args
    prompt = args.prompt
    project_id = args.project_id

    # Generate AI response using the correct function signature
    try:
        logger.info(f"Sending prompt to Gemini: {prompt}")
        state = await generate_ai_response(user_prompt=prompt, project_id=project_id)

        # Print the response
        print("\nGemini Response:")
        print("=" * 80)
        print(state.ai_response if hasattr(state, "ai_response") else state)
        print("=" * 80)

        logger.info("Successfully generated response from Gemini")
        return 0
    except Exception as e:
        logger.error(f"Failed to generate response: {e}", exc_info=True)
        return 1
