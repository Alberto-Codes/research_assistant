# Test CLI Script for Research Agent
# This script runs various CLI commands to test functionality

# Command line arguments - use simple variables instead of complex parameter system
$TestName = "all"  # Default test to run
$DebugMode = $false  # Debug mode flag
$Collection = "test_collection"  # Default collection name
$DataDir = "data"  # Default data directory
$DeleteDB = $false  # Flag to delete existing DB before test

# Check if arguments were provided
if ($args.Count -gt 0) {
    $TestName = $args[0]
}

# Check for debug flag in any position
foreach ($arg in $args) {
    if ($arg -eq "-debug" -or $arg -eq "-d") {
        $DebugMode = $true
    }
    if ($arg -eq "-clean" -or $arg -eq "-c") {
        $DeleteDB = $true
    }
}

# Set log level based on debug mode
$LogLevel = if ($DebugMode) { "DEBUG" } else { "INFO" }

# Set UTF-8 encoding for the console to handle Unicode characters
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Research Agent CLI Development Test Script" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Test: $TestName" -ForegroundColor Yellow
Write-Host "Log Level: $LogLevel" -ForegroundColor Yellow
Write-Host "Collection: $Collection" -ForegroundColor Yellow
Write-Host "Data Directory: $DataDir" -ForegroundColor Yellow
Write-Host "Clean DB: $DeleteDB" -ForegroundColor Yellow
Write-Host ""

# Delete ChromaDB if flagged
if ($DeleteDB) {
    $ChromaDBPath = "./chroma_db"
    if (Test-Path -Path $ChromaDBPath) {
        Write-Host "Deleting existing ChromaDB at $ChromaDBPath" -ForegroundColor Yellow
        Remove-Item -Path $ChromaDBPath -Recurse -Force
        Write-Host "ChromaDB directory removed" -ForegroundColor Green
    } else {
        Write-Host "No existing ChromaDB found at $ChromaDBPath" -ForegroundColor Cyan
    }
    Write-Host ""
}

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
        
        # Run the command and capture output to the temp file, ensuring UTF-8 encoding
        Invoke-Expression "$Command *> $outputFile"
        $result = $LASTEXITCODE -eq 0
        
        # Read and display the output with UTF-8 encoding
        $output = Get-Content -Path $outputFile -Raw -Encoding UTF8
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

# Check if data directory exists and analyze file types
if (Test-Path -Path $DataDir) {
    Write-Host "Using existing data directory for ingestion tests: $DataDir" -ForegroundColor Cyan
    
    # Group files by extension
    $files = Get-ChildItem -Path $DataDir -File
    $filesByExtension = $files | Group-Object -Property Extension
    
    # Display summary of files by extension
    Write-Host "Found $($files.Count) files in data directory, organized by type:" -ForegroundColor Cyan
    foreach ($group in $filesByExtension) {
        Write-Host "  - $($group.Name) files: $($group.Count)" -ForegroundColor Gray
        foreach ($file in $group.Group) {
            Write-Host "      - $($file.Name)" -ForegroundColor DarkGray
        }
    }
    
    # Check for files with same base name but different extensions
    $baseNames = $files | ForEach-Object { $_.BaseName } | Group-Object
    $duplicateBaseNames = $baseNames | Where-Object { $_.Count -gt 1 }
    
    if ($duplicateBaseNames.Count -gt 0) {
        Write-Host "`nFiles with the same base name but different extensions:" -ForegroundColor Yellow
        foreach ($duplicate in $duplicateBaseNames) {
            $duplicateFiles = $files | Where-Object { $_.BaseName -eq $duplicate.Name }
            Write-Host "  - Base name: $($duplicate.Name)" -ForegroundColor DarkYellow
            foreach ($file in $duplicateFiles) {
                Write-Host "      - $($file.Name)" -ForegroundColor DarkGray
            }
        }
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

# Run the document ingestion test with specific file types
function Test-IngestByType {
    param (
        [string]$FileType,
        [string]$CollectionSuffix = ""
    )
    
    $typedCollection = if ($CollectionSuffix) { "${Collection}_${CollectionSuffix}" } else { $Collection }
    
    # Create a temporary directory for filtered files
    $tempDir = Join-Path -Path $PWD -ChildPath "temp_${FileType}_files"
    
    try {
        # Create temp directory if it doesn't exist
        if (-not (Test-Path -Path $tempDir)) {
            New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
            Write-Host "Created temporary directory: $tempDir" -ForegroundColor Cyan
        } else {
            # Clean the directory
            Remove-Item -Path "$tempDir\*" -Force -Recurse -ErrorAction SilentlyContinue
        }
        
        # Copy only files of the specified type to the temp directory
        $matchPattern = "*.$FileType"
        $sourceFiles = Get-ChildItem -Path $DataDir -Filter $matchPattern
        
        foreach ($file in $sourceFiles) {
            Copy-Item -Path $file.FullName -Destination $tempDir
            Write-Host "Copied $($file.Name) to temporary directory" -ForegroundColor Gray
        }
        
        Write-Host "Filtered $($sourceFiles.Count) $FileType files to temporary directory" -ForegroundColor Cyan
        
        # Run the ingestion with the filtered directory
        return Run-Test -Name "Ingestion of $FileType files" -Command "pipenv run python -m research_agent --log-level $LogLevel cli ingest --data-dir `"$tempDir`" --collection `"$typedCollection`""
    }
    finally {
        # Clean up temporary directory
        if ($DebugMode -eq $false) {
            if (Test-Path -Path $tempDir) {
                Remove-Item -Path $tempDir -Force -Recurse -ErrorAction SilentlyContinue
                Write-Host "Removed temporary directory: $tempDir" -ForegroundColor Gray
            }
        } else {
            Write-Host "Debug mode: Keeping temporary directory: $tempDir" -ForegroundColor Yellow
        }
    }
}

# Run the end-to-end Gemini test
function Test-E2EGemini {
    return Run-Test -Name "End-to-End Gemini Test" -Command "pipenv run python -m research_agent --log-level $LogLevel cli gemini --prompt `"Summarize what you know about the documents I just added to collection $Collection.`""
}

# RAG Tests
function Test-RAGSimple {
    param (
        [string]$CustomCollection = $Collection
    )
    return Run-Test -Name "RAG Simple Query" -Command "pipenv run python -m research_agent --log-level $LogLevel cli rag --query `"test`" --collection `"$CustomCollection`""
}

function Test-RAGSummary {
    param (
        [string]$CustomCollection = $Collection
    )
    return Run-Test -Name "RAG Document Summary" -Command "pipenv run python -m research_agent --log-level $LogLevel cli rag --query `"Please summarize the contents of the documents.`" --collection `"$CustomCollection`""
}

function Test-RAGSpecific {
    param (
        [string]$CustomCollection = $Collection,
        [string]$Query = "What information does the document contain about ChromaDB?"
    )
    return Run-Test -Name "RAG Specific Query" -Command "pipenv run python -m research_agent --log-level $LogLevel cli rag --query `"$Query`" --collection `"$CustomCollection`""
}

# Mexican food specific RAG tests
function Test-MexicanFoodRAG {
    param (
        [string]$CustomCollection = $Collection
    )
    
    $success = $true
    
    # Query about traditional Mexican dishes
    $success = Test-RAGSpecific -CustomCollection $CustomCollection -Query "What are some traditional Mexican dishes mentioned in the documents?" -and $success
    
    # Query about Mexican beverages
    $success = Test-RAGSpecific -CustomCollection $CustomCollection -Query "Tell me about traditional Mexican beverages and their ingredients." -and $success
    
    # Query about Mexican street food
    $success = Test-RAGSpecific -CustomCollection $CustomCollection -Query "What street foods are popular in Mexico according to the documents?" -and $success
    
    return $success
}

# Docling Test with error handling for graph visualization
function Test-Docling {
    # Create a workaround command that avoids graph visualization
    $command = "pipenv run python -m research_agent --log-level $LogLevel cli ingest --data-dir `"$DataDir`" --collection `"docling_test_collection`" --use-docling"
    
    # Run the Docling test with our custom command
    $cliSuccess = Run-Test -Name "Docling CLI Integration" -Command $command
    
    return $cliSuccess
}

# Debugging tests
function Test-DebugModel {
    return Run-Test -Name "Debug Model Configuration" -Command "pipenv run python -m research_agent --log-level DEBUG cli gemini --prompt `"Hello, can you confirm what model you are?`""
}

function Test-DebugChroma {
    param (
        [string]$CustomCollection = $Collection
    )
    return Run-Test -Name "Debug ChromaDB Collections" -Command "pipenv run python -c `"import chromadb; client = chromadb.PersistentClient('./chroma_db'); print('Collections:', client.list_collections()); collection = client.get_collection('$CustomCollection'); print('Document count:', collection.count()); print('Sample documents:', collection.get(limit=2))`""
}

# Test file type specific collections
function Test-FileTypeCollections {
    $success = $true
    
    # Ingest HTML files to html_collection
    $htmlIngestSuccess = Test-IngestByType -FileType "html" -CollectionSuffix "html"
    $success = $htmlIngestSuccess -and $success
    
    # Ingest TXT files to txt_collection
    $txtIngestSuccess = Test-IngestByType -FileType "txt" -CollectionSuffix "txt"
    $success = $txtIngestSuccess -and $success
    
    # If both ingestions succeeded, test queries against each collection
    if ($htmlIngestSuccess -and $txtIngestSuccess) {
        # Test HTML collection with Mexican food queries
        Write-Host "Testing HTML Collection with Mexican Food Queries:" -ForegroundColor Cyan
        $success = Test-MexicanFoodRAG -CustomCollection "${Collection}_html" -and $success
        
        # Test TXT collection with technical queries
        Write-Host "Testing TXT Collection with Tech Queries:" -ForegroundColor Cyan
        $success = Test-RAGSpecific -CustomCollection "${Collection}_txt" -Query "What is discussed about machine learning in the documents?" -and $success
    } else {
        Write-Host "Skipping collection-specific tests as ingestion failed" -ForegroundColor Yellow
    }
    
    return $success
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
        
        # Run special file type tests
        $success = Test-FileTypeCollections -and $success
        
        # Run Mexican food specific tests
        $success = Test-MexicanFoodRAG -and $success
        
        # Run Docling test
        $success = Test-Docling -and $success
    } else {
        Write-Host "Skipping RAG, E2E, and Docling tests as document ingestion failed" -ForegroundColor Yellow
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
        $success = Test-MexicanFoodRAG -and $success
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
    "ingest_html" { $success = Test-IngestByType -FileType "html" -CollectionSuffix "html" }
    "ingest_txt" { $success = Test-IngestByType -FileType "txt" -CollectionSuffix "txt" }
    "e2e_gemini" { $success = Test-E2EGemini }
    "rag_simple" { $success = Test-RAGSimple }
    "rag_summary" { $success = Test-RAGSummary }
    "rag_specific" { $success = Test-RAGSpecific }
    "mexican" { $success = Test-MexicanFoodRAG }
    "docling" { $success = Test-Docling }
    "debug_model" { $success = Test-DebugModel }
    "debug_chroma" { $success = Test-DebugChroma }
    "debug" { $success = Test-Debug }
    "rag" { $success = Test-RAG }
    "file_types" { $success = Test-FileTypeCollections }
    default {
        Write-Host "Unknown test: $TestName" -ForegroundColor Red
        Write-Host "Available tests: all, help, gemini, ingest, ingest_html, ingest_txt, e2e_gemini, rag_simple, rag_summary, rag_specific, mexican, docling, debug_model, debug_chroma, debug, rag, file_types" -ForegroundColor Yellow
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