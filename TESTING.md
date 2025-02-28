# Testing Guide for Research Agent

This document outlines the testing approach and best practices for the Research Agent project, specifically focusing on how to properly test the Gemini AI integration.

## Testing Approach

### 1. Unit Testing with pytest

We use pytest as our primary testing framework. The project includes several types of tests:

- **Unit tests** for individual components (nodes, services, etc.)
- **Integration tests** for complete workflows
- **Mock tests** for testing components that depend on external services

### 2. Mock vs. Real Testing

#### Deprecated Approach (Avoid):

Previously, the codebase included a `MockGeminiLLMClient` class directly in the production code. This approach had several downsides:
- Mixed production and testing code
- Required maintaining mock implementations in production code
- Created dependencies on testing-specific code in the production environment

#### Recommended Approach:

Now, we use pytest's built-in mocking capabilities:
1. Create proper test fixtures in test files
2. Use `unittest.mock` or custom mock classes that implement protocols
3. Keep all mock implementations in test files only

## Testing the Gemini Integration

### Option 1: Using pytest fixtures with AsyncMock

```python
@pytest.fixture
def mock_gemini_client():
    mock = AsyncMock()
    mock.generate_text = AsyncMock(return_value="Mocked response")
    return mock

@pytest.mark.asyncio
async def test_with_mock(mock_gemini_client):
    # Inject the mock into your dependencies
    deps = HelloWorldDependencies()
    deps.llm_client = mock_gemini_client
    
    # Test your component
    # ...
    
    # Verify mock was called correctly
    mock_gemini_client.generate_text.assert_called_once_with("Expected prompt")
```

### Option 2: Mocking Pydantic-AI's Agent

For testing the Pydantic-AI integration specifically:

```python
@pytest.fixture
def mock_pydantic_ai_agent():
    # Create a mock agent with the expected data attribute in the result
    agent_mock = AsyncMock()
    # Mock the run method to return an object with a data attribute
    result_mock = MagicMock()
    result_mock.data = "Mocked Pydantic-AI response"
    agent_mock.run = AsyncMock(return_value=result_mock)
    return agent_mock

@pytest.fixture
def mock_gemini_client(mock_pydantic_ai_agent):
    # Create the client with the mocked agent
    client = GeminiLLMClient(project_id="test-project")
    # Replace the agent with our mock
    client.agent = mock_pydantic_ai_agent
    return client
```

### Option 3: Using a protocol implementation (recommended)

```python
class MockLLM(LLMClient):
    def __init__(self, response="Mocked response"):
        self.response = response
        self.calls = []
        
    async def generate_text(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.response

@pytest.mark.asyncio
async def test_with_protocol_mock():
    # Create mock
    mock_llm = MockLLM()
    
    # Inject the mock
    deps = HelloWorldDependencies()
    deps.llm_client = mock_llm
    
    # Test your component
    # ...
    
    # Verify mock was called correctly
    assert len(mock_llm.calls) == 1
    assert mock_llm.calls[0] == "Expected prompt"
```

### Option 4: Using monkeypatch

```python
@pytest.fixture
def mock_gemini_with_monkeypatch(monkeypatch):
    class MockGemini:
        def __init__(self, *args, **kwargs):
            pass
            
        async def generate_text(self, prompt):
            return "Mocked response"
    
    # Replace the real class with the mock
    monkeypatch.setattr("hello_world.core.dependencies.GeminiLLMClient", MockGemini)
    return MockGemini()
```

## Running Tests

### Running Specific Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_nodes.py

# Run specific test
python -m pytest tests/test_nodes.py::test_gemini_agent_node_with_mock
```

### Test Categories

- **Node Tests**: Tests for individual graph nodes
- **Service Tests**: Tests for API service functions
- **Client Tests**: Tests for LLM clients
- **Integration Tests**: End-to-end tests of workflows

## Best Practices

1. **Keep mocks in test files**: Never implement mock classes in production code
2. **Test against protocols**: Create mocks that implement the same protocol as real implementations
3. **Use dependency injection**: Make it easy to swap real implementations with test mocks
4. **Skip API-dependent tests**: Use pytest.skip for tests that require real API access if credentials aren't available
5. **Test both success and failure cases**: Verify how your code handles errors
6. **Integration test with caution**: Ensure integration tests run only when needed and don't hit production APIs unnecessarily
7. **Separate unit and integration tests**: Have clear separation to keep your test suite fast

## Example: Testing Complete Workflow

```python
@pytest.mark.asyncio
async def test_gemini_workflow():
    # Set up mock
    mock_llm = MockLLM(response="AI response to test prompt")
    
    # Create dependencies with mock
    deps = HelloWorldDependencies(use_gemini=True)
    deps.llm_client = mock_llm
    
    # Run the workflow
    user_prompt = "Test prompt"
    output, state, _ = await run_gemini_agent_graph(user_prompt, dependencies=deps)
    
    # Verify results
    assert output == "AI response to test prompt"
    assert state.user_prompt == "Test prompt"
    assert state.ai_response == "AI response to test prompt"
```

## Transition Plan

If you need to use the deprecated `--use-mock-gemini` flag temporarily:

1. The flag will show deprecation warnings
2. As soon as possible, update your tests to use proper pytest fixtures
3. The mock implementation will be fully removed in a future version 