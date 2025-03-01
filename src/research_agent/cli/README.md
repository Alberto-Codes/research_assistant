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
       parser.add_argument("--required-arg", help="Description", required=True)
       parser.add_argument("--optional-arg", help="Description", default="default value")
       
       # Add common arguments like logging
       add_logging_arguments(parser)
       
   async def run_my_command(args):
       """Run the command with parsed arguments."""
       # Setup logging
       setup_logging(args.log_level, args.log_file)
       
       # Implement command logic...
       logger.info("Running my command")
       
       # Return exit code (0 for success)
       return 0
   ```
3. Register your command in the `commands/__init__.py` file:
   ```python
   from research_agent.cli.commands.my_command import add_my_command, run_my_command
   
   COMMAND_HANDLERS = {
       # Existing commands...
       "my-command": run_my_command,
   }
   
   def register_commands(subparsers):
       # Existing registrations...
       add_my_command(subparsers)
   ```

## Available Commands

The CLI includes these main commands:

- `gemini`: Run the Gemini AI agent with a prompt
- `ingest`: Ingest documents from a directory into ChromaDB

All commands support these common options:
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Specify a file path to save logs

## Usage

The CLI can be used through the `research_agent` command installed by the package:

```shell
# Run the Gemini AI agent
research_agent gemini --prompt "Your prompt here"

# Run with debug logging
research_agent gemini --prompt "Explain quantum physics" --log-level DEBUG

# Save logs to a file
research_agent gemini --prompt "Tell me about ML" --log-file ./logs/gemini.log

# Ingest documents into ChromaDB
research_agent ingest --data-dir "./my-documents" --collection "research_docs"

# Ingest with custom ChromaDB location
research_agent ingest --data-dir "./data" --chroma-dir "./custom_db" --collection "my_collection"
```

For more information on available commands and options, run:

```shell
research_agent --help
```

Or for help on a specific command:

```shell
research_agent <command> --help
``` 