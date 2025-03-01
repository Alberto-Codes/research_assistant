# Test CLI Script for Research Agent
# This script runs various CLI commands to test functionality

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Research Agent CLI Test Script" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Function to run a command and display the result
function Run-Test {
    param (
        [string]$Name,
        [string]$Command
    )
    
    Write-Host "TEST: $Name" -ForegroundColor Green
    Write-Host "Command: $Command" -ForegroundColor Yellow
    Write-Host ""
    
    try {
        Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "RESULT: SUCCESS" -ForegroundColor Green
        } else {
            Write-Host "RESULT: FAILED (Exit code $LASTEXITCODE)" -ForegroundColor Red
        }
    } catch {
        Write-Host "RESULT: ERROR - $_" -ForegroundColor Red
    }
    
    Write-Host "==============================================" -ForegroundColor Cyan
    Write-Host ""
}

# Check if data directory exists
if (Test-Path -Path "data") {
    Write-Host "Using existing data directory for ingestion tests" -ForegroundColor Cyan
    
    # List the files in the data directory
    $files = Get-ChildItem -Path "data" -File
    Write-Host "Found $($files.Count) files in data directory:" -ForegroundColor Cyan
    foreach ($file in $files) {
        Write-Host "  - $($file.Name)" -ForegroundColor Gray
    }
    Write-Host ""
} else {
    Write-Host "WARNING: No data directory found. Ingestion tests might fail." -ForegroundColor Yellow
    Write-Host ""
}

# Test 1: Show help
Write-Host "TEST: Help Command"
$helpCmd = "pipenv run python -m research_agent --help"
Write-Host "Command: $helpCmd"
Write-Host ""
Invoke-Expression $helpCmd
if ($LASTEXITCODE -eq 0) {
    Write-Host "RESULT: SUCCESS"
} else {
    Write-Host "RESULT: FAILED (Exit code $LASTEXITCODE)"
}
Write-Host "=============================================="
Write-Host ""

# Test 2: Gemini command with a simple prompt
Write-Host "TEST: Gemini Chat"
$geminiCmd = "pipenv run python -m research_agent --log-level DEBUG cli gemini --prompt `"What is the capital of France?`""
Write-Host "Command: $geminiCmd"
Write-Host ""
Invoke-Expression $geminiCmd
if ($LASTEXITCODE -eq 0) {
    Write-Host "RESULT: SUCCESS"
} else {
    Write-Host "RESULT: FAILED (Exit code $LASTEXITCODE)"
}
Write-Host "=============================================="
Write-Host ""

# Test 3: Document ingestion using the existing data directory
Write-Host "TEST: Document Ingestion"
$ingestCmd = "pipenv run python -m research_agent --log-level DEBUG cli ingest --data-dir `"data`" --collection `"test_collection`""
Write-Host "Command: $ingestCmd"
Write-Host ""
Invoke-Expression $ingestCmd
if ($LASTEXITCODE -eq 0) {
    Write-Host "RESULT: SUCCESS"
} else {
    Write-Host "RESULT: FAILED (Exit code $LASTEXITCODE)"
}
Write-Host "=============================================="
Write-Host ""

# Test 4: Document ingestion followed by a gemini query about the documents
Write-Host "TEST: End-to-End Test"
$e2eCmd = "pipenv run python -m research_agent --log-level DEBUG cli gemini --prompt `"Summarize what you know about the documents I just added.`""
Write-Host "Command: $e2eCmd"
Write-Host ""
Invoke-Expression $e2eCmd
if ($LASTEXITCODE -eq 0) {
    Write-Host "RESULT: SUCCESS"
} else {
    Write-Host "RESULT: FAILED (Exit code $LASTEXITCODE)"
}
Write-Host "=============================================="
Write-Host ""

Write-Host "All tests completed!" -ForegroundColor Green 