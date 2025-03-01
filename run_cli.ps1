# Test CLI Script for Research Agent
# This script runs various CLI commands to test functionality

# Command line arguments - use simple variables instead of complex parameter system
$TestName = "all"  # Default test to run
$DebugMode = $false  # Debug mode flag
$Collection = "test_collection"  # Default collection name
$DataDir = "data"  # Default data directory

# Check if arguments were provided
if ($args.Count -gt 0) {
    $TestName = $args[0]
}

# Check for debug flag in any position
foreach ($arg in $args) {
    if ($arg -eq "-debug" -or $arg -eq "-d") {
        $DebugMode = $true
    }
}

# Set log level based on debug mode
$LogLevel = if ($DebugMode) { "DEBUG" } else { "INFO" }

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Research Agent CLI Development Test Script" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Test: $TestName" -ForegroundColor Yellow
Write-Host "Log Level: $LogLevel" -ForegroundColor Yellow
Write-Host "Collection: $Collection" -ForegroundColor Yellow
Write-Host "Data Directory: $DataDir" -ForegroundColor Yellow
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
        # Create a temp file for output
        $outputFile = New-TemporaryFile
        
        # Run the command and capture output to the temp file
        Invoke-Expression "$Command *> $outputFile"
        $result = $LASTEXITCODE -eq 0
        
        # Read and display the output
        $output = Get-Content -Path $outputFile -Raw
        Write-Host "COMMAND OUTPUT:" -ForegroundColor Cyan
        Write-Host $output
        
        # Remove the temp file
        Remove-Item -Path $outputFile -Force
        
        if ($result) {
            Write-Host "RESULT: SUCCESS" -ForegroundColor Green
            return $true
        } else {
            Write-Host "RESULT: FAILED (Exit code $LASTEXITCODE)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "RESULT: ERROR - $_" -ForegroundColor Red
        return $false
    } finally {
        Write-Host "==============================================" -ForegroundColor Cyan
        Write-Host ""
    }
}

# Check if data directory exists
if (Test-Path -Path $DataDir) {
    Write-Host "Using existing data directory for ingestion tests: $DataDir" -ForegroundColor Cyan
    
    # List the files in the data directory
    $files = Get-ChildItem -Path $DataDir -File
    Write-Host "Found $($files.Count) files in data directory:" -ForegroundColor Cyan
    foreach ($file in $files) {
        Write-Host "  - $($file.Name)" -ForegroundColor Gray
    }
    Write-Host ""
} else {
    Write-Host "WARNING: Data directory '$DataDir' not found. Ingestion tests might fail." -ForegroundColor Yellow
    Write-Host ""
}

# Run the specified test
$success = $true

# Run the help command test
function Test-Help {
    return Run-Test -Name "Help Command" -Command "pipenv run python -m research_agent --log-level $LogLevel --help"
}

# Run the Gemini chat test
function Test-Gemini {
    return Run-Test -Name "Gemini Chat" -Command "pipenv run python -m research_agent --log-level $LogLevel cli gemini --prompt `"What is the capital of France?`""
}

# Run the document ingestion test
function Test-Ingest {
    return Run-Test -Name "Document Ingestion" -Command "pipenv run python -m research_agent --log-level $LogLevel cli ingest --data-dir `"$DataDir`" --collection `"$Collection`""
}

# Run the end-to-end Gemini test
function Test-E2EGemini {
    return Run-Test -Name "End-to-End Gemini Test" -Command "pipenv run python -m research_agent --log-level $LogLevel cli gemini --prompt `"Summarize what you know about the documents I just added to collection $Collection.`""
}

# RAG Tests
function Test-RAGSimple {
    return Run-Test -Name "RAG Simple Query" -Command "pipenv run python -m research_agent --log-level $LogLevel cli rag --query `"test`" --collection `"$Collection`""
}

function Test-RAGSummary {
    return Run-Test -Name "RAG Document Summary" -Command "pipenv run python -m research_agent --log-level $LogLevel cli rag --query `"Please summarize the contents of the documents.`" --collection `"$Collection`""
}

function Test-RAGSpecific {
    return Run-Test -Name "RAG Specific Query" -Command "pipenv run python -m research_agent --log-level $LogLevel cli rag --query `"What information does the document contain about ChromaDB?`" --collection `"$Collection`""
}

# Debugging tests
function Test-DebugModel {
    return Run-Test -Name "Debug Model Configuration" -Command "pipenv run python -m research_agent --log-level DEBUG cli gemini --prompt `"Hello, can you confirm what model you are?`""
}

function Test-DebugChroma {
    return Run-Test -Name "Debug ChromaDB Collections" -Command "pipenv run python -c `"import chromadb; client = chromadb.PersistentClient('./chroma_db'); print('Collections:', client.list_collections()); collection = client.get_collection('$Collection'); print('Document count:', collection.count()); print('Sample documents:', collection.get(limit=2))`""
}

# Function to run all tests
function Test-All {
    $success = $true
    
    $success = Test-Help -and $success
    $success = Test-Gemini -and $success
    
    # Ingest documents first
    $ingestSuccess = Test-Ingest
    $success = $ingestSuccess -and $success
    
    # Only run these if ingestion succeeded
    if ($ingestSuccess) {
        $success = Test-E2EGemini -and $success
        $success = Test-RAGSimple -and $success
        $success = Test-RAGSummary -and $success
        $success = Test-RAGSpecific -and $success
    } else {
        Write-Host "Skipping RAG and E2E tests as document ingestion failed" -ForegroundColor Yellow
    }
    
    return $success
}

# Function to run RAG tests
function Test-RAG {
    $success = $true
    
    # Ingest documents first
    $ingestSuccess = Test-Ingest
    $success = $ingestSuccess -and $success
    
    # Only run these if ingestion succeeded
    if ($ingestSuccess) {
        $success = Test-RAGSimple -and $success
        $success = Test-RAGSummary -and $success
        $success = Test-RAGSpecific -and $success
    } else {
        Write-Host "Skipping RAG tests as document ingestion failed" -ForegroundColor Yellow
    }
    
    return $success
}

# Function to run debug tests
function Test-Debug {
    $success = $true
    $success = Test-DebugModel -and $success
    $success = Test-DebugChroma -and $success
    return $success
}

# Run the specified test
switch ($TestName.ToLower()) {
    "all" { $success = Test-All }
    "help" { $success = Test-Help }
    "gemini" { $success = Test-Gemini }
    "ingest" { $success = Test-Ingest }
    "e2e_gemini" { $success = Test-E2EGemini }
    "rag_simple" { $success = Test-RAGSimple }
    "rag_summary" { $success = Test-RAGSummary }
    "rag_specific" { $success = Test-RAGSpecific }
    "debug_model" { $success = Test-DebugModel }
    "debug_chroma" { $success = Test-DebugChroma }
    "debug" { $success = Test-Debug }
    "rag" { $success = Test-RAG }
    default {
        Write-Host "Unknown test: $TestName" -ForegroundColor Red
        Write-Host "Available tests: all, help, gemini, ingest, e2e_gemini, rag_simple, rag_summary, rag_specific, debug_model, debug_chroma, debug, rag" -ForegroundColor Yellow
        $success = $false
    }
}

if ($success) {
    Write-Host "All tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Some tests failed. Review output for details." -ForegroundColor Red
}

# Return success status as exit code
if (-not $success) {
    exit 1
}