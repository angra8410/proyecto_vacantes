<#
.SYNOPSIS
    Deduplicate and clean JSONL training data file

.DESCRIPTION
    This script reads a JSONL file, removes duplicate entries based on the 'text' field,
    removes entries with empty or whitespace-only text, and validates JSON structure.
    It creates automatic backups before making changes.

.PARAMETER InputFile
    Path to the input JSONL file (default: data/training_data.jsonl)

.PARAMETER OutputFile
    Path to the output file (default: same as input file)

.PARAMETER DryRun
    Show what would be done without making any changes

.PARAMETER MinTextLength
    Minimum text length to keep (default: 10 characters)

.PARAMETER RemoveEmpty
    Remove entries with empty or whitespace-only text

.EXAMPLE
    .\dedupe_clean.ps1 -DryRun
    Preview deduplication without making changes

.EXAMPLE
    .\dedupe_clean.ps1 -InputFile "data\training_data.jsonl"
    Deduplicate the file with automatic backup

.EXAMPLE
    .\dedupe_clean.ps1 -InputFile "data\training_data.jsonl" -MinTextLength 20 -RemoveEmpty
    Deduplicate and remove short or empty entries
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$InputFile = "data\training_data.jsonl",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [int]$MinTextLength = 10,
    
    [Parameter(Mandatory=$false)]
    [switch]$RemoveEmpty
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Get project root (assuming script is in scripts/ folder)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Function to get absolute path
function Get-AbsolutePath {
    param([string]$Path)
    
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }
    return Join-Path $ProjectRoot $Path
}

# Function to create backup with timestamp
function New-Backup {
    param(
        [string]$FilePath
    )
    
    $AbsPath = Get-AbsolutePath $FilePath
    
    if (-not (Test-Path $AbsPath)) {
        Write-Warning "File not found, skipping backup: $AbsPath"
        return $null
    }
    
    $FileInfo = Get-Item $AbsPath
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupDir = Join-Path $ProjectRoot "backups"
    
    if (-not (Test-Path $BackupDir)) {
        New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    }
    
    $BackupName = "$($FileInfo.BaseName)_$Timestamp$($FileInfo.Extension).bak"
    $BackupPath = Join-Path $BackupDir $BackupName
    
    Copy-Item -Path $AbsPath -Destination $BackupPath -Force
    Write-Host "✓ Backup created: $BackupPath" -ForegroundColor Green
    
    return $BackupPath
}

# Function to read and analyze JSONL file
function Read-JsonlFile {
    param(
        [string]$FilePath
    )
    
    $AbsPath = Get-AbsolutePath $FilePath
    
    if (-not (Test-Path $AbsPath)) {
        throw "File not found: $AbsPath"
    }
    
    $Entries = @()
    $InvalidLines = @()
    $EmptyLines = 0
    $LineNumber = 0
    
    Get-Content $AbsPath -Encoding UTF8 | ForEach-Object {
        $LineNumber++
        $Line = $_.Trim()
        
        if ([string]::IsNullOrWhiteSpace($Line)) {
            $EmptyLines++
            return
        }
        
        try {
            $Entry = $_ | ConvertFrom-Json
            $Entries += $Entry
        }
        catch {
            $InvalidLines += @{
                LineNumber = $LineNumber
                Content = $Line.Substring(0, [Math]::Min(50, $Line.Length))
                Error = $_.Exception.Message
            }
            Write-Verbose "Invalid JSON at line $LineNumber : $_"
        }
    }
    
    return @{
        Entries = $Entries
        InvalidLines = $InvalidLines
        EmptyLines = $EmptyLines
    }
}

# Function to write JSONL file
function Write-JsonlFile {
    param(
        [string]$FilePath,
        [array]$Entries
    )
    
    $AbsPath = Get-AbsolutePath $FilePath
    $DirPath = Split-Path -Parent $AbsPath
    
    if (-not (Test-Path $DirPath)) {
        New-Item -ItemType Directory -Path $DirPath -Force | Out-Null
    }
    
    $Entries | ForEach-Object {
        $_ | ConvertTo-Json -Compress
    } | Set-Content -Path $AbsPath -Encoding UTF8
    
    Write-Host "✓ Written $($Entries.Count) entries to: $AbsPath" -ForegroundColor Green
}

# Main execution
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "JSONL Deduplication and Cleaning Tool" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Set output file to input file if not specified
if ([string]::IsNullOrWhiteSpace($OutputFile)) {
    $OutputFile = $InputFile
}

# Convert paths to absolute
$AbsInputFile = Get-AbsolutePath $InputFile
$AbsOutputFile = Get-AbsolutePath $OutputFile

# Display configuration
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project Root: $ProjectRoot"
Write-Host "  Input File: $AbsInputFile"
Write-Host "  Output File: $AbsOutputFile"
Write-Host "  Min Text Length: $MinTextLength characters"
Write-Host "  Remove Empty: $RemoveEmpty"
Write-Host ""

# Check if input file exists
if (-not (Test-Path $AbsInputFile)) {
    Write-Error "Input file not found: $AbsInputFile"
    exit 1
}

# Read and analyze file
Write-Host "Reading and analyzing file..." -ForegroundColor Cyan
$Result = Read-JsonlFile $AbsInputFile

$TotalRead = $Result.Entries.Count
$InvalidCount = $Result.InvalidLines.Count
$EmptyLineCount = $Result.EmptyLines

Write-Host "  Total entries read: $TotalRead" -ForegroundColor Green
Write-Host "  Empty lines: $EmptyLineCount" -ForegroundColor Gray

if ($InvalidCount -gt 0) {
    Write-Host "  Invalid JSON lines: $InvalidCount" -ForegroundColor Yellow
    if ($Result.InvalidLines.Count -le 5) {
        foreach ($Invalid in $Result.InvalidLines) {
            Write-Host "    Line $($Invalid.LineNumber): $($Invalid.Content)..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "    (showing first 5 of $InvalidCount)" -ForegroundColor Yellow
        foreach ($Invalid in $Result.InvalidLines[0..4]) {
            Write-Host "    Line $($Invalid.LineNumber): $($Invalid.Content)..." -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# Process entries
Write-Host "Processing entries..." -ForegroundColor Cyan

$CleanEntries = @()
$SeenTexts = @{}
$DuplicateCount = 0
$ShortTextCount = 0
$EmptyTextCount = 0

foreach ($Entry in $Result.Entries) {
    $Text = $Entry.text
    
    if ($null -eq $Text) {
        $Text = ""
    }
    
    $TextTrimmed = $Text.Trim()
    
    # Check for empty text
    if ([string]::IsNullOrWhiteSpace($TextTrimmed)) {
        $EmptyTextCount++
        if ($RemoveEmpty) {
            continue
        }
    }
    
    # Check for short text
    if ($TextTrimmed.Length -lt $MinTextLength) {
        $ShortTextCount++
        continue
    }
    
    # Check for duplicates
    if ($SeenTexts.ContainsKey($TextTrimmed)) {
        $DuplicateCount++
        continue
    }
    
    # Add to clean entries
    $SeenTexts[$TextTrimmed] = $true
    $CleanEntries += $Entry
}

# Display statistics
Write-Host ""
Write-Host "Statistics:" -ForegroundColor Cyan
Write-Host "  Original entries: $TotalRead" -ForegroundColor White
Write-Host "  Duplicates removed: $DuplicateCount" -ForegroundColor Yellow
Write-Host "  Short texts removed (< $MinTextLength chars): $ShortTextCount" -ForegroundColor Yellow

if ($RemoveEmpty) {
    Write-Host "  Empty texts removed: $EmptyTextCount" -ForegroundColor Yellow
} elseif ($EmptyTextCount -gt 0) {
    Write-Host "  Empty texts found (not removed): $EmptyTextCount" -ForegroundColor Gray
}

Write-Host "  Final unique entries: $($CleanEntries.Count)" -ForegroundColor Green
Write-Host ""

# Calculate reduction
$ReductionCount = $TotalRead - $CleanEntries.Count
$ReductionPercent = if ($TotalRead -gt 0) { ($ReductionCount / $TotalRead) * 100 } else { 0 }

Write-Host "Reduction: $ReductionCount entries ($($ReductionPercent.ToString('F2'))%)" -ForegroundColor Cyan
Write-Host ""

# DRY RUN: Stop here
if ($DryRun) {
    Write-Host "Dry run complete. Run without -DryRun to apply changes." -ForegroundColor Yellow
    exit 0
}

# ACTUAL EXECUTION: Create backup
if (Test-Path $AbsInputFile) {
    Write-Host "Creating backup..." -ForegroundColor Cyan
    New-Backup $AbsInputFile | Out-Null
    Write-Host ""
}

# Write cleaned file
Write-Host "Writing cleaned output..." -ForegroundColor Cyan
Write-JsonlFile -FilePath $AbsOutputFile -Entries $CleanEntries

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Cleaning completed successfully!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  Input file: $AbsInputFile"
Write-Host "  Output file: $AbsOutputFile"
Write-Host "  Entries: $TotalRead → $($CleanEntries.Count)"
Write-Host ""
Write-Host "Done! Review the output file to verify the results." -ForegroundColor Cyan
