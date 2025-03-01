# Testing and Coverage PowerShell Script for Research Agent
# This provides a complete solution for running tests and coverage

param (
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Run-Tests {
    Write-Host "Running all tests..." -ForegroundColor Cyan
    pipenv run pytest
}

function Run-Coverage {
    Write-Host "Running tests with coverage (terminal report)..." -ForegroundColor Cyan
    pipenv run pytest --cov=src/research_agent --cov-report=term
}

function Run-CoverageHtml {
    Write-Host "Running tests with coverage (HTML report)..." -ForegroundColor Cyan
    
    # Create directory for HTML report if it doesn't exist
    if (-not (Test-Path "coverage_html_report")) {
        New-Item -ItemType Directory -Path "coverage_html_report" -Force | Out-Null
    }
    
    # Run pytest with coverage and HTML report
    pipenv run pytest --cov=src/research_agent --cov-report=html
    
    Write-Host "Coverage report generated in coverage_html_report/" -ForegroundColor Green
    $reportPath = Join-Path -Path (Get-Location) -ChildPath "coverage_html_report\index.html"
    
    if (Test-Path $reportPath) {
        Write-Host "Report available at: $reportPath" -ForegroundColor Green
    }
}

function Run-CoverageReport {
    Write-Host "Running tests with coverage and opening browser report..." -ForegroundColor Cyan
    
    # Create directory for HTML report if it doesn't exist
    if (-not (Test-Path "coverage_html_report")) {
        New-Item -ItemType Directory -Path "coverage_html_report" -Force | Out-Null
    }
    
    # Run pytest with coverage
    Write-Host "Running tests with coverage..." -ForegroundColor Cyan
    $process = Start-Process -FilePath "pipenv" -ArgumentList "run", "pytest", "--cov=src/research_agent", "--cov-report=term", "--cov-report=html" -NoNewWindow -PassThru -Wait -RedirectStandardOutput "coverage_output.txt" -RedirectStandardError "coverage_errors.txt"
    
    # Display test output
    Write-Host "`n" + "=" * 80 -ForegroundColor Yellow
    Write-Host "TEST OUTPUT:" -ForegroundColor Yellow
    Write-Host "=" * 80 -ForegroundColor Yellow
    Get-Content -Path "coverage_output.txt"
    
    # Display any errors
    if ((Get-Item "coverage_errors.txt").Length -gt 0) {
        Write-Host "`n" + "=" * 80 -ForegroundColor Red
        Write-Host "ERRORS:" -ForegroundColor Red
        Write-Host "=" * 80 -ForegroundColor Red
        Get-Content -Path "coverage_errors.txt"
    }
    
    # Clean up temporary files
    Remove-Item -Path "coverage_output.txt" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "coverage_errors.txt" -Force -ErrorAction SilentlyContinue
    
    # Open the HTML report in the default browser
    $reportPath = Join-Path -Path (Get-Location) -ChildPath "coverage_html_report\index.html"
    if (Test-Path $reportPath) {
        Write-Host "`nCoverage report generated at: $reportPath" -ForegroundColor Green
        Write-Host "Opening coverage report in browser..." -ForegroundColor Cyan
        Start-Process $reportPath
    } else {
        Write-Host "`nWarning: Coverage HTML report not found." -ForegroundColor Yellow
    }
    
    # Return the exit code from pytest
    return $process.ExitCode
}

function Clean-Coverage {
    Write-Host "Cleaning up coverage files and Python artifacts..." -ForegroundColor Cyan
    if (Test-Path .coverage) { Remove-Item .coverage -Force }
    if (Test-Path coverage_html_report) { Remove-Item coverage_html_report -Recurse -Force }
    Get-ChildItem -Path . -Recurse -Filter "*.pyc" | Remove-Item -Force
    Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
}

function Show-Help {
    Write-Host ""
    Write-Host "Research Agent Testing Tools" -ForegroundColor Green
    Write-Host "----------------------------" -ForegroundColor Green
    Write-Host "Usage: .\run_tests.ps1 [command]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Cyan
    Write-Host "  test            Run all tests"
    Write-Host "  coverage        Run tests with coverage and display terminal report"
    Write-Host "  coverage-html   Run tests with coverage and generate HTML report"
    Write-Host "  coverage-report Run tests with coverage and open HTML report in browser"
    Write-Host "  clean           Clean up coverage files and Python artifacts"
    Write-Host "  help            Display this help message"
    Write-Host ""
    
    # Add a pause to ensure all output is visible
    Write-Host "Press any key to continue..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Process command
switch ($Command.ToLower()) {
    "test" { Run-Tests }
    "coverage" { Run-Coverage }
    "coverage-html" { Run-CoverageHtml }
    "coverage-report" { Run-CoverageReport }
    "clean" { Clean-Coverage }
    "help" { Show-Help }
    default { 
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Show-Help 
    }
} 