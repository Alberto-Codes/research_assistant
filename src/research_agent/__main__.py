"""
Main entry point for the Research Agent package.

This module allows the research_agent package to be executed directly
using 'python -m research_agent'.
"""

import importlib.util
import sys
from pathlib import Path

# Add the parent directory to sys.path to ensure main.py can be imported
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import and run the main function from the top-level main.py
spec = importlib.util.spec_from_file_location("main", str(Path(__file__).parent.parent / "main.py"))
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

if __name__ == "__main__":
    main_module.main()
