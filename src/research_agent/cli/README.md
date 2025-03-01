# Research Agent CLI

This directory contains the command-line interface (CLI) implementation for the Research Agent.

## Structure

The CLI is organized as follows:

```
cli/
├── __init__.py       # Package initialization
├── main.py           # Main entry point
├── commands/         # Individual commands
│   ├── __init__.py   # Commands package
│   ├── gemini.py     # Gemini command implementation
│   └── ingest.py     # Document ingestion command
└── README.md         # This file
```

## Adding New Commands

To add a new command to the CLI:

1. Create a new file in the `commands/` directory (e.g., `commands/my_command.py`)
2. Implement the command following this pattern:
   ```python
   def add_my_command(subparsers):
       """Add the command to the CLI subparsers."""
       parser = subparsers.add_parser("my-command", help="My command description")
       # Add arguments...
       
   async def run_my_command(args):
       """Run the command with parsed arguments."""
       # Implement command...
       return 0  # Return exit code
   ```
3. Update `main.py` to register your command:
   - Import your command: `from research_agent.cli.commands.my_command import add_my_command`
   - Add it to the parser: `add_my_command(subparsers)`
   - Add it to the command handlers: `"my-command": "research_agent.cli.commands.my_command.run_my_command"`

## Usage

The CLI can be used through the `research-agent` command installed by the package:

```shell
# Run the Gemini AI agent
research-agent gemini --prompt "Your prompt here"

# Ingest documents into ChromaDB
research-agent ingest --data-dir "./my-documents"
```

For more information on available commands and options, run:

```shell
research-agent --help
```

Or for help on a specific command:

```shell
research-agent <command> --help
``` 