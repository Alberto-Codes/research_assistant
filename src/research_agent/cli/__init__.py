"""
Command-line interface package for Research Agent.

This package contains the command-line interface implementation
for the Research Agent application.

Note: The main CLI entry point is now in research_agent.main
"""

# Import commands for convenience
from research_agent.cli.commands.gemini import add_gemini_command, run_gemini_command
from research_agent.cli.commands.ingest import add_ingest_command, run_ingest_command

__all__ = [
    "add_gemini_command", 
    "run_gemini_command",
    "add_ingest_command", 
    "run_ingest_command"
]
