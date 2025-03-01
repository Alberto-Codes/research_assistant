# Research Agent

A Pydantic Graph AI Agent implementation with Gemini integration.

## Overview

This project implements an AI agent using Pydantic Graph and integrates with Google's Gemini Flash 2.0 model through Vertex AI. The implementation includes both actual API connections and mock clients for local development and testing.

## Features

- Integrates with Google Vertex AI using Gemini models
- Uses Pydantic-AI for streamlined LLM interaction
- Graph-based workflow for AI agent implementation
- Command-line interface for prompt-based interactions
- Streamlit UI for interactive chat experiences
- Document ingestion capabilities for knowledge retrieval
- Multi-page UI with both chat and document management
- Unified entry point for both CLI and UI interfaces
- Retrieval Augmented Generation (RAG) for document-based question answering

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd research_agent
   ```

2. Install dependencies with pipenv:
   ```
   pipenv install
   ```

## Usage

### Command Line Interface

The project provides a command-line interface for running the AI agent:

```
research_agent gemini --prompt "Your question here" [--project-id PROJECT_ID] [--log-level LEVEL] [--log-file PATH]
```

Options:
- `--prompt`: The prompt to send to the Gemini model (required)
- `--project-id`: Google Cloud project ID (optional)
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO)
- `--log-file`: Specify a file to save logs (optional)

Examples:

```bash
# Basic usage
research_agent gemini --prompt "What is machine learning?"

# With debug logging
research_agent gemini --prompt "Explain neural networks" --log-level DEBUG

# Saving logs to a file
research_agent gemini --prompt "How does reinforcement learning work?" --log-file logs/gemini.log

# Specifying a project ID
research_agent gemini --prompt "Explain transformer architecture" --project-id your-project-id
```

### Document Ingestion

You can ingest documents into a ChromaDB collection for later retrieval:

```
research_agent ingest --data-dir "./data" --collection "my_collection" [--chroma-dir "./chroma_db"]
```

Options:
- `--data-dir`: Directory containing documents to ingest (required)
- `--collection`: Name of the ChromaDB collection to use (required)
- `--chroma-dir`: Directory where ChromaDB data should be persisted (default: "./chroma_db")

### RAG Queries

You can query your document collections using Retrieval Augmented Generation (RAG):

```
research_agent rag --query "Your question about documents" --collection "my_collection" [--chroma-dir "./chroma_db"]
```

Options:
- `--query`: The question to ask about your documents (required)
- `--collection`: Name of the ChromaDB collection to query (required)
- `--chroma-dir`: Directory where ChromaDB data is stored (default: "./chroma_db")
- `--project-id`: Google Cloud project ID (optional)

Examples:

```bash
# Basic usage
research_agent rag --query "What information is in my documents about machine learning?"

# Querying a specific collection
research_agent rag --query "Summarize the documents" --collection "research_papers"
```

The RAG system will:
1. Retrieve relevant documents based on your query
2. Provide the document context to the Gemini model
3. Generate an answer that cites the relevant documents
4. Display timing metrics for retrieval and generation

### Streamlit UI Interface

For an interactive experience with both chat and document management capabilities, use the Streamlit-based interface:

```
python -m src.main ui
```

You can also specify a custom port:

```
python -m src.main ui --port 8888
```

The Streamlit interface will automatically open in your browser, or you can visit `http://localhost:8501` (or your specified port).

#### Streamlit Features

The Streamlit UI includes multiple pages:

1. **Chat with Gemini**: Interact with the Gemini model in a chat interface
   - Configure system prompts to customize the assistant behavior
   - Enable/disable chat history for contextual conversations
   - View response metrics and debugging information

2. **Document Ingestion**: Upload and manage documents
   - Upload multiple documents at once
   - Organize documents into collections
   - View detailed ingestion results
   - Configure ChromaDB storage location

### Alternative Interface

You can also use the previous CLI-based approach to launch the UI:

```
python -m research_agent.ui.cli_entry --app gemini
```

### Development Example

For development and testing without setting up Google Cloud authentication, you can use the provided example:

```
python examples/gemini_pydantic_ai_example.py "Your question here"
```

## Authentication for Vertex AI

To use the actual Vertex AI service:

1. Install the Google Cloud CLI
2. Authenticate with `gcloud auth application-default login`
3. Make sure you have the Vertex AI API enabled in your Google Cloud project

## Project Structure

- `src/main.py`: Main entry point for both CLI and UI interfaces
- `src/research_agent/`: Main package
  - `api/`: API layer including services
  - `cli/`: Command-line interface and commands
  - `core/`: Core implementation including nodes, graph, and dependencies
  - `ui/`: UI components (Streamlit)
    - `streamlit/`: Streamlit web UI
      - `app.py`: Multi-page Streamlit application
      - `gemini_chat.py`: Chat interface for Gemini
      - `document_ingestion.py`: Document ingestion interface
- `examples/`: Example scripts for testing and demonstration
- `tests/`: Unit tests

## Dependencies

- `pydantic-ai`: For LLM interaction and Vertex AI integration
- `pydantic-graph`: For graph-based workflow
- `streamlit`: For the web-based UI
- `google-cloud-aiplatform`: For Vertex AI integration
- `chromadb`: For document storage and vector database capabilities

## Testing Approach

This project follows best practices for testing, with a focus on keeping production code and test code separate:

### Test-First Development
- Unit tests for all components
- Integration tests for workflows
- Mock clients for external services (Vertex AI)
- Streamlit UI tests using `streamlit.testing.v1.AppTest`

### Code Coverage
- Comprehensive code coverage tracking using pytest-cov
- PowerShell script (`run_tests.ps1`) at the project root for easy coverage testing
- HTML report generation with browser integration
- Current coverage is at 42% with plans for improvement
- Customizable coverage settings via `.coveragerc`
- Run coverage tests with `.\run_tests.ps1 coverage-report` to see detailed reports

### Mock Clients
We've deprecated the practice of including mock implementations in production code. Instead:
- All mock implementations are kept in test files
- We use pytest fixtures for providing test doubles
- Test against protocols rather than concrete implementations

### UI Testing
For Streamlit UI testing, we use Streamlit's AppTest framework to test UI components without running a full browser:
- Test the presence and configuration of UI elements
- Simulate user interactions
- Mock async streaming responses
- Test UI state changes

For more details, see the [Testing Guide](TESTING.md).

## Project Structure

The project follows a clean separation of concerns:

```
src/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point for CLI and UI
├── research_agent/
│   ├── __init__.py          # Package initialization
│   ├── core/                # Core business logic
│   │   ├── dependencies.py  # Dependency injection definitions
│   │   ├── graph.py         # Graph definition
│   │   ├── logging_config.py # Centralized logging configuration
│   │   ├── nodes.py         # Node definitions
│   │   └── state.py         # State class definition
│   ├── api/                 # API layer
│   │   └── services.py      # Service functions for interfaces
│   ├── cli/                 # Command-line interface
│   │   ├── commands/        # CLI command implementations
│   │   │   ├── gemini.py    # Gemini command implementation
│   │   │   └── ingest.py    # Document ingestion command
│   │   └── main.py          # CLI entry point
│   └── ui/                  # User interface layer
│       ├── streamlit/       # Streamlit web UI
│       │   ├── app.py       # Multi-page Streamlit application
│       │   ├── gemini_chat.py # Gemini chat interface
│       │   └── document_ingestion.py # Document ingestion interface
│       └── web/             # (Future) FastAPI web API
```

## Code Quality

This project follows strict code quality guidelines based on the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html). We use the following tools to maintain code quality:

### Static Analysis Tools

- **Black**: Enforces a consistent code style
- **isort**: Organizes imports according to best practices
- **Flake8**: Checks for style guide enforcement and common errors
- **Pylint**: Performs deeper static analysis
- **Mypy**: Provides static type checking
- **Bandit**: Scans for security vulnerabilities

### Setup and Usage

We use `pre-commit` hooks to run these tools automatically before each commit. To set up the development environment with all code quality tools:

```bash
# Install all development dependencies
pipenv install --dev

# Run tests
.\run_tests.ps1 test

# Run coverage tests with report
.\run_tests.ps1 coverage-report

# Run CLI tests
.\run_cli.ps1 all

# Run UI
.\run_ui.ps1
```

### Error Handling

This project follows consistent error handling practices:

1. All functions have clear type annotations and docstrings
2. Exceptions are caught at appropriate levels and contextualized
3. Structured logging is used for debugging and tracing with configurable levels
4. Custom exceptions are used for domain-specific errors

#### Logging Configuration

The application uses a centralized logging system that can be configured via command line:

```bash
# Run with debug level logging
research_agent gemini --prompt "Your question" --log-level DEBUG

# Save logs to a file
research_agent gemini --prompt "Your question" --log-file logs/app.log
```

Logging features include:
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Console and/or file output
- Structured format with timestamps, levels, and module names
- Module-specific loggers for targeted debugging

## Graph-Based Workflow

The project uses `pydantic-graph` to create workflows with connected nodes:

### RAG (Retrieval Augmented Generation) Workflow

The RAG workflow consists of three main nodes:

1. `QueryNode` - Processes the user's query
2. `RetrieveNode` - Retrieves relevant documents from ChromaDB based on the query
3. `AnswerNode` - Generates an answer using Gemini based on retrieved documents and query

The RAG workflow provides:
- Document-grounded responses based on your data
- Automatic citation of sources
- Detailed timing metrics for performance analysis
- Robust error handling with graceful fallbacks

### Document Ingestion Workflow

The document ingestion workflow uses:
1. `ChromaDBIngestionNode` - Processes and stores documents in the vector database

Each workflow executes its nodes in sequence, maintaining state between nodes to pass information through the graph.

## Document Management

The project includes a complete document management system using ChromaDB for vector storage:

1. Document ingestion through both CLI and UI interfaces
2. Support for various document formats
3. Collection-based organization
4. Persistent storage of document embeddings
5. Built using a modular graph-based workflow

## Dependency Management

This project uses `pipenv` for dependency management. The main dependencies are:

- `pydantic-graph` - For defining the graph workflow
- `pydantic-ai` - For LLM integration
- `streamlit` - For the web-based UI
- `chromadb` - For document storage and retrieval

## Recent Updates

The most significant recent updates include:

1. **Consolidated entry points** into a single source of truth in `src/main.py`
2. **Document ingestion UI** added to the Streamlit interface
3. **Multi-page Streamlit application** with navigation between features
4. **Enhanced service layer** for document management

For more details on the project status and recent changes, see the [Project Status](docs/PROJECT_STATUS.md) document.