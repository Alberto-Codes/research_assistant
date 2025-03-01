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
├── research_agent/             # Main package
│   ├── core/                # Core business logic
│   │   ├── dependencies.py  # Dependency injection definitions
│   │   ├── graph.py         # Graph definition
│   │   ├── logging_config.py # Centralized logging configuration
│   │   ├── nodes.py         # Node definitions
│   │   └── state.py         # State class definition
│   ├── api/                 # API layer
│   │   └── services.py      # Service functions for interfaces
│   ├── cli/                 # Command-line interface
│   │   └── commands.py      # CLI functionality
│   └── ui/                  # User interface layer
│       ├── streamlit/       # Streamlit web UI
│       │   ├── app.py       # Hello World Streamlit application
│       │   └── gemini_chat.py # Gemini Chat interface
│       └── cli_entry.py     # Entry point for UI applications
tests/                       # Test directory
├── research_agent/             # Tests for the research_agent package
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
   pipenv run pytest tests/research_agent/test_nodes.py -v
   ```

3. **Add new tests**:
   - Each new feature should have corresponding tests
   - Tests should be in the appropriate file in the `tests/` directory
   - Use pytest fixtures for common setup

4. **Streamlit UI Testing**:
   - Streamlit UI tests use the `AppTest` class from `streamlit.testing.v1`
   - Tests should verify UI elements, user interactions, and response handling
   - Example:
     ```python
     from streamlit.testing.v1 import AppTest
     
     def test_streamlit_app():
         # Create a test app instance
         at = AppTest.from_file("src/research_agent/ui/streamlit/app.py")
         
         # Run the app
         at.run()
         
         # Check UI elements
         assert "Title" in at.title[0].value
         
         # Test interactions
         at.text_input[0].set_value("Test input")
         at.button[0].click()
         at.run()
         
         # Verify results
         assert "Result" in at.markdown[0].value
     ```
   - For async streaming tests, use proper mocking techniques
   - See `tests/research_agent/test_streamlit.py` for examples
   - Refer to the [Testing Guide](../TESTING.md) for detailed instructions

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
   - Log relevant information using the structured logging system

## Logging Guidelines

The Research Agent project uses a centralized logging system for consistent log management across all modules.

### Logging Setup

The project has a centralized logging configuration in `src/research_agent/core/logging_config.py` that:
- Sets up consistent log formatting
- Configures handlers (console and optional file output)
- Provides runtime configuration via command-line parameters

### Using Logging in Your Code

1. **Get a module-specific logger**:
   ```python
   import logging
   
   # At the module level (outside of any class or function)
   logger = logging.getLogger(__name__)
   ```

2. **Use appropriate log levels**:
   - `logger.debug()` - Detailed debugging information
   - `logger.info()` - Confirmation of normal operation
   - `logger.warning()` - Something unexpected but not an error
   - `logger.error()` - An error occurred but execution continues
   - `logger.critical()` - A critical error that may prevent further execution

3. **Follow these best practices**:
   - Use structured logging with format parameters instead of string concatenation:
     ```python
     # Good
     logger.info("Processing item %s with status %s", item_id, status)
     
     # Avoid
     logger.info(f"Processing item {item_id} with status {status}")
     ```
   - Include contextual information that will help with debugging
   - Log at the beginning and end of important operations
   - Include timing information for performance-sensitive operations

4. **Error handling with logging**:
   ```python
   try:
       result = perform_operation()
   except Exception as e:
       logger.error("Operation failed: %s", e, exc_info=True)
       # Handle the error appropriately
   ```

5. **Don't use print statements**:
   - Always use the logging system instead of print statements
   - This ensures all output follows the same format and filtering rules

### Command-line Options

The logging system supports the following command-line options:
- `--log-level`: Sets the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Specifies a file to write logs to (in addition to console output)

Example:
```bash
python -m research_agent.cli.commands hello --log-level DEBUG --log-file logs/app.log
```

## Command-line Interface

The Research Agent project uses a structured command-line interface (CLI) based on Python's `argparse` library, implemented in the `commands.py` module.

### CLI Structure

The CLI is organized with a main entry point that accepts subcommands:

```
research_agent <command> [options]
```

Current commands:
- `gemini`: Interact with the Gemini AI model

Each command has its own set of arguments and options, with consistent logging options across all commands.

### Command Implementation

The CLI implementation follows these patterns:

1. **Command parser creation**: The `create_parser()` function creates and configures the argument parser.
2. **Command handlers**: Each command has its own async handler function (e.g., `gemini_command()`).
3. **Main entry point**: The `cli_entry()` function serves as the main entry point registered in `setup.py`.
4. **Logging configuration**: Each command automatically configures logging based on command-line args.

### Adding a New Command

To add a new command to the CLI:

1. Update the `create_parser()` function to add your new subcommand:
   ```python
   def create_parser() -> argparse.ArgumentParser:
       # ... existing code ...
       
       # Add your new command
       new_command_parser = subparsers.add_parser(
           "new_command", help="Description of your new command"
       )
       new_command_parser.add_argument(
           "--option", 
           type=str, 
           help="Description of the option"
       )
       
       # Add logging arguments
       add_logging_args(new_command_parser)
       
       return parser
   ```

2. Create a handler function for your command:
   ```python
   async def new_command(args: argparse.Namespace) -> None:
       """
       Implementation for the new command.
       
       Args:
           args: Command-line arguments.
       """
       logger = logging.getLogger(__name__)
       logger.info("Running new command")
       
       # Command implementation
       try:
           # Your code here
           pass
       except Exception as e:
           logger.error("Error running new command: %s", e)
           print(f"Error: {e}")
           sys.exit(1)
   ```

3. Update the `main_async()` function to handle your new command:
   ```python
   async def main_async(args: Optional[List[str]] = None) -> None:
       # ... existing code ...
       
       # Run the appropriate command
       if parsed_args.command == "gemini":
           await gemini_command(parsed_args)
       elif parsed_args.command == "new_command":
           await new_command(parsed_args)
       else:
           parser.print_help()
   ```

4. Add tests for your new command in the `tests/` directory.

### CLI Best Practices

- Provide helpful descriptions for all commands and options
- Use consistent naming conventions for options
- Include `--help` output that clearly explains each option
- Follow the established pattern of error handling and logging
- Make command implementations async to support concurrent operations
- Keep command handlers focused and delegate complex logic to service functions

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
   - Create tests in `tests/research_agent/test_nodes.py`
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
   - Create tests in `tests/research_agent/test_graph.py`
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
   - Create tests in `tests/research_agent/test_dependencies.py`
   - Test the dependency's behavior

## Working with the Gemini Chat UI

The Gemini Chat UI is a Streamlit-based interface for interacting with Google's Gemini models. Here's how to work with it:

### Running the Gemini Chat UI

```bash
# Using the CLI entry point
python -m research_agent.ui.cli_entry --app gemini

# Or directly running the Streamlit script
streamlit run src/research_agent/ui/streamlit/gemini_chat.py
```

### Key Components

1. **gemini_chat.py**: Main UI file that handles:
   - User interface rendering
   - Message handling and history management
   - Integration with the GeminiLLMClient

2. **Streaming Implementation**: The UI implements streaming responses using:
   - Async context managers
   - Proper event loop handling with nest_asyncio
   - Chunked text display with typing animation

3. **Configuration**: The UI allows customization of:
   - System prompts
   - Chat memory behavior
   - Response parameters

### Development Guidelines

When working on the Gemini Chat UI:

1. **Keep async code clean**: Avoid unnecessary event loop manipulation
2. **Use proper error handling**: Catch and display errors appropriately
3. **Test streaming functionality**: Ensure responses stream properly without errors
4. **Maintain responsive UI**: Keep the interface responsive during model calls

### Testing the Gemini Chat UI

The Gemini Chat UI has comprehensive tests in `tests/research_agent/test_streamlit.py` using Streamlit's `AppTest` framework:

1. **Test Setup**:
   ```python
   @patch("research_agent.ui.streamlit.gemini_chat.asyncio.run")
   @patch("research_agent.ui.streamlit.gemini_chat.GeminiLLMClient")
   def test_gemini_chat_ui(mock_gemini_client, mock_asyncio_run):
       # Create a test app
       at = AppTest.from_file("src/research_agent/ui/streamlit/gemini_chat.py")
       at.run()
       
       # Test UI elements and interactions
       # ...
   ```

2. **Testing Async Features**:
   - Use `@pytest.mark.asyncio` decorator for async tests
   - Mock streaming response functions
   - Test both success and error paths
   
3. **Testing Response Generation**:
   - Test both regular and streaming response generation
   - Mock the agent and client dependencies
   - Verify proper state updates

4. **Error Handling**:
   - Wrap Streamlit tests in try/except blocks to handle context errors
   - Use `pytest.skip()` with informative messages for environment issues

For detailed examples, see `tests/research_agent/test_streamlit.py` and the [Testing Guide](../TESTING.md).

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