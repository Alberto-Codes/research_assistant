"""
Utilities for working with the Research Agent graphs.

This module provides common functions and utilities for working with
different graphs in the Research Agent application.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic_graph import GraphRunResult

# Set up logging
logger = logging.getLogger(__name__)

# Note: The utility functions that were previously here have been moved
# to their respective modules to avoid circular imports:
# - run_gemini_chat -> use core.gemini.graph.run_gemini_agent_graph directly
# - ingest_documents -> use core.document.graph.run_document_ingestion_graph directly
# - display_results -> use core.gemini.graph.display_results directly 