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
   pipenv run research_agent --help
   ```
   
   You should see a help message listing available commands.

## Using the Research Agent

### Choosing an Interface

The Research Agent offers multiple ways to interact with it:

1. **Command-line Interface (CLI)** - Text-based, good for scripting
2. **Web Interface** - Visual, easier for exploration
3. **Gemini Chat UI** - Interactive chat interface for conversations with Gemini models

#### Web Interface (Recommended for Beginners)

The web interface provides a visual way to interact with the Research Agent:

1. **Start the web interface**:
   ```bash
   make run-ui
   ```
   or
   ```bash
   pipenv run research_agent ui
   ```

2. **Access the interface**: 
   - Open your web browser
   - Go to http://localhost:8501
   
3. **Using the interface**:
   - The sidebar contains configuration options
   - The main panel shows results and visualizations
   - Click the "Generate" button to run the process

   ![Streamlit Interface Example](images/streamlit_interface.png)

#### Gemini Chat Interface

The Gemini Chat UI provides an interactive chat experience with Google's Gemini models:

1. **Start the Gemini Chat interface**:
   ```bash
   make run-gemini
   ```
   or
   ```bash
   pipenv run research_agent --app gemini
   ```
   or
   ```bash
   streamlit run src/research_agent/ui/streamlit/gemini_chat.py
   ```

2. **Access the interface**:
   - Open your web browser
   - Go to http://localhost:8501

3. **Using the Gemini Chat**:
   - Type your message in the text input at the bottom
   - Messages will stream in real-time with typing animation
   - Configure system prompts and chat options in the sidebar
   - Toggle conversation memory on/off in the sidebar
   - Save your conversation history as a JSON file

#### Command-line Interface

For more advanced users or for automation:

1. **Basic usage**:
   ```bash
   pipenv run research_agent cli
   ```

2. **With custom options**:
   ```bash
   pipenv run research_agent cli --prefix "AI"
   ```

3. **Using Gemini from the command line**:
   ```bash
   pipenv run research_agent gemini --prompt "What are the three laws of robotics?"
   ```

### Configuration Options

You can customize how the Research Agent works:

#### In the Web Interface

- **Text Prefix**: Add a prefix to generated text (e.g., "AI")

#### In the Gemini Chat Interface

- **System Prompt**: Edit the system instructions to customize the assistant's behavior
- **Chat Memory**: Toggle conversation memory on or off
- **Clear History**: Reset the conversation
- **Save Conversation**: Download the chat history as a JSON file

#### In the Command-line

- `--prefix TEXT`: Add a prefix to generated text

## Example Workflows

### Basic Research Example

1. Start the web interface with `make run-ui`
2. Keep the default settings in the sidebar
3. Click the "Generate" button
4. Observe the result: "Hello World!"
5. Review the timing information and execution history

### Gemini Chat Example

1. Start the Gemini Chat UI with `research_agent --app gemini`
2. In the sidebar, customize the system prompt if desired
3. Type a message in the input field, such as "Tell me about quantum computing"
4. Observe the streaming response from Gemini
5. Continue the conversation with follow-up questions
6. Save your conversation using the "Save Chat" button

### Custom Research Example

1. Start the web interface with `make run-ui`
2. Enter "AI" in the Text Prefix field
3. Click the "Generate" button
4. Observe the result: "AI Hello AI World!"

## Understanding the Results

The Research Agent provides several pieces of information:

1. **Generated Text**: The final output of the research process
2. **Timing Information**: How long each step took
3. **Execution History**: The sequence of steps that were performed
4. **Component Outputs**: What each component produced

In the Gemini Chat UI, you'll also see:
1. **Response Time**: How long it took to generate the response
2. **Token Metrics**: Information about tokens used (when available)
3. **Chat History**: Complete conversation thread

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

#### Gemini Chat UI Issues

- If you encounter event loop errors, make sure you're using the latest version
- Authentication errors may indicate issues with Google Cloud credentials
- See the [Gemini Integration Guide](gemini_integration.md) for more troubleshooting tips

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