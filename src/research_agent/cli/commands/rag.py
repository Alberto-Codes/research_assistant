"""
RAG command implementation.

This module defines the RAG (Retrieval Augmented Generation) command for the Research Agent CLI,
which allows running queries against ingested documents using Gemini for generating answers.
"""

import argparse
import asyncio
import logging
import time
from typing import Optional

import chromadb
from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel

from research_agent.core.rag import run_rag_query


def add_rag_command(subparsers: "argparse._SubParsersAction") -> None:
    """
    Add the RAG command to the CLI subparsers.

    Args:
        subparsers: The subparsers object to add the command to.
    """
    rag_parser = subparsers.add_parser(
        "rag",
        help="Query documents using RAG with Gemini",
        description="Use Retrieval Augmented Generation to answer questions based on your documents",
    )

    rag_parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="The question to ask about your documents",
    )

    rag_parser.add_argument(
        "--collection",
        type=str,
        default="my_docs",
        help="ChromaDB collection name to query",
    )

    rag_parser.add_argument(
        "--chroma-dir",
        type=str,
        default="./chroma_db",
        help="Directory for ChromaDB storage",
    )

    rag_parser.add_argument(
        "--project-id",
        type=str,
        help="Google Cloud project ID (optional, will detect from environment if not provided)",
    )

    rag_parser.add_argument(
        "--model",
        type=str,
        default="gemini-1.5-pro",
        help="Gemini model to use",
    )

    rag_parser.add_argument(
        "--region",
        type=str,
        default="us-central1",
        help="Google Cloud region for Vertex AI",
    )


async def run_rag_command(args: argparse.Namespace) -> int:
    """
    Run the RAG command with the specified arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    logger = logging.getLogger(__name__)
    logger.info("Running RAG query")

    start_time = time.time()

    # Extract parameters from args
    query = args.query
    collection_name = args.collection
    chroma_dir = args.chroma_dir
    project_id = args.project_id
    model_name = args.model
    region = args.region

    try:
        # Initialize ChromaDB
        logger.info(f"Connecting to ChromaDB at {chroma_dir}")
        chroma_client = chromadb.PersistentClient(path=chroma_dir)

        try:
            collection = chroma_client.get_collection(collection_name)
            logger.info(f"Found collection '{collection_name}' with {collection.count()} documents")
        except Exception as e:
            logger.error(f"Could not find collection '{collection_name}': {e}")
            print(
                f"Error: Collection '{collection_name}' not found. Please ingest documents first."
            )
            return 1

        # Initialize Gemini model
        logger.info(f"Initializing Gemini model {model_name}")
        gemini_model = VertexAIModel(model_name=model_name, project_id=project_id, region=region)

        # Inspect the model's methods and attributes
        logger.info(f"VertexAIModel type: {type(gemini_model)}")
        logger.info(f"VertexAIModel methods: {dir(gemini_model)}")

        # Check if specific methods exist
        for method in ["__call__", "run", "complete", "generate", "invoke", "ainvoke"]:
            logger.info(f"Has method '{method}': {hasattr(gemini_model, method)}")

        # Create a PydanticAI Agent to use the VertexAIModel
        logger.info("Creating Agent with VertexAIModel")
        agent = Agent(gemini_model)

        logger.info(f"Running RAG query: '{query}'")
        result = await run_rag_query(
            query=query, chroma_collection=collection, gemini_model=agent, project_id=project_id
        )

        # Print the results
        print("\nRAG Query Results:")
        print("=" * 80)
        print(result["answer"])
        print("=" * 80)
        print(f"Retrieval time: {result['retrieval_time']:.2f}s")
        print(f"Generation time: {result['generation_time']:.2f}s")
        print(f"Total execution time: {result['total_time']:.2f}s")

        logger.info("Successfully completed RAG query")
        return 0
    except Exception as e:
        logger.error(f"Failed to run RAG query: {e}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1
