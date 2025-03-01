# Retrieval Augmented Generation (RAG) Example with Pydantic AI

This example demonstrates how to build a simple Retrieval Augmented Generation (RAG) system using Pydantic AI. It creates a document retrieval tool that can search through a collection of documents and uses it to answer questions based on the retrieved information.

## What is RAG?

Retrieval Augmented Generation (RAG) is a technique that enhances Large Language Models by retrieving relevant information from a knowledge base before generating a response. This approach combines the strengths of both retrieval-based and generation-based methods:

1. **Retrieval**: Finding relevant documents or information from a knowledge base
2. **Augmentation**: Enhancing the context given to the LLM with the retrieved information
3. **Generation**: Using the LLM to generate a coherent, informative response based on the augmented context

RAG helps to ground LLM responses in factual information, reducing hallucinations and providing more accurate answers.

## How This Example Works

The example demonstrates a simple end-to-end RAG implementation with the following components:

1. **Document Store**: A collection of documents with vector search capabilities using ChromaDB
2. **Embedding Generation**: ChromaDB handles the embedding generation automatically
3. **Retrieval Tool**: A Pydantic AI tool that searches for relevant documents based on semantic similarity
4. **RAG Agent**: An Agent instance that uses the retrieval tool to augment its responses

## Research Agent RAG Implementation

In the Research Agent project, we've implemented a comprehensive RAG system using Pydantic-Graph:

1. **Graph-Based Workflow**: The RAG process is implemented as a graph with three nodes:
   - **QueryNode**: Handles the initial user query
   - **RetrieveNode**: Retrieves relevant documents from ChromaDB
   - **AnswerNode**: Generates an answer using Gemini based on retrieved documents

2. **Robust Handling**: The implementation includes:
   - Detailed timing metrics for retrieval and generation phases
   - Comprehensive error handling for document retrieval and answer generation 
   - Support for both synchronous and asynchronous document retrieval
   - Fallback mechanisms for missing source information
   - 100% test coverage with comprehensive test cases

3. **CLI Integration**: Easy access through the command line:
   ```
   research_agent rag --query "Your question" --collection "your_collection"
   ```

4. **Performance Metrics**: Each RAG query returns detailed timing information:
   - Retrieval time (how long it took to find relevant documents)
   - Generation time (how long it took the model to generate an answer)
   - Total execution time (end-to-end processing time)

## Requirements

To run this example, you'll need the following packages:

- pydantic-ai
- openai
- chromadb

You can install these with pip:

```bash
pip install pydantic-ai openai chromadb
```

You'll also need to set up your OpenAI API key:

```bash
export OPENAI_API_KEY=your-api-key-here
```

## Running the Example

To run the example:

```bash
python rag_example.py
```

This will:
1. Create sample documents
2. Initialize a ChromaDB collection for vector search
3. Add documents to the ChromaDB collection
4. Set up a RAG agent with a document retrieval tool
5. Answer a few example questions using RAG

## What is ChromaDB?

[ChromaDB](https://docs.trychroma.com/docs/overview/introduction) is an open-source embedding database designed specifically for AI applications. It makes it easy to:

- Store and manage embedding vectors and their metadata
- Perform semantic search using various similarity metrics
- Scale from local development to production deployment

ChromaDB is a great choice for RAG applications because:

- It handles the embedding generation automatically
- It provides efficient vector search capabilities
- It supports multiple embedding models
- It can be run in-memory for development or persisted for production

## Recent Improvements in Research Agent

Our latest updates to the Research Agent RAG system include:

- Enhanced RetrieveNode with improved coroutine handling for various query responses
- Added robust error handling for awaitable results in document retrieval
- Fixed mock function signatures in tests to properly align with pydantic-graph Graph.run method
- Improved debug logging throughout the RAG workflow for better troubleshooting
- Updated ChromaDB integration to handle API updates in version 0.6.0
- Added source field fallback to use filename when source is not available
- Enhanced document citation for better content attribution

## Extending the Example

Here are some ways you could extend this example:

1. **Load Real Documents**: Modify the code to load documents from files or a database
2. **Custom Document Processing**: Add preprocessing steps for documents, such as chunking, summarization, etc.
3. **Different Embedding Models**: Configure ChromaDB to use a specific embedding function
4. **Advanced Retrieval**: Implement hybrid search combining keyword and semantic search
5. **Streaming Responses**: Modify the agent to stream responses as they're generated

## Learn More

For more information:
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/docs/overview/introduction)
- [Research Agent Documentation](../docs/next_steps.md) 