# Research Agent Entry Points

This document describes the entry point structure for the Research Agent package.

## Entry Point Structure

The Research Agent package has been reorganized to have a cleaner entry point structure:

### Primary Entry Points

- **research_agent.main.main()** - The main entry point for the package
- **research_agent.main.cli_entry()** - The entry point used by the console_scripts

### Console Script

The package installs a command-line tool:

```bash
research_agent [interface] [command] [options]
```

Where:
- `interface` is either `cli` or `ui`
- `command` (for CLI interface) is one of the available commands (e.g., `gemini`, `ingest`)

### Example Usage

```bash
# Run the CLI interface with the gemini command
research_agent cli gemini query "What is quantum physics?"

# Run the Streamlit UI
research_agent ui --port 8501
```

### Programmatic Usage

```python
# Import the main entry point
from research_agent import main

# Run the CLI interface
main(["cli", "gemini", "query", "What is quantum physics?"])

# Run the UI interface
main(["ui", "--port", "8501"])
```

## Deprecated Entry Points

The following entry points are now deprecated and will be removed in a future version:

- **src/main.py** - Replaced by research_agent.main
- **src/research_agent/cli/main.py** - Replaced by research_agent.main
- **src/research_agent/ui/cli_entry.py** - Replaced by research_agent.main

These files now show deprecation warnings and redirect to the new entry point.

## Adding New Commands

To add a new command to the CLI interface:

1. Create a new module in `src/research_agent/cli/commands/`
2. Implement the required functions:
   - `add_xxx_command(subparsers)` - Add command to the argument parser
   - `run_xxx_command(args)` - Run the command with the parsed arguments
3. Update the command_handlers dictionary in `research_agent.main`

## Directory Structure

```
src/
├── __init__.py           # Top-level package init, exports cli_entry
├── main.py               # DEPRECATED: Redirects to research_agent.main
└── research_agent/
    ├── __init__.py       # Package init, exports main and cli_entry
    ├── __main__.py       # Enables running as python -m research_agent
    ├── main.py           # NEW: Consolidated main entry point
    ├── cli/
    │   ├── __init__.py
    │   ├── main.py       # DEPRECATED: Legacy CLI entry point
    │   └── commands/     # CLI command implementations
    └── ui/
        ├── cli_entry.py  # DEPRECATED: Legacy UI entry point
        └── streamlit/    # Streamlit applications
```

This structure provides a clean, organized way to access the package's functionality through a single entry point. 