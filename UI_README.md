# Research Agent UI

This document provides instructions for launching and using the Research Agent UI.

## Requirements

- Python 3.10 or higher
- Pipenv (for dependency management)
- Google Cloud credentials (for Gemini API access)

## Launching the UI

The UI can be launched using the `run_ui.ps1` PowerShell script:

```powershell
# Launch with default port (8501)
.\run_ui.ps1

# Launch with custom port
.\run_ui.ps1 -Port 8080
```

## Troubleshooting

### Authentication Issues

If you encounter errors related to Google authentication, make sure you have:

1. Set up your Google Cloud credentials by setting the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

   ```powershell
   $env:GOOGLE_APPLICATION_CREDENTIALS = "path\to\your\credentials.json"
   ```

2. Enabled the required APIs in your Google Cloud project:
   - Vertex AI API
   - Gemini API

3. Created a service account with appropriate permissions

### Common Errors

#### "Streamed response ended without content or tool calls"

This error typically indicates an authentication or API access issue. Check your credentials and ensure your Google Cloud project has the necessary APIs enabled.

#### "quota exceeded" or "API not enabled"

You may need to set up a quota project or enable the required APIs in your Google Cloud project.

## Using the UI

Once launched, the UI will be available in your web browser at:
- Local: http://localhost:[PORT]
- Network: http://[YOUR-IP]:[PORT]

The UI provides an interactive interface for interacting with the Research Agent, allowing you to:
- Input research questions
- View AI responses
- Upload and process documents 