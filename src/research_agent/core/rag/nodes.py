"""
Node definitions for the RAG graph in the Research Agent.

This module defines the nodes used in the RAG workflow, including:
- QueryNode: Processes the initial user query
- RetrieveNode: Retrieves relevant documents from ChromaDB
- AnswerNode: Generates an answer using Gemini based on retrieved documents
"""

import logging
import time
from dataclasses import dataclass

from typing_extensions import Annotated

from pydantic_graph import BaseNode, Edge, End, GraphRunContext

from research_agent.core.rag.state import RAGState
from research_agent.core.rag.dependencies import RAGDependencies

# Module-specific logger
logger = logging.getLogger(__name__)


@dataclass
class QueryNode(BaseNode[RAGState]):
    """Node to handle initial user query.
    
    This node logs the incoming query and prepares for document retrieval.
    """
    
    async def run(
        self, ctx: GraphRunContext[RAGState]
    ) -> Annotated[
        "RetrieveNode", Edge(label="Retrieve documents")
    ]:
        """Process the user query and continue to document retrieval.
        
        Args:
            ctx: Graph run context containing the state
            
        Returns:
            The RetrieveNode to continue execution
        """
        # Log the incoming query
        logger.info(f"Processing query: {ctx.state.query}")
        
        # Start timing the overall process
        ctx.state.total_time = time.time()
        
        return RetrieveNode()


@dataclass
class RetrieveNode(BaseNode[RAGState, RAGDependencies]):
    """Node to retrieve relevant documents from ChromaDB.
    
    This node queries ChromaDB for documents relevant to the user's query
    and adds them to the state for use in answer generation.
    """
    
    async def run(
        self, ctx: GraphRunContext[RAGState, RAGDependencies]
    ) -> Annotated[
        "AnswerNode", Edge(label="Generate answer")
    ]:
        """Retrieve relevant documents from ChromaDB.
        
        Args:
            ctx: Graph run context containing the state and dependencies
            
        Returns:
            The AnswerNode to continue execution
        """
        # Get our dependencies
        collection = ctx.deps.chroma_collection
        
        # Start timing retrieval
        retrieval_start = time.time()
        
        # Query ChromaDB for relevant documents
        logger.info(f"Querying ChromaDB for documents relevant to: {ctx.state.query}")
        try:
            results = await collection.query(
                query_texts=[ctx.state.query],
                n_results=5
            )
            
            # Store retrieved documents and metadata in state
            if results and "documents" in results and len(results["documents"]) > 0:
                ctx.state.retrieved_documents = [
                    {"content": doc, "metadata": meta}
                    for doc, meta in zip(
                        results["documents"][0], 
                        results["metadatas"][0]
                    )
                ]
                
                # Store source information
                ctx.state.sources = [
                    meta.get("source", "unknown") 
                    for meta in results["metadatas"][0]
                ]
                
                logger.info(f"Retrieved {len(ctx.state.retrieved_documents)} documents")
            else:
                logger.warning("No documents returned from ChromaDB query")
                
        except Exception as e:
            logger.error(f"Error during document retrieval: {str(e)}")
            # Store empty results but allow the workflow to continue
            ctx.state.retrieved_documents = []
            ctx.state.sources = []
        
        # Record retrieval time
        ctx.state.retrieval_time = time.time() - retrieval_start
        
        return AnswerNode()


@dataclass
class AnswerNode(BaseNode[RAGState, RAGDependencies]):
    """Node to generate answer using Gemini based on retrieved documents.
    
    This node formats the retrieved documents into a prompt and uses the
    Gemini model to generate a response.
    """
    
    async def run(
        self, ctx: GraphRunContext[RAGState, RAGDependencies]
    ) -> Annotated[
        End, Edge(label="Complete")
    ]:
        """Generate an answer based on retrieved documents.
        
        Args:
            ctx: Graph run context containing the state and dependencies
            
        Returns:
            End object to signal completion of the graph
        """
        # Get our model
        model = ctx.deps.gemini_model
        
        # Start timing generation
        generation_start = time.time()
        
        # Format context from retrieved documents
        if ctx.state.retrieved_documents:
            context = "\n\n".join([
                f"Document {i+1} (from {ctx.state.sources[i]}):\n{doc['content']}"
                for i, doc in enumerate(ctx.state.retrieved_documents)
            ])
        else:
            context = "No relevant documents found."
        
        # Create prompt with retrieval results and query
        prompt = f"""
        Based on the following information, please answer the question.
        
        CONTEXT:
        {context}
        
        QUESTION:
        {ctx.state.query}
        
        Answer the question based only on the provided context. If the context doesn't contain 
        the information needed to answer the question, say "I don't have enough information to 
        answer this question."
        
        Include citations to the relevant documents where appropriate.
        """
        
        logger.info("Generating answer with Gemini model")
        try:
            # Generate answer using Gemini
            result = await model.generate(prompt)
            ctx.state.answer = result.text
            logger.info(f"Generated answer with {len(ctx.state.answer)} characters")
        except Exception as e:
            logger.error(f"Error during answer generation: {str(e)}")
            ctx.state.answer = (
                "I'm sorry, I encountered an error while generating a response. "
                "Please try again later."
            )
        
        # Record generation time
        ctx.state.generation_time = time.time() - generation_start
        
        # Calculate total time as the time since the initial state.total_time was set
        elapsed = time.time() - ctx.state.total_time
        ctx.state.total_time = elapsed
        
        # Format the final result with answer and sources
        if ctx.state.sources:
            source_list = ", ".join(ctx.state.sources)
            text_result = f"{ctx.state.answer}\n\nSources: {source_list}"
        else:
            text_result = ctx.state.answer
        
        # Create an End object with the text attribute
        result = End(data=text_result)
        
        return result 