# ChromaDB and Gemini Integration with Pydantic-Graph

This document outlines the implementation plan for integrating ChromaDB with Gemini using pydantic-graph to create a powerful RAG (Retrieval Augmented Generation) system.

## Overview of the Implementation

The solution will combine:
1. Existing ChromaDB integration for document storage and retrieval
2. Gemini LLM for generating responses based on retrieved documents
3. Pydantic-graph for structured workflow management

## Step-by-Step Implementation

### 1. Define Dependencies and State Models

First, create models for dependencies and state tracking:

```python
from dataclasses import dataclass, field
from typing import List, Optional
from chromadb import Collection
from pydantic_ai.models.vertexai import VertexAIModel
from google.cloud.aiplatform import Vertex
from typing_extensions import Annotated

@dataclass
class RAGDependencies:
    """Dependencies for RAG workflow."""
    chroma_collection: Collection
    gemini_model: VertexAIModel

@dataclass
class RAGState:
    """State for RAG workflow."""
    query: str
    retrieved_documents: List[dict] = field(default_factory=list)
    answer: Optional[str] = None
    sources: List[str] = field(default_factory=list)
```

### 2. Create Graph Nodes

Create dedicated nodes for each step in the RAG process:

```python
from pydantic_graph import BaseNode, Edge, End, GraphRunContext

@dataclass
class QueryNode(BaseNode[RAGState]):
    """Node to handle initial user query."""
    
    async def run(
        self, ctx: GraphRunContext[RAGState]
    ) -> Annotated[RetrieveNode, Edge(label="Retrieve documents")]:
        # Log the incoming query
        print(f"Processing query: {ctx.state.query}")
        return RetrieveNode()

@dataclass
class RetrieveNode(BaseNode[RAGState]):
    """Node to retrieve relevant documents from ChromaDB."""
    
    async def run(
        self, ctx: GraphRunContext[RAGState]
    ) -> Annotated[AnswerNode, Edge(label="Generate answer")]:
        # Get our dependencies
        collection = ctx.deps.chroma_collection
        
        # Query ChromaDB for relevant documents
        results = collection.query(
            query_texts=[ctx.state.query],
            n_results=5
        )
        
        # Store retrieved documents and metadata in state
        ctx.state.retrieved_documents = [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(
                results["documents"][0], 
                results["metadatas"][0]
            )
        ]
        
        # Store source information
        ctx.state.sources = [meta.get("source", "unknown") 
                            for meta in results["metadatas"][0]]
        
        return AnswerNode()

@dataclass
class AnswerNode(BaseNode[RAGState]):
    """Node to generate answer using Gemini based on retrieved documents."""
    
    async def run(
        self, ctx: GraphRunContext[RAGState]
    ) -> Annotated[End[str], Edge(label="Complete")]:
        # Get our model
        model = ctx.deps.gemini_model
        
        # Format context from retrieved documents
        context = "\n\n".join([
            f"Document {i+1}:\n{doc['content']}"
            for i, doc in enumerate(ctx.state.retrieved_documents)
        ])
        
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
        
        # Generate answer using Gemini
        result = await model.generate(prompt)
        ctx.state.answer = result.text
        
        return End(f"{ctx.state.answer}\n\nSources: {', '.join(ctx.state.sources)}")
```

### 3. Create and Configure the Graph

```python
from pydantic_graph import Graph

# Create the RAG graph
rag_graph = Graph[RAGState, RAGDependencies](
    nodes=[QueryNode, RetrieveNode, AnswerNode],
    start_node=QueryNode
)

# Generate a visualization of your graph
rag_graph.mermaid_save("rag_workflow.png", direction="TB")
```

### 4. Service Function to Run the Graph

Create a service function that integrates with your existing CLI and UI:

```python
async def run_rag_query(
    query: str, 
    collection_name: str = "my_docs",
    chroma_dir: str = "./chroma_db",
    project_id: Optional[str] = None
) -> str:
    """Run a RAG query through the graph workflow."""
    import chromadb
    import time
    from pydantic_ai.models.vertexai import VertexAIModel
    
    start_time = time.time()
    
    # Initialize ChromaDB
    chroma_client = chromadb.PersistentClient(path=chroma_dir)
    collection = chroma_client.get_collection(collection_name)
    
    # Initialize Gemini model
    gemini_model = VertexAIModel(
        model="gemini-1.5-pro",
        project_id=project_id,
        max_tokens=1024
    )
    
    # Create dependencies
    deps = RAGDependencies(
        chroma_collection=collection,
        gemini_model=gemini_model
    )
    
    # Create initial state with the query
    state = RAGState(query=query)
    
    # Run the graph
    result = await rag_graph.arun(state, deps)
    
    # Extract the result (which is the answer with sources)
    answer = result.value
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return {
        "answer": answer,
        "execution_time": execution_time
    }
```

### 5. CLI Integration

Update your CLI commands to use the RAG graph:

```python
# In commands/rag.py
import argparse
import asyncio
from research_agent.services import run_rag_query

def configure_parser(subparsers):
    parser = subparsers.add_parser(
        "rag",
        help="Query documents using RAG with Gemini"
    )
    parser.add_argument(
        "--query", 
        required=True,
        help="The question to ask about your documents"
    )
    parser.add_argument(
        "--collection",
        default="my_docs",
        help="ChromaDB collection name"
    )
    parser.add_argument(
        "--chroma-dir",
        default="./chroma_db",
        help="Directory for ChromaDB storage"
    )
    parser.add_argument(
        "--project-id",
        help="Google Cloud project ID for Vertex AI"
    )
    return parser

async def run_command(args):
    result = await run_rag_query(
        query=args.query,
        collection_name=args.collection,
        chroma_dir=args.chroma_dir,
        project_id=args.project_id
    )
    
    print(f"Answer: {result['answer']}")
    print(f"Execution time: {result['execution_time']:.2f} seconds")

def handle_command(args):
    asyncio.run(run_command(args))
```

### 6. Streamlit UI Integration

Add a RAG page to your Streamlit UI:

```python
# In ui/pages/rag_search.py
import streamlit as st
import asyncio
from research_agent.services import run_rag_query

def render_rag_page():
    st.title("Document Search with RAG")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        collection_name = st.text_input("Collection Name", value="my_docs")
        chroma_dir = st.text_input("ChromaDB Directory", value="./chroma_db")
        project_id = st.text_input("Google Cloud Project ID (optional)")
    
    # Main query area
    query = st.text_area("Enter your question:", height=100)
    
    # Only show search button if query is not empty
    if query:
        if st.button("Search", type="primary"):
            with st.spinner("Searching documents and generating answer..."):
                # Run the RAG query
                result = asyncio.run(run_rag_query(
                    query=query,
                    collection_name=collection_name,
                    chroma_dir=chroma_dir,
                    project_id=project_id
                ))
                
                # Display results
                st.markdown("### Answer")
                st.markdown(result["answer"])
                
                # Show execution metrics
                st.info(f"Query processed in {result['execution_time']:.2f} seconds")
```

### 7. Update Main Entry Points

Ensure your main entry points register the new RAG command:

```python
# In main.py or cli_entry.py
from research_agent.commands import gemini, ingest, rag

def register_commands(parser):
    subparsers = parser.add_subparsers(dest="command")
    
    # Register existing commands
    gemini.configure_parser(subparsers)
    ingest.configure_parser(subparsers)
    
    # Register new RAG command
    rag.configure_parser(subparsers)
    
    return parser
```

## Key Benefits of This Implementation

1. **Structured Workflow**: Uses pydantic-graph to create a maintainable, extensible research workflow
2. **Separation of Concerns**: Each node handles a specific task (querying, retrieval, answer generation)
3. **Visualizable Flow**: The graph can be visualized with mermaid to understand the workflow
4. **Integrated with Existing Code**: Builds on your existing ChromaDB and Gemini integrations
5. **Flexible Configuration**: Allows customization of collection names, ChromaDB directory, and project IDs
6. **Multiple Interfaces**: Accessible through both CLI and Streamlit UI

## Next Steps

1. **Extend the Graph**: Add new nodes for follow-up questions, refinement, or fact-checking
2. **Enhanced Retrieval**: Implement more sophisticated retrieval strategies (e.g., re-ranking)
3. **Context-Aware Generation**: Improve prompts to generate more accurate answers based on retrieved documents
4. **Evaluation Metrics**: Add nodes to evaluate the quality of generated answers
5. **User Feedback Integration**: Allow users to provide feedback that improves future responses

## References

- [Pydantic AI RAG Example](https://ai.pydantic.dev/examples/rag/)
- [Pydantic AI Graph Documentation](https://ai.pydantic.dev/graph/#genai-example) 