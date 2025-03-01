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