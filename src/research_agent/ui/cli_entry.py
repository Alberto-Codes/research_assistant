"""
DEPRECATED: Command-line entry point for the Research Agent application.

This module is deprecated and will be removed in a future version.
Please use research_agent.main instead:

    from research_agent.main import main
    main()

Or run the package directly:

    python -m research_agent
"""

import sys
import warnings

# Show deprecation warning
warnings.warn(
    "The research_agent.ui.cli_entry module is deprecated. "
    "Please use research_agent.main instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Import the main function with an alias to avoid name collision
from research_agent.main import main as main_func


# For backward compatibility
def run_gemini_chat():
    """Run the Gemini chat Streamlit app using the new main module."""
    main_func(["ui"])


# For backward compatibility
def main():
    """Command-line entry point using the new main module."""
    main_func()
