# Development Guide

This guide provides information for developers who want to contribute to the Research Agent project.

## Setting Up a Development Environment

### Prerequisites

- Python 3.9 or newer
- pipenv (recommended)
- Git

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd research_agent
   ```

2. **Install development dependencies**:
   ```bash
   make setup
   ```
   
   This will:
   - Install all required packages
   - Set up pre-commit hooks
   - Configure the development environment

3. **Verify your setup**:
   ```bash
   make quality
   ```
   
   This runs all quality checks to ensure your environment is correctly configured.

## Project Structure

The project is organized as follows:

```
src/
├── hello_world/             # Package for the Hello World example
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
│       └── streamlit/       # Streamlit web UI
│           └── app.py       # Streamlit application
tests/                       # Test directory
├── hello_world/             # Tests for the hello_world package
│   ├── test_nodes.py        # Tests for nodes
│   ├── test_graph.py        # Tests for graph
│   └── ...                  # Other test files
scripts/                     # Utility scripts
docs/                        # Documentation
```

## Development Workflow

We follow a **fork and pull model** for contributions. This keeps the main repository clean and ensures all code is reviewed before merging.

For detailed instructions on the contribution workflow, please see our [Contributing Guide](CONTRIBUTING.md).

### Quick Summary of Contribution Process

1. Fork the repository to your account
2. Clone your fork locally
3. Create a feature branch for your work
4. Make your changes following our standards
5. Push your branch to your fork
6. Create a pull request to the main repository

### Making Changes

When working on changes:

- Keep each pull request focused on a single feature or bug fix
- Follow the coding standards and project conventions
- Add tests for new functionality
- Update documentation as needed

### Running Quality Checks

Before submitting your pull request, ensure your code meets our quality standards:

```bash
make quality
```

This will run all formatters, linters, security checks, tests, and documentation checks.

### Testing

1. **Run all tests**:
   ```bash
   make test
   ```

2. **Run specific tests**:
   ```bash
   pipenv run pytest tests/hello_world/test_nodes.py -v
   ```

3. **Add new tests**:
   - Each new feature should have corresponding tests
   - Tests should be in the appropriate file in the `tests/` directory
   - Use pytest fixtures for common setup

### Code Quality Standards

All code must meet the following standards:

1. **Formatting**:
   - Black with 100 character line length
   - isort for import organization

2. **Linting**:
   - Flake8 for style guide enforcement
   - Pylint for deeper static analysis
   - Mypy for type checking
   - Bandit for security checks

3. **Documentation**:
   - All modules, classes, and functions should have docstrings
   - Follow Google style for docstrings

4. **Error Handling**:
   - Use appropriate exception types
   - Catch exceptions at the right level
   - Log relevant information

## Adding New Components

### Creating New Nodes

1. **Define the node class**:
   - Create a new class inheriting from `BaseNode`
   - Implement the `run` method
   - Add appropriate type annotations

   Example:
   ```python
   @dataclass
   class MyNewNode(BaseNode[MyState, HelloWorldDependencies, str]):
       """Node description."""
       
       async def run(self, ctx: GraphRunContext) -> NextNode:
           # Node implementation
           return NextNode()
   ```

2. **Add tests for the node**:
   - Create tests in `tests/hello_world/test_nodes.py`
   - Test the node's behavior in isolation

### Creating a New Graph

1. **Define the graph**:
   - Create a function that returns a `Graph` instance
   - Specify the nodes and their connections

   Example:
   ```python
   def get_my_new_graph() -> Graph:
       graph = Graph(
           nodes=[FirstNode, SecondNode, ThirdNode],
       )
       return graph
   ```

2. **Add tests for the graph**:
   - Create tests in `tests/hello_world/test_graph.py`
   - Test that the graph executes as expected

### Adding Dependencies

1. **Define the dependency protocol**:
   - Create a new protocol in `dependencies.py`
   - Specify the required methods

   Example:
   ```python
   class MyNewDependency(Protocol):
       async def some_method(self, input: str) -> str:
           ...
   ```

2. **Implement the dependency**:
   - Create classes that fulfill the protocol
   - Add the dependency to the `HelloWorldDependencies` class

3. **Add tests for the dependency**:
   - Create tests in `tests/hello_world/test_dependencies.py`
   - Test the dependency's behavior

## Documentation

### Updating Documentation

1. **Code documentation**:
   - Update docstrings when changing functions or classes
   - Ensure examples in docstrings are current

2. **User documentation**:
   - Update files in the `docs/` directory
   - Keep the README.md up to date

### Building Documentation

Currently, documentation is in Markdown format. We may implement a documentation generator in the future.

## Release Process

1. **Ensure all tests pass**:
   ```bash
   make quality
   ```

2. **Update version numbers**:
   - Update in `setup.py`
   - Update in any other relevant files

3. **Create a release commit**:
   ```bash
   git add .
   git commit -m "Release vX.Y.Z"
   git tag vX.Y.Z
   ```

4. **Push to remote**:
   ```bash
   git push origin main
   git push origin vX.Y.Z
   ```

## Getting Help

If you need assistance with development:

1. Check the existing documentation
2. Look at the code comments and docstrings
3. Examine the tests for examples
4. Reach out to the maintainers for guidance 