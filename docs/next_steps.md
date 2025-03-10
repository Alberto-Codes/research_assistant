# ChromaDB and Gemini Integration with Pydantic-Graph

## Implementation Status

**Current Status: Nearly Complete**

- ✅ **Step 1: Define Dependencies and State Models** - Completed
  - RAGDependencies and RAGState classes implemented
  - 100% test coverage achieved for these components
  - Classes available in `src/research_agent/core/rag/dependencies.py` and `src/research_agent/core/rag/state.py`

- ✅ **Step 2: Create Graph Nodes** - Completed
  - QueryNode, RetrieveNode, and AnswerNode classes implemented
  - Robust error handling in each node
  - Enhanced RetrieveNode with improved coroutine handling and better debug logging
  - Detailed timing metrics for retrieval and generation phases
  - 100% test coverage with comprehensive test cases
  - Classes available in `src/research_agent/core/rag/nodes.py`

- ✅ **Step 3: Create and Configure the Graph** - Completed
  - Graph configuration with node connections implemented
  - Singleton graph instance created for reuse
  - Error handling for graph execution failures
  - Available in `src/research_agent/core/rag/graph.py`

- ✅ **Step 4: Service Function to Run the Graph** - Completed
  - `run_rag_query` function implemented with proper timing metrics
  - Consistent interface for CLI and UI integration
  - Detailed error handling and logging
  - Return structure with answer and timing information
  - Fixed test implementation to properly mock graph run function
  
- ✅ **Step 5: CLI Integration** - Completed
  - RAG command implemented in `commands/rag.py`
  - Proper argument parsing and validation
  - Integration with the service layer
  - Error handling and user feedback
  
- ✅ **Step 6: Streamlit UI Infrastructure** - Partially Completed
  - Basic UI components created for RAG search in `ui/streamlit/rag_search.py`
  - `list_collections` function fixed to work with latest ChromaDB API
  - `execute_rag_query` function implemented to connect UI with backend services
  - Comprehensive test suite created with 76% coverage for the rag_search module
  - Basic UI rendering functionality implemented
  - Still need to complete integration with the main navigation
  
- ❌ **Step 7: Update Main Entry Points** - Not started

**Next Steps:**
1. Complete the Streamlit RAG UI page integration with the main navigation
2. Improve async test structure to eliminate remaining warnings:
   - Refactor unittest-style async tests to pure pytest-style to avoid coroutine warnings
   - Properly implement async tests to ensure coroutines are awaited correctly
   - Address the deprecation warnings related to test functions returning non-None values
3. Update main entry points to include the RAG UI page in navigation
4. Add comprehensive user documentation for RAG functionality
5. ✅ **Integrate Docling for Enhanced Document Processing**:
   - ✅ Add Docling library integration for advanced document understanding
   - ✅ Create DoclingProcessor service for handling multiple document formats
   - ✅ Implement document structure understanding for better context retrieval
   - ✅ Add comprehensive test suite for document processing
   - ✅ Implement proper mocking for tests without requiring Docling installation
   - ✅ Convert tests to pytest style for better integration with testing infrastructure
   - ❌ Update document ingestion UI to support and preview various file formats
   - ❌ Update the document ingestion pipeline to use DoclingProcessor
   - ❌ Create adapters to transform DoclingDocument objects to ChromaDB-compatible format
   - ❌ Integrate OCR functionality for processing scanned documents and images

## Docling Integration Plan

The current document processing pipeline has limited format support and lacks advanced document understanding capabilities. Integrating Docling (https://ds4sd.github.io/docling/) will significantly enhance these capabilities:

### Benefits of Docling Integration

1. **Multi-format Support**: Process PDF, DOCX, XLSX, HTML, images, and more file formats
2. **Advanced PDF Understanding**: Extract page layout, reading order, tables, and structural elements
3. **Unified Document Representation**: DoclingDocument provides a consistent format for all document types
4. **Local Processing**: Run document processing locally for sensitive data and air-gapped environments
5. **OCR Capabilities**: Process scanned documents and images with text extraction
6. **Enhanced Metadata**: Extract and utilize document metadata for better search and filtering
7. **Structure-aware Processing**: Maintain document structure during chunking for more coherent retrieval

### Detailed Implementation Approach

1. **Core Integration**: ✅ COMPLETED
   - ✅ Add Docling as a dependency to the project (`docling>=2.25.0`)
   - ✅ Created a `DoclingProcessor` service in the core module:
     ```python
     # src/research_agent/core/document_processing/docling_processor.py
     from dataclasses import dataclass
     from typing import List, Optional
     from docling.document_converter import DocumentConverter
     from docling.options import PipelineOptions
     
     @dataclass
     class DoclingProcessorOptions:
         """Configuration options for Docling processing."""
         enable_ocr: bool = True
         extract_tables: bool = True
         extract_images: bool = True
         language: Optional[str] = None
         chunk_size: int = 1000
         chunk_overlap: int = 200
     
     class DoclingProcessor:
         """Processes documents using Docling."""
         
         def __init__(self, options: Optional[DoclingProcessorOptions] = None):
             self.options = options or DoclingProcessorOptions()
             self.converter = DocumentConverter()
             
         def process_file(self, file_path: str):
             """Process a single file with Docling."""
             pipeline_options = PipelineOptions(
                 ocr_language=self.options.language,
                 extract_tables=self.options.extract_tables,
                 extract_images=self.options.extract_images,
             )
             
             result = self.converter.convert(file_path, pipeline_options=pipeline_options)
             return result.document
     ```

2. **ChromaDB Adapter**: ❌ NOT STARTED
   - Develop adapters to convert DoclingDocument objects to ChromaDB-compatible format:
     ```python
     # src/research_agent/core/document_processing/chromadb_adapter.py
     import hashlib
     import os
     from typing import List, Dict, Any, Tuple
     from docling.document import DoclingDocument
     from docling.document.chunking import chunk_document
     
     class DoclingChromaDBAdapter:
         """Adapts DoclingDocument objects for ChromaDB ingestion."""
         
         def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
             self.chunk_size = chunk_size
             self.chunk_overlap = chunk_overlap
         
         def document_to_chunks(self, document: DoclingDocument, source_path: str) -> List[Tuple[str, str, Dict[str, Any]]]:
             """Convert a DoclingDocument to a list of chunks for ChromaDB."""
             # Extract document metadata
             metadata_base = {
                 "source": source_path,
                 "filename": os.path.basename(source_path),
                 "format": os.path.splitext(source_path)[1][1:].lower(),
                 "document_type": document.document_type,
             }
             
             # Use Docling's chunking functionality
             chunks = chunk_document(
                 document, 
                 chunk_size=self.chunk_size, 
                 chunk_overlap=self.chunk_overlap
             )
             
             # Convert chunks to ChromaDB format: (id, text, metadata)
             result = []
             for i, chunk in enumerate(chunks):
                 # Create chunk-specific metadata
                 metadata = {
                     **metadata_base,
                     "chunk_index": i,
                     "page_numbers": chunk.source_pages,
                     "section_title": chunk.section_title,
                     "is_table": chunk.is_table,
                     "is_figure": chunk.is_figure,
                 }
                 
                 # Generate unique ID
                 content = chunk.text + str(metadata)
                 chunk_id = hashlib.md5(content.encode()).hexdigest()
                 
                 result.append((chunk_id, chunk.text, metadata))
                 
             return result
     ```

3. **✅ Testing Implementation**: COMPLETED
   - ✅ Created unit tests for DoclingProcessor and options classes
   - ✅ Implemented integration tests that use mock Docling functions
   - ✅ Converted all tests to pytest-style for better integration with existing infrastructure
   - ✅ Added test data for document processing tests
   - ✅ Ensured tests run successfully with the existing test scripts:
     - `run_tests.ps1`: For running unit and integration tests
     - `run_cli.ps1`: For testing CLI functionality 
     - `run_ui.ps1`: For testing UI integration

4. **Update Document Ingestion Service**: ❌ NOT STARTED
   - Modify the existing ingestion service to use Docling:
     ```python
     # Update in src/research_agent/services.py
     async def ingest_documents_with_docling(
         data_dir: str,
         collection_name: str,
         chroma_dir: str = "./chroma_db",
         enable_ocr: bool = True,
         chunk_size: int = 1000,
         chunk_overlap: int = 200
     ):
         """Ingest documents from a directory using Docling and store in ChromaDB."""
         # Initialize Docling processor
         processor = DoclingProcessor(DoclingProcessorOptions(
             enable_ocr=enable_ocr,
             chunk_size=chunk_size,
             chunk_overlap=chunk_overlap
         ))
         
         # Initialize ChromaDB adapter
         adapter = DoclingChromaDBAdapter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
         
         # Process documents and add to ChromaDB
         # [Implementation details...]
     ```

5. **RAG Enhancements**: ❌ NOT STARTED
   - Modify the RetrieveNode to leverage document structure:
     ```python
     # Enhanced in src/research_agent/core/rag/nodes.py
     @dataclass
     class RetrieveNode(BaseNode[RAGState]):
         """Node to retrieve relevant documents with structure awareness."""
         
         async def run(self, ctx: GraphRunContext[RAGState]):
             # Query ChromaDB with structure awareness
             # [Implementation details...]
             
             # Apply document re-ranking based on structure
             reranked_docs = self._rerank_documents(retrieved_docs, ctx.state.query)
             
             # [Additional implementation...]
             
         def _rerank_documents(self, documents, query):
             """Rerank documents based on structure and relevance."""
             # Prioritize based on query content and document structure
             # [Implementation details...]
     ```

6. **UI Enhancements**:
   - Update the document ingestion UI to handle multiple file formats:
     ```python
     # src/research_agent/ui/streamlit/document_ingestion.py
     def render_document_ingestion_ui():
         """Render the document ingestion UI with Docling support."""
         # [UI implementation with file upload for multiple formats]
         
         uploaded_files = st.file_uploader(
             "Upload documents", 
             accept_multiple_files=True,
             type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg", "txt", "html"]
         )
         
         # [Rest of implementation...]
     ```

7. **Testing Strategy**:
   - Create unit tests for DoclingProcessor and adapter
   - Add integration tests for the complete pipeline
   - Update CLI tests to test Docling ingestion
   - Ensure compatibility with existing test scripts:
     - `run_tests.ps1`: For running unit and integration tests
     - `run_cli.ps1`: For testing CLI functionality with Docling
     - `run_ui.ps1`: For testing UI integration with Docling

### Future Enhancements After Docling Integration

Now that the core `DoclingProcessor` and test suite have been implemented, the next priorities are:

1. **Complete ChromaDB Integration**:
   - Implement the `DoclingChromaDBAdapter` to convert processed documents to ChromaDB format
   - Update the document ingestion pipeline to use the new processor
   - Enhance metadata extraction for better document search and filtering
   - Update the RAG system to make use of document structure information

2. **Document Preview Capabilities**:
   - Implement document preview in the UI to visualize document structure
   - Display tables, figures, and document layout as they appear in the original
   - Add thumbnail generation for documents in collections
   - Create a side-by-side view of original document and extracted text

3. **Enhanced Search and Filtering**:
   - Implement faceted search based on document structure
   - Enable filtering by document type, section, table/figure content
   - Add semantic search within specific document sections
   - Integrate keyword highlighting in search results

4. **Document Analytics Dashboard**:
   - Create visualizations of document collections
   - Provide insights on document types, content distribution
   - Generate word clouds and topic modeling from document collections
   - Track most frequently accessed documents and sections

5. **Multimodal RAG Capabilities**:
   - Enhance RAG to utilize images and tables in document understanding
   - Implement visual question answering for figures and diagrams
   - Add table-specific reasoning for numerical data
   - Create specialized prompts for different document components

6. **Advanced Document Processing**:
   - Implement chart and graph understanding for data visualization
   - Add language detection and translation capabilities
   - Create specialized extractors for domain-specific content (legal, scientific, etc.)
   - Develop custom document templates for common document types

These enhancements will transform the Research Agent into a comprehensive document intelligence platform capable of understanding and retrieving information from diverse document formats with high fidelity and context awareness.

## Test Suite Improvements

The test suite has been substantially improved, but there are still some issues to resolve around async testing:

### Current Test Structure Issues

The current test implementation mixes unittest-style tests with pytest's asyncio functionality, leading to warnings:

1. **Coroutine Warnings**: Test methods decorated with `@pytest.mark.asyncio` are not being properly awaited within the unittest framework:
   ```
   RuntimeWarning: coroutine 'TestClass.test_async_method' was never awaited
   ```

2. **Deprecation Warnings**: Test methods returning values (common in async tests) trigger unittest deprecation warnings:
   ```
   DeprecationWarning: It is deprecated to return a value that is not None from a test case
   ```

### Proposed Solutions

1. **Convert to Pure Pytest**: Transition from unittest.TestCase classes to pure pytest-style test functions for async tests:
   ```python
   # Instead of:
   class TestClass(unittest.TestCase):
       @pytest.mark.asyncio
       async def test_method(self):
           # test code
           return None
   
   # Use:
   @pytest.mark.asyncio
   async def test_function():
       # test code
       # No need to return None
   ```

2. **Proper Awaiting of Async Methods**: Ensure all async methods are properly awaited within the test runner:
   ```python
   # For any tests that must remain in unittest style:
   class TestClass(unittest.TestCase):
       def test_method(self):
           result = asyncio.run(self._async_test_implementation())
           self.assertEqual(result, expected_value)
       
       async def _async_test_implementation(self):
           # Async test code here
           return result
   ```

3. **Consistent Async Pattern**: Establish a consistent pattern for async testing throughout the codebase:
   - Use `@pytest.mark.asyncio` only with pytest-style test functions, not unittest methods
   - Explicitly use `asyncio.run()` in unittest test methods that need to call async code
   - Never return non-None values from unittest test methods

These improvements will help eliminate the remaining warnings and make the test suite more maintainable.

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

### 6. Streamlit UI Infrastructure

The RAG UI infrastructure has been partially implemented with the following components:

```python
# In ui/streamlit/rag_search.py
import streamlit as st
import asyncio
import chromadb
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_ai.models.agent import Agent
from research_agent.core.rag.graph import run_rag_query

def list_collections(chroma_dir="./chroma_db"):
    """List available collections in ChromaDB."""
    try:
        client = chromadb.PersistentClient(path=chroma_dir)
        return client.list_collections()
    except Exception as e:
        st.error(f"Error listing collections: {e}")
        return []

async def execute_rag_query(
    query: str,
    collection_name: str = "my_docs",
    chroma_dir: str = "./chroma_db",
    project_id: str = None,
    model_name: str = "gemini-1.5-pro",
    region: str = "us-central1"
):
    """Execute a RAG query and return results."""
    try:
        # Initialize ChromaDB
        client = chromadb.PersistentClient(path=chroma_dir)
        collection = client.get_collection(collection_name)
        
        # Check if the collection has documents
        doc_count = collection.count()
        if doc_count == 0:
            return {
                "answer": "Collection is empty. Please ingest documents first.",
                "retrieval_time": 0,
                "generation_time": 0,
                "total_time": 0
            }
        
        # Initialize the Gemini model and agent
        vertex_model = VertexAIModel(
            model_name=model_name, 
            project_id=project_id,
            region=region
        )
        agent = Agent(vertex_model)
        
        # Run the RAG query
        result = await run_rag_query(
            query=query,
            chroma_collection=collection,
            gemini_model=agent,
            project_id=project_id
        )
        
        return result
        
    except Exception as e:
        return {
            "answer": f"Error executing query: {str(e)}",
            "retrieval_time": 0,
            "generation_time": 0,
            "total_time": 0
        }

def render_rag_search_ui():
    """Render the RAG search UI."""
    st.title("Document Search with RAG")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        chroma_dir = st.text_input("ChromaDB Directory", value="./chroma_db")
        
        # List available collections
        collections = list_collections(chroma_dir)
        if collections:
            collection_name = st.selectbox(
                "Select Collection", 
                options=collections,
                index=0
            )
        else:
            st.warning("No collections found. Please ingest documents first.")
            collection_name = ""
        
        # Advanced options
        with st.expander("Advanced Options"):
            project_id = st.text_input("Google Cloud Project ID (optional)")
            model_name = st.selectbox(
                "Model", 
                options=["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                index=0
            )
            region = st.text_input("Region", value="us-central1")
    
    # Query input area
    query = st.text_area("Enter your question about the documents:", height=100)
    
    # Check if we can perform a search
    can_search = collections and query
    
    if query:
        if st.button("Search Documents", disabled=not can_search):
            with st.spinner("Searching documents and generating answer..."):
                # Execute the query
                result = asyncio.run(execute_rag_query(
                    query=query,
                    collection_name=collection_name,
                    chroma_dir=chroma_dir,
                    project_id=project_id,
                    model_name=model_name,
                    region=region
                ))
                
                # Display the answer
                st.markdown("### Answer")
                st.markdown(result["answer"])
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Retrieval Time", f"{result['retrieval_time']:.2f}s")
                with col2:
                    st.metric("Generation Time", f"{result['generation_time']:.2f}s")
                with col3:
                    st.metric("Total Time", f"{result['total_time']:.2f}s")
```

To complete the UI integration, the component will need to be registered in the main Streamlit application and added to the navigation.

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