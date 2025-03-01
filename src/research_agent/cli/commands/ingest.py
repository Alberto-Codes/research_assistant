"""
Document ingestion command implementation.

This module defines the ingest command for the Research Agent CLI,
which allows ingesting documents into ChromaDB from a specified directory.
"""

import argparse
import logging
import os
from typing import Any, Dict, List, Optional

from research_agent.core.doc_graph import (
    load_documents_from_directory,
    run_document_ingestion_graph,
)


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


async def run_ingest_command(args: argparse.Namespace) -> int:
    """
    Run the ingest command with the specified arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    logger = logging.getLogger(__name__)

    # Check if data directory exists
    if not os.path.exists(args.data_dir) or not os.path.isdir(args.data_dir):
        logger.error(f"Data directory '{args.data_dir}' does not exist or is not a directory")
        return 1

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

    # Create document IDs based on filenames
    document_ids = [f"doc_{i}_{meta['filename']}" for i, meta in enumerate(metadata)]

    # Set up ChromaDB directory
    os.makedirs(args.chroma_dir, exist_ok=True)

    # Run the document ingestion graph
    logger.info(f"Ingesting documents into ChromaDB collection '{args.collection}'")
    result, state, errors = await run_document_ingestion_graph(
        documents=documents,
        collection_name=args.collection,
        document_ids=document_ids,
        metadata=metadata,
        persist_directory=args.chroma_dir,
    )

    # Check for errors
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
    print(f"- Ingestion Time: {state.total_time:.3f} seconds")

    print("\nIngested Documents:")
    for i, (doc_id, meta) in enumerate(zip(document_ids, metadata)):
        print(f"  {i+1}. {doc_id} - {meta['filename']} ({meta['file_size']} bytes)")

    return 0
