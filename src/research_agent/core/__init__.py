"""
Core components of the Research Agent application.

This package contains the core components of the Research Agent application,
organized into subpackages for different graph types.
"""

# Import Document components
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
from research_agent.core.document_processing.docling_processor import DoclingProcessor, DoclingProcessorOptions

# Import Gemini components
from research_agent.core.gemini.dependencies import GeminiDependencies
from research_agent.core.gemini.graph import (
    display_results,
    get_gemini_agent_graph,
    run_gemini_agent_graph,
)
from research_agent.core.gemini.nodes import GeminiAgentNode
from research_agent.core.gemini.state import GeminiState

# Old imports for backwards compatibility
# These will be deprecated in a future version
from research_agent.core.logging_config import configure_logging

__all__ = [
    # Common utilities
    "display_results",
    "ingest_documents",
    # Gemini components
    "GeminiAgentNode",
    "GeminiDependencies",
    "GeminiState",
    "get_gemini_agent_graph",
    "run_gemini_agent_graph",
    # Document components
    "ChromaDBDependencies",
    "DoclingDependencies",
    "ChromaDBIngestionNode",
    "DoclingProcessorNode",
    "DoclingProcessor",
    "DoclingProcessorOptions",
    "DocumentState",
    "get_document_ingestion_graph",
    "get_document_ingestion_graph_with_docling",
    "ingest_documents",
    "ingest_files_with_docling",
    "load_documents_from_directory",
    "run_document_ingestion_graph",
    "run_document_ingestion_graph_with_docling",
    # Legacy components
    "configure_logging",
]
