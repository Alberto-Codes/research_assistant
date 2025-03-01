"""
DEPRECATED: Main entry point for the Research Agent application.

This module is deprecated and will be removed in a future version.
Please use research_agent.main instead:

    from research_agent.main import main
    main()

Or run the package directly:

    python -m research_agent
"""

import sys
import warnings

from research_agent.main import main

# Show deprecation warning
warnings.warn(
    "The top-level main.py module is deprecated. " "Please use research_agent.main instead.",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    # Forward to the new main function
    sys.exit(main())
