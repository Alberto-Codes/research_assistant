"""
Graph configuration for the RAG workflow.

This module defines the RAG graph that connects the QueryNode, RetrieveNode,
and AnswerNode into a complete workflow for retrieving and answering questions
based on document context.
"""

import logging
import traceback
from typing import Any, Dict, Optional

# Try to import from pydantic_graph with a fallback for GraphError
try:
    from pydantic_graph import Graph, GraphError, GraphRunResult
except ImportError:
    from pydantic_graph import Graph, GraphRunResult

    # Define GraphError if it's not available in pydantic_graph
    class GraphError(Exception):
        """Error raised when a graph fails to execute."""

        pass


from research_agent.core.rag.dependencies import RAGDependencies
from research_agent.core.rag.nodes import AnswerNode, QueryNode, RetrieveNode
from research_agent.core.rag.state import RAGState

# Module-specific logger
logger = logging.getLogger(__name__)


def create_rag_graph() -> Graph:
    """Create and configure the RAG workflow graph.

    Returns:
        A configured Graph for the RAG workflow
    """
    logger.info("Creating RAG graph")

    # Create the node instances
    # The first node will be the starting node by default
    query_node = QueryNode()
    retrieve_node = RetrieveNode()
    answer_node = AnswerNode()

    # Create the RAG graph with all the nodes
    graph = Graph(nodes=[query_node, retrieve_node, answer_node])

    logger.info("RAG graph created with nodes: QueryNode, RetrieveNode, AnswerNode")

    return graph


# Create a singleton instance of the graph for reuse
rag_graph = create_rag_graph()


async def run_rag_query(
    query: str, chroma_collection: Any, gemini_model: Any, project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Run a RAG query through the graph workflow.

    Args:
        query: The user's question
        chroma_collection: ChromaDB collection for document retrieval
        gemini_model: Gemini model for generating answers
        project_id: Optional Google Cloud project ID

    Returns:
        Dictionary with answer and timing information
    """
    import time

    logger.debug("Starting run_rag_query")

    start_time = time.time()

    # Create dependencies
    logger.debug(
        f"Creating RAGDependencies with collection: {chroma_collection}, model: {gemini_model}"
    )
    deps = RAGDependencies(
        chroma_collection=chroma_collection, gemini_model=gemini_model, project_id=project_id
    )
    logger.debug(f"Created dependencies: {deps}")

    # Create initial state with the query
    logger.debug(f"Creating RAGState with query: {query}")
    state = RAGState(query=query)
    logger.debug(f"Created state: {state}")

    # Run the graph
    logger.info(f"Running RAG graph for query: '{query}'")
    try:
        # Use the QueryNode as the start_node and pass state and deps as kwargs
        logger.debug("Calling rag_graph.run with start_node=QueryNode()")

        # Correct signature: run(start_node, state=state, deps=deps)
        result = await rag_graph.run(QueryNode(), state=state, deps=deps)

        logger.debug(f"Graph run completed with result type: {type(result)}")
        logger.debug(f"Result attributes: {dir(result)}")

        # Check what's in the result object
        if hasattr(result, "data"):
            logger.debug(f"Result has 'data' attribute: {result.data}")
            answer = result.data
        elif hasattr(result, "output"):
            logger.debug(f"Result has 'output' attribute: {result.output}")
            answer = result.output
        elif hasattr(result, "text"):
            logger.debug(f"Result has 'text' attribute: {result.text}")
            answer = result.text
        else:
            logger.warning(f"Could not find expected attribute in result: {result}")
            answer = f"Warning: Could not extract answer from result object: {result}"

        logger.debug(f"Extracted answer: {answer}")
    except Exception as e:
        logger.error(f"Error running RAG graph: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        answer = f"Error: {str(e)}"

    # Extract timing information
    execution_time = time.time() - start_time
    logger.debug(f"Execution completed in {execution_time:.2f}s")

    # Return the answer and timing information
    result_dict = {
        "answer": answer,
        "retrieval_time": state.retrieval_time,
        "generation_time": state.generation_time,
        "total_time": execution_time,
    }
    logger.debug(f"Returning result: {result_dict}")
    return result_dict
