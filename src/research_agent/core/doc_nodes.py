"""
Node definitions for document ingestion in the Research Agent graph.

This module defines the nodes used for document ingestion into ChromaDB.
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

# Import what's available from pydantic_graph
from pydantic_graph import BaseNode, End, GraphRunContext

from research_agent.core.chroma_dependencies import ChromaDBDependencies
from research_agent.core.doc_state import DocumentState

# Import from existing code
from research_agent.core.nodes import NodeError, _measure_execution_time

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class ChromaDBIngestionNode(BaseNode[DocumentState, ChromaDBDependencies, Dict[str, Any]]):
    """Node that ingests documents into a ChromaDB collection.

    This node takes a list of documents from the state and adds them to a
    ChromaDB collection using the provided ChromaDB client.
    """

    _log_prefix = "Document Ingestion"

    def _get_output_text(self, ctx):
        """Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        if ctx.state.ingestion_results:
            return f"Ingested {len(ctx.state.documents)} documents into {ctx.state.chroma_collection_name}"
        return "No documents ingested"

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> End[Dict[str, Any]]:
        """Ingest documents into ChromaDB.

        Args:
            ctx: The graph run context containing state and dependencies.

        Returns:
            An End object containing the ingestion results.
        """
        # Record the start time
        start_time = time.time()

        # Check if we have documents to ingest
        if not ctx.state.documents or len(ctx.state.documents) == 0:
            result = {"error": "No documents provided for ingestion"}
            ctx.state.ingestion_results = result
            logger.warning("ChromaDBIngestionNode: No documents provided for ingestion")
            return End(result)

        try:
            # Use the ChromaDB client from dependencies to ingest documents
            ingestion_result = ctx.deps.chroma_client.add_documents(
                collection_name=ctx.state.chroma_collection_name,
                documents=ctx.state.documents,
                document_ids=ctx.state.document_ids,
                metadata=ctx.state.metadata,
            )

            # Store the results in the state
            ctx.state.ingestion_results = ingestion_result

            # Record the ingestion time
            ingestion_time = time.time() - start_time

            # Add to execution history
            if "node_execution_history" not in ctx.state.__dict__:
                ctx.state.node_execution_history = []
            ctx.state.node_execution_history.append(
                f"ChromaDBIngestionNode: Ingested {len(ctx.state.documents)} documents into {ctx.state.chroma_collection_name}"
            )

            # Calculate the total execution time
            ctx.state.total_time = ingestion_time

            logger.info(
                f"Ingested {len(ctx.state.documents)} documents into ChromaDB collection '{ctx.state.chroma_collection_name}'"
            )

            return End(ingestion_result)

        except Exception as e:
            error_message = f"Error during document ingestion: {str(e)}"
            logger.error(error_message)
            result = {"error": error_message}
            ctx.state.ingestion_results = result
            return End(result)
