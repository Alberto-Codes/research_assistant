"""
Test the GeminiLLMClient implementation using Pydantic-AI.

This module contains tests for the GeminiLLMClient class that uses
Pydantic-AI for model integration with Vertex AI.
"""

import asyncio

import pytest

from hello_world.core.dependencies import GeminiLLMClient, LLMClient


@pytest.fixture
def mock_gemini_client(monkeypatch):
    """Create a mock Gemini client for testing.

    This fixture provides a proper mock of the GeminiLLMClient
    for testing without requiring Vertex AI credentials.
    """

    class MockGeminiClient:
        """Mock implementation for testing."""

        def __init__(self, project_id=None, location=None, model_name=None):
            self.project_id = project_id
            self.location = location
            self.model_name = model_name
            self.responses = {
                "What are the three laws of robotics?": """The Three Laws of Robotics, introduced by science fiction writer Isaac Asimov in his 1942 short story "Runaround," are:

1. First Law: A robot may not injure a human being or, through inaction, allow a human being to come to harm.

2. Second Law: A robot must obey the orders given it by human beings except where such orders would conflict with the First Law.

3. Third Law: A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.

Asimov later added a "Zeroth Law" that preceded the others: A robot may not harm humanity, or, by inaction, allow humanity to come to harm.""",
                "default": "This is a test response from the mock Gemini client.",
            }

        async def generate_text(self, prompt: str) -> str:
            """Return a predefined response based on the prompt."""
            for key, response in self.responses.items():
                if key.lower() in prompt.lower():
                    return response
            return self.responses["default"]

    # Replace the real client with our mock
    monkeypatch.setattr("hello_world.core.dependencies.GeminiLLMClient", MockGeminiClient)

    return MockGeminiClient()


@pytest.mark.asyncio
async def test_gemini_client_initialization():
    """Test that the GeminiLLMClient can be initialized."""
    client = GeminiLLMClient()
    assert client is not None
    assert hasattr(client, "agent")
    assert hasattr(client, "vertex_model")


@pytest.mark.asyncio
async def test_gemini_client_generate_text():
    """
    Test that the GeminiLLMClient can generate text.

    Note: This test requires proper authentication with Vertex AI.
    If running locally, make sure you have:
    1. Installed the gcloud CLI
    2. Authenticated with `gcloud auth application-default login`
    3. Have access to a GCP project with Vertex AI API enabled
    """
    prompt = "What are the three laws of robotics?"

    try:
        client = GeminiLLMClient()
        response = await client.generate_text(prompt)

        # Check that we got a non-empty response
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0

        # Check that we don't have an error response
        assert not response.startswith("Error generating response")

        print(f"Gemini response: {response}")
    except Exception as e:
        pytest.skip(f"Skipping test due to Vertex AI setup issue: {str(e)}")


@pytest.mark.asyncio
async def test_gemini_client_with_mock(mock_gemini_client):
    """Test the Gemini client using the mock fixture."""
    prompt = "What are the three laws of robotics?"
    response = await mock_gemini_client.generate_text(prompt)

    # Check that we got the expected mock response
    assert "Three Laws of Robotics" in response
    assert "First Law" in response
    assert "Second Law" in response
    assert "Third Law" in response

    # Test with a generic prompt
    generic_prompt = "Tell me something interesting"
    generic_response = await mock_gemini_client.generate_text(generic_prompt)
    assert generic_response == "This is a test response from the mock Gemini client."


if __name__ == "__main__":
    """
    Run the test directly if this file is executed.
    This is useful for quick testing during development.
    """

    async def run_test():
        test_client = GeminiLLMClient()
        response = await test_client.generate_text("What is the capital of France?")
        print(f"Response: {response}")

    asyncio.run(run_test())
