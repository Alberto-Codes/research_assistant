# Pydantic Graph Hello World Example

This project demonstrates how to use the `pydantic-graph` library to create a graph workflow that prints "Hello World!".

## Project Structure

The project follows a clean separation of concerns:

```
src/
├── __init__.py              # Package initialization
├── hello_world/
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
pytest tests/hello_world/test_nodes.py

# Run specific test
pytest tests/hello_world/test_nodes.py::test_hello_node
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
3. Provide implementations of the Protocol (MockLLMClient and CustomLLMClient)
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