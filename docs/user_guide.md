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
   research_agent --help
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
   research_agent --app streamlit
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
   research_agent --app gemini
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

1. **Using Gemini from the command line**:
   ```bash
   research_agent gemini --prompt "What are the three laws of robotics?"
   ```

2. **With logging options**:
   ```bash
   research_agent gemini --prompt "Explain neural networks" --log-level DEBUG --log-file ./logs/gemini.log
   ```

3. **Ingesting documents**:
   ```bash
   research_agent ingest --data-dir "./documents" --collection "my_research" --chroma-dir "./chroma_db"
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

- Common options available for all commands:
  - `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `--log-file`: Specify a file to save logs

- Gemini command options:
  - `--prompt`: The prompt to send to the Gemini model (required)
  - `--project-id`: Google Cloud project ID (optional)

- Ingest command options:
  - `--data-dir`: Directory containing documents to ingest
  - `--collection`: Name of the ChromaDB collection
  - `--chroma-dir`: Directory for ChromaDB persistence

## Example Workflows

### Example Workflow

Here's an example of how the Research Agent processes a query:

1. You submit a query about your documents: "What information do my documents contain about machine learning?"
2. The QueryNode processes your query and prepares for document retrieval
3. The RetrieveNode searches ChromaDB for relevant documents
4. The AnswerNode generates a comprehensive answer based on the retrieved documents
5. You receive a detailed response with citations to the source documents

### Basic Research Example

1. Start the web interface with `research_agent --app streamlit`
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

### Document Ingestion Example

1. Prepare a directory with text documents:
   ```
   documents/
     ├── research1.txt
     ├── research2.txt
     └── article.txt
   ```

2. Ingest the documents:
   ```bash
   research_agent ingest --data-dir "./documents" --collection "quantum_research"
   ```

3. Verify ingestion with detailed logging:
   ```bash
   research_agent ingest --data-dir "./documents" --collection "quantum_research" --log-level DEBUG
   ```

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

#### ChromaDB Issues

- If document ingestion fails, check that your data directory exists and contains text files
- For embedding errors, verify ChromaDB is installed correctly
- Use `--log-level DEBUG` to get detailed information about any errors

## Next Steps

After getting familiar with the basic functionality, you can:

1. Examine the code to understand how the components work
2. Create custom nodes for specific research tasks
3. Integrate with real language model providers
4. Build more complex research workflows

## Testing and Contributing

### Running Tests

The Research Agent has a comprehensive test suite:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific tests
pytest tests/research_agent/test_cli.py

# Run Streamlit UI tests
pytest tests/research_agent/test_streamlit.py
```

### Writing Tests

If you want to contribute to the project:

1. Add tests for any new functionality
2. Ensure all tests pass before submitting changes
3. Follow the patterns in the existing test files
4. For UI tests, use the Streamlit testing framework with `AppTest`

The project now features enhanced Streamlit UI testing using the `AppTest` framework, which allows for testing UI components without running a full browser:

- Tests verify UI elements, interactions, and streaming responses
- Uses proper mocking techniques for async functions
- Includes error handling for Streamlit context errors
- Provides a robust approach for testing the Gemini chat interface

For example, to test a UI interaction:

```python
from streamlit.testing.v1 import AppTest

def test_ui_interaction():
    # Create and run the test app
    at = AppTest.from_file("path/to/app.py")
    at.run()
    
    # Test a user interaction
    at.chat_input[0].set_value("Test question")
    at.run()
    
    # Verify the response appeared
    assert "response" in at.markdown[0].value.lower()
```

See the [Testing Guide](../TESTING.md) for detailed information about the testing approach.

## Getting Help

If you need assistance:

1. Check the documentation in the `docs/` directory
2. Review the code comments for detailed explanations
3. Look at the tests for examples of expected behavior 