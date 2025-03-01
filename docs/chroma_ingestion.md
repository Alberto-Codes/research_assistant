# ChromaDB Document Ingestion

This document explains how to use the ChromaDB document ingestion feature in the Research Agent.

## Overview

The ChromaDB document ingestion feature allows you to:
- Load documents from files in a directory
- Ingest documents into a persistent ChromaDB collection
- Use these documents later for vector search and retrieval

## Prerequisites

Make sure you have installed the required dependencies:

```bash
pip install -e .
# or
pipenv install
```

The feature requires `chromadb` package, which should be installed automatically.

## Usage

### Command Line Interface

You can use the CLI script to ingest documents from a directory:

```bash
python -m research_agent.cli.ingest_documents --data-dir ./data --collection my_collection --chroma-dir ./chroma_db
```

Options:
- `--data-dir`: Directory containing documents to ingest (default: `./data`)
- `--collection`: Name of the ChromaDB collection to use (default: `default_collection`)
- `--chroma-dir`: Directory where ChromaDB data should be persisted (default: `./chroma_db`)

### Programmatic Usage

You can also use the document ingestion graph programmatically:

```python
import asyncio
from research_agent.core.doc_graph import run_document_ingestion_graph

async def ingest_documents():
    documents = [
        "This is the first document content.",
        "This is the second document content."
    ]
    
    document_ids = ["doc_1", "doc_2"]
    metadata = [
        {"source": "example", "type": "text"},
        {"source": "example", "type": "text"}
    ]
    
    result, state, errors = await run_document_ingestion_graph(
        documents=documents,
        collection_name="my_collection",
        document_ids=document_ids,
        metadata=metadata,
        persist_directory="./chroma_db"
    )
    
    if errors:
        print("Errors:", errors)
    else:
        print("Documents ingested successfully.")
        print(f"Ingestion time: {state.total_time:.3f} seconds")

# Run the function
asyncio.run(ingest_documents())
```

## Data Directory Structure

The document ingestion feature expects text files in the data directory. Each text file will be considered a separate document.

Example directory structure:
```
data/
  ├── document1.txt
  ├── document2.txt
  └── document3.txt
```

## ChromaDB Storage

The documents are stored in a persistent ChromaDB collection. The data is saved in the directory specified by the `--chroma-dir` option (default: `./chroma_db`).

This allows you to:
- Persist your document embeddings between runs
- Use the same collection across different sessions
- Scale to large document collections efficiently

## Next Steps

After ingesting documents, you can:
1. Query the collection for similar documents
2. Retrieve documents based on semantic similarity
3. Build applications that use the ingested documents as a knowledge base

For more information on how to use ChromaDB for queries, refer to the [ChromaDB documentation](https://docs.trychroma.com/). 