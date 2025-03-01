# Research Agent CLI

This directory contains command implementations for the Research Agent's command-line interface.

## Structure

- `commands/` - Individual command implementations (gemini, ingest, etc.)
- `main.py` - Legacy CLI entry point (deprecated)

## Usage

The CLI functionality is now accessed through the main `research_agent` entry point:

```bash
# Run the CLI interface
research_agent cli gemini query "Your research question here"

# Run the UI interface
research_agent ui
```

Or programmatically:

```python
from research_agent.main import main

# Run with command-line arguments
main(["cli", "gemini", "query", "Your research question here"])

# Run the UI
main(["ui"])
```

## Adding New Commands

To add a new command:

1. Create a new module in the `commands/` directory
2. Implement two functions:
   - `add_xxx_command(subparsers)` - Adds the command to the argument parser
   - `run_xxx_command(args)` - Runs the command with the parsed arguments
3. Update `research_agent.main` to include your new command:
   - Import the command functions
   - Add the command to the command_handlers dictionary

## Deprecated Interfaces

Several legacy entry points are now deprecated:

- `src/main.py` - Use `research_agent.main` instead
- `src/research_agent/cli/main.py` - Use `research_agent.main` instead
- `src/research_agent/ui/cli_entry.py` - Use `research_agent.main` instead 