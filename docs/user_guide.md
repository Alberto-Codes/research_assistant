# Research Agent User Guide

This guide helps you get started with the Research Agent tool. It covers installation, basic usage, and common tasks.

## Getting Started

### Installation

1. **Prerequisites**:
   - Python 3.9 or newer
   - Pipenv (recommended) or pip

2. **Install the package**:

   Using pipenv (recommended):
   ```bash
   pipenv install -e .
   ```

   Using pip:
   ```bash
   pip install -e .
   ```

3. **Verify installation**:
   ```bash
   pipenv run hello-graph --help
   ```
   
   You should see a help message listing available commands.

## Using the Research Agent

### Choosing an Interface

The Research Agent offers two main ways to interact with it:

1. **Command-line Interface (CLI)** - Text-based, good for scripting
2. **Web Interface** - Visual, easier for exploration

#### Web Interface (Recommended for Beginners)

The web interface provides a visual way to interact with the Research Agent:

1. **Start the web interface**:
   ```bash
   make run-ui
   ```
   or
   ```bash
   pipenv run hello-graph ui
   ```

2. **Access the interface**: 
   - Open your web browser
   - Go to http://localhost:8501
   
3. **Using the interface**:
   - The sidebar contains configuration options
   - The main panel shows results and visualizations
   - Click the "Generate" button to run the process

   ![Streamlit Interface Example](images/streamlit_interface.png)

#### Command-line Interface

For more advanced users or for automation:

1. **Basic usage**:
   ```bash
   pipenv run hello-graph cli
   ```

2. **With custom options**:
   ```bash
   pipenv run hello-graph cli --use-custom-llm --prefix "AI"
   ```

### Configuration Options

You can customize how the Research Agent works:

#### In the Web Interface

- **Use Custom LLM**: Toggle this option to use a custom language model
- **Text Prefix**: Add a prefix to generated text (e.g., "AI")

#### In the Command-line

- `--use-custom-llm`: Use a custom language model client
- `--prefix TEXT`: Add a prefix to generated text

## Example Workflows

### Basic Research Example

1. Start the web interface with `make run-ui`
2. Keep the default settings in the sidebar
3. Click the "Generate" button
4. Observe the result: "Hello World!"
5. Review the timing information and execution history

### Custom Research Example

1. Start the web interface with `make run-ui`
2. In the sidebar, check "Use Custom LLM"
3. Enter "AI" in the Text Prefix field
4. Click the "Generate" button
5. Observe the result: "AI Hello AI World!"

## Understanding the Results

The Research Agent provides several pieces of information:

1. **Generated Text**: The final output of the research process
2. **Timing Information**: How long each step took
3. **Execution History**: The sequence of steps that were performed
4. **Component Outputs**: What each component produced

## Troubleshooting

### Common Issues

#### Web Interface Won't Start

- Make sure Streamlit is installed: `pipenv install streamlit`
- Check if the port is already in use
- Verify you're in the correct directory

#### Generation Takes Too Long

- The current system uses simulated delays to demonstrate the workflow
- In a real system, processing time depends on the LLM service response time

#### Custom Settings Don't Work

- Verify you've entered the settings correctly
- Check the logs for any error messages
- Restart the interface if settings aren't being applied

## Next Steps

After getting familiar with the basic functionality, you can:

1. Examine the code to understand how the components work
2. Create custom nodes for specific research tasks
3. Integrate with real language model providers
4. Build more complex research workflows

## Getting Help

If you need assistance:

1. Check the documentation in the `docs/` directory
2. Review the code comments for detailed explanations
3. Look at the tests for examples of expected behavior 