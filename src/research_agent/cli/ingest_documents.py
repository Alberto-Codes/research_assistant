"""
Command-line script for ingesting documents into ChromaDB.

This script provides a command-line interface for ingesting documents
from a directory into a ChromaDB collection.
"""

import argparse
import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Make sure we can import from the package
try:
    from research_agent.core.doc_graph import (
        load_documents_from_directory,
        run_document_ingestion_graph,
    )
    from research_agent.core.graph import display_results
except ImportError:
    # Add parent directory to path if run directly
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    sys.path.insert(0, parent_dir)
    from research_agent.core.doc_graph import (
        load_documents_from_directory,
        run_document_ingestion_graph,
    )
    from research_agent.core.graph import display_results


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ingest documents into ChromaDB from a directory")
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./data",
        help="Directory containing documents to ingest",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="default_collection",
        help="Name of the ChromaDB collection to use",
    )
    parser.add_argument(
        "--chroma-dir",
        type=str,
        default="./chroma_db",
        help="Directory where ChromaDB data should be persisted",
    )

    return parser.parse_args()


async def main():
    """Main function to run the document ingestion."""
    # Parse command line arguments
    args = parse_args()

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


if __name__ == "__main__":
    # Set up asyncio for Windows if needed
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the main function
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
