"""
Document ingestion components for the Research Agent.

This package contains classes and utilities specifically for
the document ingestion functionality in the Research Agent.
"""

# Import all needed components to make them available from the package
from research_agent.core.document.dependencies import ChromaDBDependencies
from research_agent.core.document.graph import (
    get_document_ingestion_graph,
    ingest_documents,
    load_documents_from_directory,
    run_document_ingestion_graph,
)
from research_agent.core.document.nodes import ChromaDBIngestionNode
from research_agent.core.document.state import DocumentState

__all__ = [
    "ChromaDBDependencies",
    "ChromaDBIngestionNode",
    "DocumentState",
    "get_document_ingestion_graph",
    "ingest_documents",
    "load_documents_from_directory",
    "run_document_ingestion_graph",
]
