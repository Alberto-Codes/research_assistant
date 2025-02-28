# Pydantic Graph Hello World Example

This project demonstrates how to use the `pydantic-graph` library to create a graph workflow that prints "Hello World!".

## Project Structure

The project follows a clean separation of concerns:

```
src/
├── __init__.py             # Package initialization
├── hello_world/
│   ├── __init__.py         # Exports public API
│   ├── graph.py            # Graph definition and runner
│   ├── nodes.py            # Node definitions
│   └── state.py            # State class definition
└── main.py                 # Main entry point
```

## Overview

The project uses `pydantic-graph` to create a simple workflow with four nodes:

1. `HelloNode` - Generates the text "Hello"
2. `WorldNode` - Generates the text "World"
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
pipenv run python src/main.py --hello "Greetings" --world "Universe"
```

## Expected Output

```
Generated: Hello
Generated: World
Combined: Hello World!
Final output: Hello World!

=== Graph Execution Results ===
Result: Hello World!
Final state: MyState(hello_text='Hello', world_text='World', combined_text='Hello World!')

Node execution history:
  1. NodeStep
  2. NodeStep
  3. NodeStep
  4. EndStep
==============================
```

## How It Works

1. The `state.py` module defines a `MyState` class to store the intermediate text values
2. The `nodes.py` module defines each node as a subclass of `BaseNode` from the `pydantic-graph` library
3. The `graph.py` module connects the nodes into a graph using the `Graph` class
4. The `main.py` script serves as the entry point, parsing command-line arguments and running the graph
5. When the graph is run, each node executes in sequence, updating the state
6. The result of the graph execution includes the final output, state, and execution history

## Evolving the Project

This structure provides a solid foundation for evolving the project:

- Add more complex nodes by extending the nodes in `nodes.py`
- Create different state classes in `state.py` for different types of data
- Define multiple graphs in `graph.py` for different workflows
- Add additional utility functions for processing graph results

The separation of concerns makes it easy to modify or extend any part of the system without affecting the others. 