# Pydantic Graph Hello World Example

This project demonstrates how to use the `pydantic-graph` library to create a graph workflow that prints "Hello World!".

## Project Structure

The project follows a clean separation of concerns:

```
src/
├── __init__.py             # Package initialization
├── hello_world/
│   ├── __init__.py         # Exports public API
│   ├── dependencies.py     # Dependency injection definitions
│   ├── graph.py            # Graph definition and runner
│   ├── nodes.py            # Node definitions
│   └── state.py            # State class definition
└── main.py                 # Main entry point
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

This will install the package in development mode, allowing you to make changes to the code and see them reflected immediately.

## Running the Example

To run the example with default values:

```bash
# Using the module
pipenv run python src/main.py

# Using the installed console script
pipenv run hello-graph
```

You can also customize the "Hello" and "World" text with command-line arguments:

```bash
pipenv run hello-graph --hello "Greetings" --world "Universe"
```

### Using Dependency Injection

The application supports dependency injection for an LLM client:

```bash
# Use the custom LLM client
pipenv run hello-graph --use-custom-llm

# Use the custom LLM client with a prefix
pipenv run hello-graph --use-custom-llm --prefix "AI"
```

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