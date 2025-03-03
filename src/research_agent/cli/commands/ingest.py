"""
Document ingestion command implementation.

This module defines the ingest command for the Research Agent CLI,
which allows ingesting documents into ChromaDB from a specified directory.
"""

import argparse
import logging
import os
from typing import Any, Dict, List, Optional

from research_agent.core.document.graph import (
    load_documents_from_directory,
    run_document_ingestion_graph,
    run_document_ingestion_graph_with_docling,
    visualize_document_processing_graph,
)
from research_agent.core.document_processing.docling_processor import DoclingProcessorOptions
from research_agent.core.document.dependencies import DoclingDependencies
from research_agent.core.document.state import DocumentState
from research_agent.core.document.dependencies import ChromaDBDependencies


def add_ingest_command(subparsers: "argparse._SubParsersAction") -> None:
    """
    Add the ingest command to the CLI subparsers.

    Args:
        subparsers: The subparsers object to add the command to.
    """
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest documents into ChromaDB",
        description="Ingest documents from a directory into a ChromaDB collection",
    )

    ingest_parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Directory containing documents to ingest",
    )

    ingest_parser.add_argument(
        "--collection",
        type=str,
        default="default_collection",
        help="Name of the ChromaDB collection to use",
    )

    ingest_parser.add_argument(
        "--chroma-dir",
        type=str,
        default="./chroma_db",
        help="Directory where ChromaDB data should be persisted",
    )
    
    ingest_parser.add_argument(
        "--use-docling",
        action="store_true",
        help="Process documents with Docling before ingestion",
    )
    
    ingest_parser.add_argument(
        "--enable-ocr",
        action="store_true",
        help="Enable OCR processing with Docling (only applies when --use-docling is set)",
    )
    
    ingest_parser.add_argument(
        "--extract-tables",
        action="store_true",
        help="Extract tables from documents with Docling (only applies when --use-docling is set)",
    )
    
    ingest_parser.add_argument(
        "--extract-images",
        action="store_true",
        help="Extract images from documents with Docling (only applies when --use-docling is set)",
    )
    
    ingest_parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate a visualization of the document processing graph",
    )
    
    ingest_parser.add_argument(
        "--visualize-path",
        type=str,
        default="document_processing_graph.png",
        help="Path to save the graph visualization (only applies when --visualize is set)",
    )
    
    ingest_parser.add_argument(
        "--visualize-direction",
        type=str,
        default="LR",
        choices=["LR", "TB", "RL", "BT"],
        help="Direction of the graph visualization (LR=left-right, TB=top-bottom, RL=right-left, BT=bottom-top)",
    )


async def run_ingest_command(args: argparse.Namespace) -> int:
    """
    Run the ingest command with the specified arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    logger = logging.getLogger(__name__)

    # If visualization is requested, generate and save the graph diagram
    if args.visualize:
        logger.info(f"Generating document processing graph visualization to {args.visualize_path}")
        visualize_document_processing_graph(
            output_path=args.visualize_path, 
            direction=args.visualize_direction
        )
        logger.info(f"Graph visualization saved to {args.visualize_path}")
        
        # If only visualization was requested, return success
        if not os.path.exists(args.data_dir) or not os.path.isdir(args.data_dir):
            return 0

    # Check if data directory exists
    if not os.path.exists(args.data_dir) or not os.path.isdir(args.data_dir):
        logger.error(f"Data directory '{args.data_dir}' does not exist or is not a directory")
        return 1

    # Set up ChromaDB directory
    os.makedirs(args.chroma_dir, exist_ok=True)
    
    # Determine if we should use Docling
    if args.use_docling:
        return await run_with_docling(args, logger)
    else:
        return await run_standard_ingestion(args, logger)


async def run_standard_ingestion(args: argparse.Namespace, logger: logging.Logger) -> int:
    """
    Run standard document ingestion without Docling.
    
    Args:
        args: Parsed command line arguments.
        logger: Logger to use for logging.
        
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Load documents from directory
    logger.info(f"Loading documents from '{args.data_dir}'")
    document_dicts = load_documents_from_directory(args.data_dir)

    if not document_dicts:
        logger.error("No documents found in the specified directory")
        return 1

    logger.info(f"Found {len(document_dicts)} documents")

    # Extract content and metadata from document dicts
    documents = [doc["content"] for doc in document_dicts]
    metadata = [doc["metadata"] for doc in document_dicts]

    # Create document IDs based on filenames - include file extension in ID to avoid collisions
    document_ids = []
    for i, meta in enumerate(metadata):
        filename = meta['filename']
        # Extract file name and extension
        name_parts = os.path.splitext(filename)
        base_name = name_parts[0]
        extension = name_parts[1].lstrip('.') if len(name_parts) > 1 else ""
        
        # Create a more unique document ID that includes the file type
        doc_id = f"doc_{i}_{base_name}_type_{extension}"
        document_ids.append(doc_id)
        
        # Log the ID mapping
        logger.debug(f"Assigned document ID: {doc_id} to file: {filename}")

    # Create a document state
    state = DocumentState(
        documents=documents,
        document_ids=document_ids,
        metadata=metadata,
        chroma_collection_name=args.collection,
    )
    
    # Create dependencies
    dependencies = ChromaDBDependencies(persist_directory=args.chroma_dir)

    # Run the document ingestion graph
    logger.info(f"Ingesting documents into ChromaDB collection '{args.collection}'")
    result, final_state, history = await run_document_ingestion_graph(
        state=state, 
        dependencies=dependencies
    )

    # Check for errors in history
    errors = [item for item in history if isinstance(item, Exception)]
    if errors:
        logger.error("Errors occurred during document ingestion:")
        for error in errors:
            logger.error(f"  - {error}")
        return 1

    # Print results
    print("\nDocument Ingestion Results:")
    print(f"- Collection: {args.collection}")
    print(f"- Documents: {len(documents)}")
    print(f"- ChromaDB Directory: {os.path.abspath(args.chroma_dir)}")
    print(f"- Ingestion Time: {final_state.total_time:.3f} seconds")

    print("\nIngested Documents:")
    for i, (doc_id, meta) in enumerate(zip(document_ids, metadata)):
        print(f"  {i+1}. {doc_id} - {meta['filename']} ({meta['file_size']} bytes)")

    return 0


async def run_with_docling(args: argparse.Namespace, logger: logging.Logger) -> int:
    """
    Run document ingestion with Docling processing.
    
    Args:
        args: Parsed command line arguments.
        logger: Logger to use for logging.
        
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    # Get a list of all file paths in the data directory
    file_paths = []
    metadata = []
    document_ids = []
    
    logger.info(f"Scanning '{args.data_dir}' for documents to process with Docling")
    
    # Recursively find all files in the directory
    for root, _, files in os.walk(args.data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)
            
            # Create basic metadata
            file_stat = os.stat(file_path)
            meta = {
                "filename": file,
                "file_path": file_path,
                "file_size": file_stat.st_size,
                "last_modified": file_stat.st_mtime,
                "source": file_path,
            }
            metadata.append(meta)
            
            # Create ID with file type to prevent collisions
            # Extract file name and extension
            name_parts = os.path.splitext(file)
            base_name = name_parts[0]
            extension = name_parts[1].lstrip('.') if len(name_parts) > 1 else ""
            
            # Create a more unique document ID that includes the file type
            doc_id = f"doc_{len(document_ids)}_{base_name}_type_{extension}"
            document_ids.append(doc_id)
            
            # Log the ID mapping
            logger.debug(f"Assigned document ID: {doc_id} to file: {file}")
    
    if not file_paths:
        logger.error("No files found in the specified directory")
        return 1
    
    logger.info(f"Found {len(file_paths)} files to process with Docling")
    
    # Configure Docling options based on args
    docling_options = DoclingProcessorOptions(
        enable_ocr=args.enable_ocr,
        extract_tables=args.extract_tables,
        extract_images=args.extract_images,
    )
    
    # Create initial state with file paths
    state = DocumentState(
        file_paths=file_paths,
        document_ids=document_ids,
        metadata=metadata,
        chroma_collection_name=args.collection,
    )
    
    # Set up dependencies
    chroma_dependencies = ChromaDBDependencies(persist_directory=args.chroma_dir)
    docling_dependencies = DoclingDependencies.create(docling_options=docling_options)
    
    # Run the document ingestion graph with Docling
    logger.info(f"Processing and ingesting documents with Docling into ChromaDB collection '{args.collection}'")
    
    try:
        result, final_state, logs = await run_document_ingestion_graph_with_docling(
            state=state,
            chroma_dependencies=chroma_dependencies,
            docling_dependencies=docling_dependencies,
        )
        
        # Check for errors
        if logs and any(isinstance(log, Exception) for log in logs):
            logger.error("Errors occurred during document processing and ingestion:")
            for log in logs:
                if isinstance(log, Exception):
                    logger.error(f"  - {str(log)}")
            return 1
        
        # Print results
        print("\nDocument Processing and Ingestion Results:")
        print(f"- Collection: {args.collection}")
        print(f"- Files Processed: {len(file_paths)}")
        print(f"- Documents Ingested: {len(final_state.documents)}")
        print(f"- Processing Method: Docling")
        print(f"- ChromaDB Directory: {os.path.abspath(args.chroma_dir)}")
        print(f"- Total Time: {final_state.total_time:.3f} seconds")
        
        print("\nExecution History:")
        for entry in final_state.node_execution_history:
            print(f"  - {entry}")
        
        return 0
    except Exception as e:
        logger.error(f"Error during document processing and ingestion: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
