# Gemini Integration Guide

This document explains how to use the Gemini AI model integration in the Research Agent project using Pydantic-AI.

## Overview

The Research Agent project uses Google's Gemini AI models via Vertex AI, integrated through the Pydantic-AI library. This approach provides several benefits:

- Simplified authentication
- Improved reliability
- Better error handling
- Automatic project detection

## Setup

### Prerequisites

1. Google Cloud account with Vertex AI API enabled
2. Application Default Credentials (ADC) configured

### Installation

The required dependencies are included in the project's setup:

```bash
# Install the project with all dependencies
pip install -e .
```

## Authentication

The project supports two authentication methods:

1. **Application Default Credentials (ADC)** - Recommended for development
   ```bash
   gcloud auth application-default login
   ```

2. **Service Account** - Recommended for production
   ```bash
   # Export the path to your service account key
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account-key.json
   ```

### Project ID Configuration

The project ID is automatically detected from:

1. The `--project-id` CLI parameter if provided
2. Google Cloud SDK configuration if available
3. Service account credentials if using a service account

Ensure you have a default project set:

```bash
gcloud config set project YOUR_PROJECT_ID
```

## Using the Gemini Integration

### Command Line

```bash
python -m research_agent.cli.commands gemini --prompt "Your prompt here"
```

Optional parameters:
- `--project-id PROJECT_ID`: Specify a Google Cloud project ID

### Interactive Chat UI

The project provides a fully featured chat interface for interacting with Gemini models:

```bash
# Launch the Gemini Chat UI
python -m research_agent.ui.cli_entry --app gemini
```

Or if you've installed the package:

```bash
research_agent --app gemini
```

Features of the Gemini Chat UI:
- Streaming responses for a natural conversation experience
- Custom system prompt configuration
- Conversation memory that can be toggled on/off
- Response metrics and debugging information
- Conversation saving functionality
- Optimized async implementation with reliable event loop handling

### Programmatic Usage

```python
from research_agent.api.services import generate_ai_response

# Generate a response
response = await generate_ai_response(
    user_prompt="What are the three laws of robotics?",
    project_id="your-project-id"  # Optional
)

print(response.ai_response)
```

### Using the Pydantic-AI Integration Directly

You can also use the Pydantic-AI integration directly:

```python
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_ai import Agent

# Initialize the model and agent
model = VertexAIModel(
    "gemini-1.5-flash-001",
    project_id="your-project-id",  # Optional
    region="us-central1"           # Optional, defaults to us-central1
)

agent = Agent(model)

# Generate a response
result = await agent.run("What are the three laws of robotics?")
print(result.data)
```

## Troubleshooting

### Missing Project ID

If you encounter an error about a missing project ID:

1. Make sure you have authenticated with `gcloud auth application-default login`
2. Set a default project with `gcloud config set project YOUR_PROJECT_ID`
3. Or explicitly pass the project ID parameter

### Authentication Errors

Authentication errors may occur if:

1. You haven't enabled the Vertex AI API in your project
2. Your account doesn't have appropriate permissions
3. Your service account credentials are invalid

Check your permissions and API status in the Google Cloud Console.

### Event Loop Issues

If you encounter event loop errors when using the Gemini Chat UI:

1. Make sure you're using the latest version of the package
2. The application now uses nest_asyncio to handle nested event loops properly
3. The streaming implementation has been completely refactored for reliability

If issues persist, please report them with specific error messages. 