# Testing Guide for Research Agent

This guide provides detailed information about the testing approach, how to run tests, and best practices for maintaining and extending the test suite.

## Overview

The Research Agent project uses pytest for testing with a focus on:

- **Unit testing** of core components
- **Integration testing** of workflows and services
- **UI testing** of Streamlit interfaces
- **Mock testing** for external dependencies like Vertex AI

## Running Tests

### Running the Full Test Suite

To run all tests:

```bash
pytest
```

For more detailed output, run:

```bash
pytest -v
```

### Running Specific Tests

Run tests from a specific file:

```bash
pytest tests/research_agent/test_graph.py
```

Run a specific test:

```bash
pytest tests/research_agent/test_graph.py::test_run_gemini_agent_graph
```

### Running Tests with Coverage

To run tests with coverage reporting:

```bash
pytest --cov=research_agent
```

For a detailed coverage report:

```bash
pytest --cov=research_agent --cov-report=html
```

This generates an HTML report in the `htmlcov` directory.

## Test Structure

Tests are organized to mirror the package structure:

```
tests/
├── research_agent/
│   ├── test_cli.py         # Tests for CLI functionality
│   ├── test_dependencies.py # Tests for dependency injection
│   ├── test_graph.py       # Tests for graph execution
│   ├── test_nodes.py       # Tests for individual nodes
│   └── test_streamlit.py   # Tests for Streamlit UI
├── test_gemini_client.py   # Tests for the Gemini client
├── test_nodes.py           # Tests for core nodes
└── test_services.py        # Tests for service layer functions
```

## Writing Tests

### Test Patterns

Follow these patterns when writing tests:

1. **AAA Pattern** (Arrange, Act, Assert):
   ```python
   def test_example():
       # Arrange - set up test data and dependencies
       test_data = "test input"
       mock_dependency = MagicMock()
       
       # Act - call the function being tested
       result = function_under_test(test_data, mock_dependency)
       
       # Assert - verify the function behaved as expected
       assert result == "expected output"
       assert mock_dependency.method.called
   ```

2. **Fixtures** for common setup:
   ```python
   @pytest.fixture
   def mock_gemini_client():
       return MagicMock()
       
   def test_with_fixture(mock_gemini_client):
       # Use the fixture
       assert function_using_client(mock_gemini_client) == expected_result
   ```

3. **Mocking** for isolating tests:
   ```python
   @patch("research_agent.core.dependencies.GeminiLLMClient")
   def test_with_mock(mock_client_class):
       mock_client = MagicMock()
       mock_client_class.return_value = mock_client
       mock_client.generate_text.return_value = "mocked response"
       
       # Test with the mock in place
       assert function_using_gemini() == "mocked response"
   ```

### Testing Async Code

For async functions, use pytest-asyncio:

```python
@pytest.mark.asyncio
async def test_async_function():
    # Test async function
    result = await async_function_under_test()
    assert result == expected_value
```

### Testing Streamlit UIs

For Streamlit interfaces, use the AppTest class:

```python
def test_streamlit_app():
    # Create a test app
    at = AppTest.from_file("path/to/app.py")
    
    # Run the app
    at.run()
    
    # Check UI elements
    assert "Title" in at.title[0].value
    
    # Interact with the app
    at.text_input[0].set_value("Test input")
    at.button[0].click()
    at.run()
    
    # Check results
    assert "Result" in at.markdown[0].value
```

When testing complex async behavior in Streamlit apps, use proper mocking:

```python
@patch("module.AsyncClass")
def test_streamlit_async(mock_async_class):
    # Setup mock for async behavior
    mock_instance = AsyncMock()
    mock_async_class.return_value = mock_instance
    
    # Configure async mock behavior
    mock_instance.async_method.return_value = "mock result"
    
    # Create and run test app
    at = AppTest.from_file("path/to/app.py")
    at.run()
    
    # Test interaction
    at.button[0].click()
    at.run()
    
    # Verify mock was called
    assert mock_instance.async_method.called
```

## Streamlit UI Testing

The Research Agent uses Streamlit for its user interfaces, and we test these UIs using Streamlit's built-in testing framework with the `AppTest` class.

### Setting Up Streamlit Tests

To test Streamlit UIs, you need to:

1. Import the `AppTest` class:
   ```python
   from streamlit.testing.v1 import AppTest
   ```

2. Create a test instance by pointing to your app file:
   ```python
   at = AppTest.from_file("src/research_agent/ui/streamlit/app.py")
   ```

3. Run the app:
   ```python
   at.run()
   ```

### Testing UI Elements

The `AppTest` class provides access to all UI elements:

```python
# Check page title
assert "Research Agent" in at.title[0].value

# Check for text in the page
assert "Instructions" in at.markdown[0].value

# Check widgets
assert at.text_input[0].label == "Your Question"
assert at.button[0].label == "Submit"
```

### Testing User Interactions

You can simulate user interactions:

```python
# Enter text
at.text_input[0].set_value("What is machine learning?")

# Click a button
at.button[0].click()

# Run the app again to process the interaction
at.run()

# Check for response
assert "machine learning" in at.chat_message[1].markdown[0].value.lower()
```

### Testing Async Streaming

For testing streaming UI features:

```python
# Mock the streaming response
with patch("module.streaming_function") as mock_stream:
    # Configure mock to return chunks of text
    async def mock_streaming():
        for chunk in ["Hello", " ", "World"]:
            yield chunk
    mock_stream.return_value = mock_streaming()
    
    # Run the app
    at.run()
    
    # Trigger streaming
    at.chat_input[0].set_value("Test")
    at.run()
    
    # Verify streaming happened
    assert mock_stream.called
```

### Handling Streamlit Context Errors

Streamlit tests may fail with context errors when run outside a Streamlit environment. Use try/except to gracefully handle these:

```python
def test_streamlit_ui():
    try:
        # Create and run test
        at = AppTest.from_file("path/to/app.py")
        at.run()
        
        # Test assertions...
        
    except Exception as e:
        pytest.skip(f"Streamlit test environment issue: {str(e)}")
```

### Tips for Effective Streamlit Testing

1. **Mock external dependencies**: Especially important for UI tests to avoid network calls
2. **Test incrementally**: Check UI setup first, then interactions, then responses
3. **Use widget indexing**: Access elements by index (e.g., `at.button[0]`, `at.text_input[1]`)
4. **Check for presence rather than exact matches**: UI content might change slightly
5. **Test critical user flows**: Focus on the most important user interactions

## Integration with CI/CD

Tests are run automatically in the CI/CD pipeline:

1. On each pull request, all tests are run
2. Coverage reports are generated
3. Tests must pass for the PR to be merged

## Dealing with External Dependencies

When testing code that relies on external services:

1. **Use mocks** for API clients and services
2. **Create fixtures** that simulate responses from external services
3. **Use dependency injection** to swap real implementations with test doubles

For Vertex AI and Gemini:

```python
@pytest.fixture
def mock_gemini_response():
    return {
        "text": "This is a mock response from Gemini",
        "metadata": {
            "token_count": 10,
            "response_time": 0.5
        }
    }

@patch("research_agent.core.dependencies.GeminiLLMClient")
def test_with_mock_gemini(mock_client_class, mock_gemini_response):
    # Configure the mock
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    mock_client.generate_text.return_value = mock_gemini_response["text"]
    
    # Test code that uses the client
    result = function_that_uses_gemini()
    assert result == mock_gemini_response["text"]
```

## Best Practices

1. **Keep tests isolated** - Each test should run independently
2. **Use descriptive test names** - Names should describe what's being tested
3. **Test edge cases** - Not just the happy path
4. **Avoid test interdependence** - Don't rely on state from other tests
5. **Clean up after tests** - Use teardown or context managers
6. **Mock external dependencies** - Don't call real APIs in tests
7. **Test one thing per test** - Each test should verify one aspect of behavior 

## Code Coverage

The project uses `pytest-cov` (built on top of the `coverage` package) to measure code coverage during testing. This helps identify which parts of the codebase are being tested and which parts need more test coverage.

### Running Tests with Coverage

#### Using PowerShell Script

The project provides a comprehensive PowerShell script (`run_tests.ps1`) that handles all test and coverage operations:

```powershell
# Run all tests without coverage
.\run_tests.ps1 test

# Run tests with terminal coverage report
.\run_tests.ps1 coverage

# Run tests with HTML coverage report
.\run_tests.ps1 coverage-html

# Run tests with coverage and automatically open the HTML report in browser
.\run_tests.ps1 coverage-report

# Clean up coverage files
.\run_tests.ps1 clean

# Show all available commands
.\run_tests.ps1 help
```

This script includes all necessary functionality in one place, making it the preferred way to run tests and coverage reports.

#### Manually Running Coverage

If needed, you can also run the coverage commands directly:

```bash
# Run tests with terminal coverage output
pipenv run pytest --cov=src/research_agent

# Run tests with HTML report generation
pipenv run pytest --cov=src/research_agent --cov-report=html
```

### Viewing Coverage Reports

After running tests with the HTML report option, you can view the detailed coverage report by opening `coverage_html_report/index.html` in your browser. This report shows:

- Overall coverage percentage
- Coverage by module
- Line-by-line coverage highlighting
- Missing coverage indicators

### Coverage Configuration

The coverage settings are configured in two files:

1. `.coveragerc` - Configures which files to include/exclude and report settings
2. `pytest.ini` - Configures pytest coverage integration

### Improving Coverage

When the coverage report shows low coverage in certain modules, consider adding more tests to cover:

1. Untested functions or methods
2. Edge cases and error conditions
3. Different code paths through conditional logic

Aim for at least 80% code coverage, focusing on the core functionality and business logic of the application. 