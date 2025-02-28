# Research Agent

A Pydantic Graph AI Agent implementation with Gemini integration.

## Overview

This project implements an AI agent using Pydantic Graph and integrates with Google's Gemini Flash 2.0 model through Vertex AI. The implementation includes both actual API connections and mock clients for local development and testing.

## Features

- Integrates with Google Vertex AI using Gemini models
- Uses Pydantic-AI for streamlined LLM interaction
- Graph-based workflow for AI agent implementation
- Command-line interface for prompt-based interactions
- Mock implementation for local testing without API credentials

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

#### Hello World Example

```
python -m research_agent.cli.commands hello [--prefix PREFIX] [--use-custom-llm]
```

#### Gemini AI Agent

```
python -m research_agent.cli.commands gemini --prompt "Your question here" [--project-id PROJECT_ID] [--use-mock-gemini]
```

Options:
- `--prompt`: The prompt to send to the Gemini model (required)
- `--project-id`: Google Cloud project ID (optional)
- `--use-mock-gemini`: Use the mock Gemini client for local testing without authentication

### Gemini Chat UI

For an interactive chat experience with Gemini models, you can use the Streamlit-based chat interface:

```
streamlit run src/research_agent/ui/streamlit/gemini_chat.py
```

This opens a web interface where you can:
- Chat with the Gemini model in real-time with streaming responses
- Configure system prompts that define the assistant's behavior
- Toggle conversation memory on/off
- View detailed response metrics
- Save your conversation history as JSON files

The chat UI features a completely refactored async implementation that ensures reliable streaming and supports multi-turn conversations. Recent improvements include enhanced error handling and robust event loop management.

### Development Example

For development and testing without setting up Google Cloud authentication, you can use the provided example:

```
python examples/gemini_pydantic_ai_example.py "Your question here"
```

Or use the CLI with the mock client:

```
python -m research_agent.cli.commands gemini --prompt "Your question here" --use-mock-gemini
```

## Authentication for Vertex AI

To use the actual Vertex AI service:

1. Install the Google Cloud CLI
2. Authenticate with `gcloud auth application-default login`
3. Make sure you have the Vertex AI API enabled in your Google Cloud project

## Project Structure

- `src/research_agent/`: Main package
  - `api/`: API layer including services
  - `cli/`: Command-line interface
  - `core/`: Core implementation including nodes, graph, and dependencies
  - `ui/`: UI components (Streamlit)
- `examples/`: Example scripts for testing and demonstration
- `tests/`: Unit tests

## Dependencies

- `pydantic-ai`: For LLM interaction and Vertex AI integration
- `pydantic-graph`: For graph-based workflow

## Testing Approach

This project follows best practices for testing, with a focus on keeping production code and test code separate:

### Test-First Development
- Unit tests for all components
- Integration tests for workflows
- Mock clients for external services (Vertex AI)

### Mock Clients
We've deprecated the practice of including mock implementations in production code. Instead:
- All mock implementations are kept in test files
- We use pytest fixtures for providing test doubles
- Test against protocols rather than concrete implementations

For more details, see the [Testing Guide](TESTING.md).

## Project Structure

The project follows a clean separation of concerns:

```
src/
├── __init__.py              # Package initialization
├── research_agent/
│   ├── __init__.py          # Package initialization
│   ├── core/                # Core business logic
│   │   ├── dependencies.py  # Dependency injection definitions
│   │   ├── graph.py         # Graph definition
│   │   ├── nodes.py         # Node definitions
│   │   └── state.py         # State class definition
│   ├── api/                 # API layer
│   │   └── services.py      # Service functions for interfaces
│   ├── cli/                 # Command-line interface
│   │   └── commands.py      # CLI functionality
│   └── ui/                  # User interface layer
│       ├── streamlit/       # Streamlit web UI
│       │   └── app.py       # Streamlit application
│       └── web/             # (Future) FastAPI web API
└── main.py                  # Main entry point
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
make setup

# Run all quality checks manually
make quality

# Run individual checks
make format     # Format code with black and isort
make lint       # Run all linters
make security   # Run security checks
```

### Error Handling

This project follows consistent error handling practices:

1. All functions have clear type annotations and docstrings
2. Exceptions are caught at appropriate levels and contextualized
3. Logging is used for debugging and tracing
4. Custom exceptions are used for domain-specific errors

## Overview

The project uses `pydantic-graph` to create a simple workflow with four nodes:

1. `HelloNode` - Generates the text "Hello" (can use LLM via dependency injection)
2. `WorldNode` - Generates the text "World" (can use LLM via dependency injection)
3. `CombineNode` - Combines the texts to create "Hello World!"
4. `PrintNode` - Prints the final result and ends the graph execution

Each node runs in sequence, passing its state to the next node in the graph.

## Requirements

This project uses `pipenv` for dependency management. The main dependencies are:

- `pydantic-graph` - For defining the graph workflow
- `pydantic-ai` - A dependency of `pydantic-graph`

## Installation

You can install this package in development mode using pipenv:

```bash
pipenv install -e .
```

Or using pip:

```bash
pip install -e .
```

For development with testing, install with the dev extras:

```bash
pipenv install -e ".[dev]"
# or
pip install -e ".[dev]"
```

This will install the package in development mode, allowing you to make changes to the code and see them reflected immediately.

## Testing

This project uses pytest as its testing framework. To run the tests:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/research_agent/test_nodes.py

# Run specific test
pytest tests/research_agent/test_nodes.py::test_hello_node
```

Test categories:

- **Node Tests**: Verify each node's individual behavior
- **Dependency Tests**: Ensure dependency injection works correctly
- **Graph Tests**: Test complete graph execution with different configurations
- **CLI Tests**: Verify command-line interface functionality

The tests use pytest fixtures to set up test dependencies and mock objects, making it easy to test different aspects of the application in isolation.

## Running the Example

To run the example, you can use the hello-graph command with different interfaces:

### Command-Line Interface

```bash
# Run the CLI with default values
pipenv run hello-graph cli

# Run the CLI with custom LLM and prefix
pipenv run hello-graph cli --use-custom-llm --prefix "AI"
```

### Streamlit Web Interface

```bash
# Run the Streamlit UI
pipenv run hello-graph ui

# Run on a specific port
pipenv run hello-graph ui --port 8502
```

The Streamlit interface provides a user-friendly way to interact with the application, including:

- A configuration sidebar for setting options
- Real-time display of results
- Detailed timing information
- Execution history visualization

## Architecture

The application follows a layered architecture pattern:

1. **Core Layer**: Contains the essential business logic, including graph nodes, state, and dependencies
2. **API Layer**: Provides service functions that can be reused across interfaces
3. **Interface Layers**: 
   - CLI: Command-line interface for running the application
   - UI: Web interfaces including Streamlit (and future FastAPI)

This architecture makes it easy to:
- Add new interfaces without modifying core logic
- Share functionality between interfaces
- Test each layer independently

## Expected Output

With default settings:
```
Generated: Hello (took 0.103s)
Generated: World (took 0.201s)
Combined: Hello World! (took 0.153s)
Final output: Hello World! (took 0.055s)

=== Graph Execution Results ===
Time: 2025-02-28 11:02:01
Result: Hello World!
Final state: MyState(hello_text='Hello', world_text='World', combined_text='Hello World!')

Node execution history:
  1. NodeStep
  2. NodeStep
  3. NodeStep
  4. EndStep
==============================
```

With custom LLM client using a prefix:
```
Generated: AI Hello (took 0.103s)
Generated: AI World (took 0.201s)
Combined: AI Hello AI World! (took 0.153s)
Final output: AI Hello AI World! (took 0.057s)

=== Graph Execution Results ===
Time: 2025-02-28 11:08:19
Result: AI Hello AI World!
Final state: MyState(hello_text='AI Hello', world_text='AI World', combined_text='AI Hello AI World!')

Node execution history:
  1. NodeStep
  2. NodeStep
  3. NodeStep
  4. EndStep
==============================
```

## How It Works

1. The `state.py` module defines a `MyState` class to store the intermediate text values
2. The `dependencies.py` module defines interfaces and implementations for dependency injection
3. The `nodes.py` module defines each node as a subclass of `BaseNode` from the `pydantic-graph` library
4. The `graph.py` module connects the nodes into a graph using the `Graph` class
5. The `main.py` script serves as the entry point, parsing command-line arguments and running the graph
6. When the graph is run, each node executes in sequence, updating the state
7. The result of the graph execution includes the final output, state, and execution history

## Dependency Injection Pattern

This project implements dependency injection using pydantic-graph's built-in support:

1. Define a dependencies class in `dependencies.py` that holds service objects
2. Define a Protocol for the LLM client interface
3. Provide implementation of the Protocol (GeminiLLMClient)
4. Configure nodes to use dependencies by specifying the type parameter: `BaseNode[StateT, DepsT, RunEndT]`
5. Access dependencies in node methods through `ctx.deps`
6. Pass dependencies when running the graph with `graph.run(..., deps=dependencies)`

This pattern allows for easy swapping of implementations (like different LLM providers) without changing the node logic.

## Evolving the Project

This structure provides a solid foundation for evolving the project:

- Add more complex nodes by extending the nodes in `nodes.py`
- Create different state classes in `state.py` for different types of data
- Define multiple graphs in `graph.py` for different workflows
- Add additional utility functions for processing graph results
- Implement real LLM clients that use APIs like OpenAI, Anthropic, etc.

The separation of concerns makes it easy to modify or extend any part of the system without affecting the others.

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Development Guide](docs/development.md)
- [User Guide](docs/user_guide.md)
- [Gemini Integration Guide](docs/gemini_integration.md)
- [Testing Guide](TESTING.md)

## Using the Gemini Chat Interface

The Research Agent now includes a chat interface for interacting with Google's Gemini LLM through the pydantic-graph framework. This feature allows you to have natural conversations with the Gemini model while leveraging the agent infrastructure.

### Running the Gemini Chat UI

You can launch the Gemini chat interface with the following command:

```bash
# From the project root
python -m research_agent.ui.cli_entry --app gemini
```

Or simply:

```bash
research_agent --app gemini
```

This will open a Streamlit web interface in your browser where you can interact with the Gemini model.

### Features of the Gemini Chat Interface

- **Streaming Responses:** See responses as they're generated, character by character
- **Custom System Prompts:** Configure how the assistant behaves by modifying the system prompt
- **Conversation Memory:** Enable or disable memory of previous messages in the conversation
- **Chat History:** View and save your conversation history
- **Response Details:** Examine timing and processing information for each response

### Configuration

The sidebar in the Streamlit interface allows you to customize your experience:

1. **System Prompt:** Edit the instructions that define the AI assistant's behavior
2. **Chat Memory:** Toggle whether the assistant remembers previous messages
3. **Clear Chat History:** Reset the conversation to start fresh

### Saving Conversations

After at least one exchange, you'll have the option to save your conversation as a JSON file for future reference or analysis 