# Research Agent UI Launcher
# This script launches the Research Agent's Streamlit UI
#
# Usage:
#   .\run_ui.ps1                  # Run with default port (8501)
#   .\run_ui.ps1 -Port 8080       # Run with custom port
#
param(
    [int]$Port = 8501  # Default port is 8501 (Streamlit's default)
)

# Set the title of the PowerShell window
$host.UI.RawUI.WindowTitle = "Research Agent UI"

Write-Host "Launching Research Agent UI on port $Port..."

# Check if credentials are set up
if (-not (Test-Path env:GOOGLE_APPLICATION_CREDENTIALS)) {
    Write-Host "Warning: GOOGLE_APPLICATION_CREDENTIALS environment variable is not set." -ForegroundColor Yellow
    Write-Host "You may encounter authentication issues with Google APIs." -ForegroundColor Yellow
    Write-Host ""
}

# Get the path to the Streamlit app
$streamlitAppPath = Join-Path -Path (Get-Location) -ChildPath "src\research_agent\ui\streamlit\gemini_chat.py"

# Verify file exists
if (-not (Test-Path $streamlitAppPath)) {
    Write-Host "Error: Streamlit application file not found at: $streamlitAppPath" -ForegroundColor Red
    exit 1
}

# Run Streamlit directly
try {
    Write-Host "Running Streamlit app from: $streamlitAppPath"
    pipenv run streamlit run $streamlitAppPath --server.port $Port
}
catch {
    Write-Host "Error launching the UI: $_" -ForegroundColor Red
    exit 1
} 