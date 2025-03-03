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
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast, Union
from pathlib import Path
import os

# Import what's available from pydantic_graph
from pydantic_graph import BaseNode, End, GraphRunContext, Edge
from typing_extensions import Annotated

from research_agent.core.document.dependencies import ChromaDBDependencies, DoclingDependencies
from research_agent.core.document.state import DocumentState
from research_agent.core.gemini.nodes import NodeError, _measure_execution_time

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class DoclingProcessorNode(BaseNode[DocumentState, DoclingDependencies]):
    """
    Node that processes documents using Docling before ingestion.

    This node takes file paths from the state and processes them using
    the Docling processor to extract structured content and metadata.
    """

    _log_prefix = "Docling Processing"
    
    def _get_output_text(self, ctx):
        """
        Get the text to display in logs.

        Args:
            ctx: The graph run context.

        Returns:
            The text to display in logs.
        """
        if hasattr(ctx.state, "file_paths") and ctx.state.file_paths:
            return f"Processed {len(ctx.state.file_paths)} documents with Docling"
        return "No documents processed with Docling"

    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> ChromaDBIngestionNode:
        """
        Process documents using Docling.

        Args:
            ctx: The graph run context containing state and dependencies.

        Returns:
            The ChromaDBIngestionNode for continuing the flow.
        """
        # Record the start time
        start_time = time.time()

        # Check if we have files to process
        if not hasattr(ctx.state, "file_paths") or not ctx.state.file_paths:
            logger.warning("DoclingProcessorNode: No file paths provided for processing")
            # We'll continue with the existing documents in state, if any
            return ChromaDBIngestionNode()

        try:
            # Get the DoclingProcessor from dependencies
            processor = ctx.deps.docling_processor
            
            # Check if Docling is available
            if not hasattr(processor, 'docling_available') or not processor.docling_available:
                logger.warning("DoclingProcessorNode: Docling is not available. Skipping Docling processing.")
                # We'll continue with any existing documents in state
                return ChromaDBIngestionNode()
            
            # Process each file
            processed_documents = []
            processed_metadata = []
            processed_ids = []
            
            for i, file_path in enumerate(ctx.state.file_paths):
                try:
                    # Process the file with Docling
                    logger.info(f"Processing file with Docling: {file_path}")
                    docling_document = processor.process_file(file_path)
                    
                    # Extract text content
                    document_text = docling_document.export_to_text()
                    processed_documents.append(document_text)
                    
                    # Create metadata including source file and other document info
                    metadata = {
                        "source": file_path,
                        "document_type": getattr(docling_document, "document_type", "unknown"),
                        "processed_with": "docling"
                    }
                    
                    # Extract rich metadata from Docling document
                    # Add document properties
                    if hasattr(docling_document, "document_name"):
                        metadata["document_name"] = docling_document.document_name
                    if hasattr(docling_document, "language"):
                        metadata["language"] = docling_document.language
                    if hasattr(docling_document, "page_count"):
                        metadata["page_count"] = docling_document.page_count
                    
                    # Extract structural information
                    if hasattr(docling_document, "parts") and docling_document.parts:
                        # Count document parts by type
                        part_counts = {}
                        for part in docling_document.parts:
                            part_type = str(part.type)
                            part_counts[part_type] = part_counts.get(part_type, 0) + 1
                        metadata["part_counts"] = part_counts
                        
                        # Extract table information if available
                        tables_info = []
                        for part in docling_document.parts:
                            if str(part.type) == "TABLE" and hasattr(part, "table"):
                                table_info = {
                                    "rows": len(part.table.rows) if hasattr(part.table, "rows") else 0,
                                    "columns": len(part.table.headers) if hasattr(part.table, "headers") else 0
                                }
                                tables_info.append(table_info)
                        if tables_info:
                            metadata["tables"] = tables_info
                    
                    # Extract document metadata if available
                    if hasattr(docling_document, "metadata") and docling_document.metadata:
                        doc_metadata = docling_document.metadata
                        if hasattr(doc_metadata, "title") and doc_metadata.title:
                            metadata["title"] = doc_metadata.title
                        if hasattr(doc_metadata, "author") and doc_metadata.author:
                            metadata["author"] = doc_metadata.author
                        if hasattr(doc_metadata, "creation_date") and doc_metadata.creation_date:
                            metadata["creation_date"] = str(doc_metadata.creation_date)
                        if hasattr(doc_metadata, "modified_date") and doc_metadata.modified_date:
                            metadata["modified_date"] = str(doc_metadata.modified_date)
                    
                    # Add any existing metadata if available
                    if hasattr(ctx.state, "metadata") and ctx.state.metadata and i < len(ctx.state.metadata):
                        metadata.update(ctx.state.metadata[i])
                    
                    processed_metadata.append(metadata)
                    
                    # Use existing ID if available, otherwise use the filename
                    doc_id = None
                    if hasattr(ctx.state, "document_ids") and ctx.state.document_ids and i < len(ctx.state.document_ids):
                        doc_id = ctx.state.document_ids[i]
                    else:
                        doc_id = f"doc_{Path(file_path).stem}_{i}"
                    
                    processed_ids.append(doc_id)
                    
                    logger.info(f"Successfully processed {file_path} with Docling")
                except Exception as e:
                    logger.error(f"Error processing file {file_path} with Docling: {str(e)}")
                    # Skip this document but continue processing others
            
            # Update the state with processed documents
            ctx.state.documents = processed_documents
            ctx.state.metadata = processed_metadata
            ctx.state.document_ids = processed_ids
            
            # Add processing time to execution history
            processing_time = time.time() - start_time
            if "node_execution_history" not in ctx.state.__dict__:
                ctx.state.node_execution_history = []
            
            ctx.state.node_execution_history.append(
                f"DoclingProcessorNode: Processed {len(processed_documents)} documents (took {processing_time:.3f}s)"
            )
            
            logger.info(f"Completed Docling processing for {len(processed_documents)} documents")
            
            # Continue to the ChromaDB ingestion node
            return ChromaDBIngestionNode()
            
        except Exception as e:
            error_message = f"Error during Docling document processing: {str(e)}"
            logger.error(error_message)
            
            # Add to execution history
            if "node_execution_history" not in ctx.state.__dict__:
                ctx.state.node_execution_history = []
            
            ctx.state.node_execution_history.append(
                f"DoclingProcessorNode: Error - {error_message}"
            )
            
            # Try to continue gracefully - create dummy documents if none exist
            if not hasattr(ctx.state, "documents") or not ctx.state.documents:
                ctx.state.documents = [f"Failed to process document {i}" for i, _ in enumerate(ctx.state.file_paths)]
                ctx.state.metadata = ctx.state.metadata if hasattr(ctx.state, "metadata") and ctx.state.metadata else [{} for _ in ctx.state.file_paths]
                ctx.state.document_ids = ctx.state.document_ids if hasattr(ctx.state, "document_ids") and ctx.state.document_ids else [f"doc_{i}" for i, _ in enumerate(ctx.state.file_paths)]
            
            # Continue to ChromaDBIngestionNode with any documents that may already be in the state
            return ChromaDBIngestionNode()


@dataclass
class ChromaDBIngestionNode(BaseNode[DocumentState, ChromaDBDependencies, Dict[str, Any]]):
    """
    Node that ingests documents into a ChromaDB collection.

    This node takes a list of documents from the state and adds them to a
    ChromaDB collection using the provided ChromaDB client.
    """

    _log_prefix = "Document Ingestion"

    def _get_output_text(self, ctx):
        """
        Get the text to display in logs.

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
        """
        Ingest documents into ChromaDB.

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


@dataclass
class FileTypeRouterNode(BaseNode[DocumentState, DoclingDependencies]):
    """
    Node that evaluates file types and routes them to the appropriate processing path.
    
    This node checks each file type to determine:
    1. If it's supported by Docling, route to DoclingProcessorNode
    2. If it's a text file, route directly to ChromaDBIngestionNode
    3. For other unsupported types, attempt to read as text or skip
    
    This allows for more efficient processing by bypassing Docling for file types
    it doesn't support.
    """
    
    _log_prefix = "File Type Router"
    docstring_notes = True  # Enable using docstring for notes in diagram
    
    # List of file extensions supported by Docling
    DOCLING_SUPPORTED_EXTENSIONS = {
        ".pdf", ".docx", ".pptx", ".html", ".htm", ".png", ".jpg", ".jpeg", 
        ".xlsx", ".csv", ".md", ".xml", ".json"
    }
    
    # Text file extensions that can go directly to Chroma
    TEXT_FILE_EXTENSIONS = {".txt"}
    
    # List of file extensions that should be skipped entirely
    SKIP_EXTENSIONS = {".exe", ".dll", ".zip", ".rar", ".7z", ".tar", ".gz", ".bin"}
    
    def _get_output_text(self, ctx):
        """
        Get the text to display in logs.
        
        Args:
            ctx: The graph run context.
            
        Returns:
            The text to display in logs.
        """
        if hasattr(ctx.state, "file_paths") and ctx.state.file_paths:
            return f"Routed {len(ctx.state.file_paths)} files based on their types"
        return "No files to route"
    
    @_measure_execution_time
    async def run(self, ctx: GraphRunContext) -> Union[DoclingProcessorNode, ChromaDBIngestionNode]:
        """
        Evaluate file types and route to the appropriate node.
        
        Args:
            ctx: The graph run context containing state and dependencies.
            
        Returns:
            Either DoclingProcessorNode or ChromaDBIngestionNode based on file types.
        """
        # Record the start time
        start_time = time.time()
        
        # Check if we have files to process
        if not hasattr(ctx.state, "file_paths") or not ctx.state.file_paths:
            logger.warning("FileTypeRouterNode: No file paths provided for processing")
            # We'll continue with the existing documents in state, if any
            return ChromaDBIngestionNode()
        
        # Process file paths to separate them by type
        docling_files = []
        text_files = []
        unsupported_files = []
        skipped_files = []
        
        for file_path in ctx.state.file_paths:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension in self.SKIP_EXTENSIONS:
                logger.info(f"Skipping binary/archive file: {file_path}")
                skipped_files.append(file_path)
                continue
                
            if file_extension in self.DOCLING_SUPPORTED_EXTENSIONS:
                docling_files.append(file_path)
            elif file_extension in self.TEXT_FILE_EXTENSIONS:
                text_files.append(file_path)
                
                # For text files, we need to read them and add to documents list
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    
                    # Add document content
                    if not hasattr(ctx.state, "documents"):
                        ctx.state.documents = []
                    ctx.state.documents.append(text_content)
                    
                    # Add metadata
                    if not hasattr(ctx.state, "metadata") or ctx.state.metadata is None:
                        ctx.state.metadata = []
                    ctx.state.metadata.append({
                        "source": file_path,
                        "document_type": "text",
                        "processed_with": "direct"
                    })
                    
                    # Add document ID
                    if not hasattr(ctx.state, "document_ids") or ctx.state.document_ids is None:
                        ctx.state.document_ids = []
                    doc_id = f"doc_{Path(file_path).stem}_{len(ctx.state.document_ids)}"
                    ctx.state.document_ids.append(doc_id)
                    
                    logger.info(f"Directly processed text file: {file_path}")
                except Exception as e:
                    logger.error(f"Error processing text file {file_path}: {str(e)}")
            else:
                # For unsupported file types, attempt to read as text if it's not binary
                unsupported_files.append(file_path)
                try:
                    # Try to detect if file is binary
                    is_binary = False
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            sample = f.read(1024)
                            # Simple binary detection - check for null bytes
                            if '\0' in sample:
                                is_binary = True
                    except UnicodeDecodeError:
                        is_binary = True
                    
                    if is_binary:
                        logger.warning(f"Skipping binary file with unsupported extension: {file_path}")
                        continue
                    
                    # Try to read as text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text_content = f.read()
                    
                    # Add document content
                    if not hasattr(ctx.state, "documents"):
                        ctx.state.documents = []
                    ctx.state.documents.append(text_content)
                    
                    # Add metadata
                    if not hasattr(ctx.state, "metadata") or ctx.state.metadata is None:
                        ctx.state.metadata = []
                    ctx.state.metadata.append({
                        "source": file_path,
                        "document_type": "unknown",
                        "processed_with": "direct",
                        "note": "Unsupported file type processed as text"
                    })
                    
                    # Add document ID
                    if not hasattr(ctx.state, "document_ids") or ctx.state.document_ids is None:
                        ctx.state.document_ids = []
                    doc_id = f"doc_{Path(file_path).stem}_{len(ctx.state.document_ids)}"
                    ctx.state.document_ids.append(doc_id)
                    
                    logger.info(f"Processed unsupported file as text: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not process unsupported file {file_path}: {str(e)}")
        
        # Update file_paths in state to only include files for Docling
        ctx.state.file_paths = docling_files
        
        # Add processing time to execution history
        processing_time = time.time() - start_time
        if "node_execution_history" not in ctx.state.__dict__:
            ctx.state.node_execution_history = []
        
        ctx.state.node_execution_history.append(
            f"FileTypeRouterNode: Routed {len(docling_files)} files to Docling, {len(text_files)} text files direct to Chroma, " + 
            f"attempted {len(unsupported_files)} unsupported files, skipped {len(skipped_files)} files (took {processing_time:.3f}s)"
        )
        
        # Route based on whether there are files for Docling
        if docling_files:
            logger.info(f"Routing {len(docling_files)} files to Docling processor")
            return DoclingProcessorNode()
        else:
            logger.info("No files for Docling, routing directly to ChromaDB")
            return ChromaDBIngestionNode()
