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

# Run the UI application
try {
    pipenv run python -m research_agent ui --port $Port
}
catch {
    Write-Host "Error launching the UI: $_" -ForegroundColor Red
    exit 1
} 