"""
Document ingestion module for the Research Agent.

This module provides functionality for ingesting documents into ChromaDB
collections, which can then be used for retrieval and other operations.
"""

# Import all needed components to make them available from the package
from research_agent.core.document.dependencies import ChromaDBDependencies, DoclingDependencies
from research_agent.core.document.graph import (
    get_document_ingestion_graph,
    get_document_ingestion_graph_with_docling,
    ingest_documents,
    ingest_files_with_docling,
    load_documents_from_directory,
    run_document_ingestion_graph,
    run_document_ingestion_graph_with_docling,
)
from research_agent.core.document.nodes import ChromaDBIngestionNode, DoclingProcessorNode
from research_agent.core.document.state import DocumentState

__all__ = [
    "ChromaDBDependencies",
    "DoclingDependencies",
    "ChromaDBIngestionNode",
    "DoclingProcessorNode",
    "DocumentState",
    "get_document_ingestion_graph",
    "get_document_ingestion_graph_with_docling",
    "ingest_documents",
    "ingest_files_with_docling",
    "load_documents_from_directory",
    "run_document_ingestion_graph",
    "run_document_ingestion_graph_with_docling",
]
