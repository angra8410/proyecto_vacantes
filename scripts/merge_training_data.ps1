<#
.SYNOPSIS
    Merge and deduplicate JSONL training data files safely

.DESCRIPTION
    This script merges multiple training_data.jsonl files, removes duplicates,
    and handles malformed JSON lines. It includes safety features like dry-run
    mode, automatic backups, and error logging.

.PARAMETER DryRun
    Show what would be done without making any changes

.PARAMETER SourceFiles
    Array of source JSONL files to merge

.PARAMETER OutputFile
    Path to the output file (default: data/training_data.jsonl)

.PARAMETER ConfirmMove
    If specified, moves the venv\data\training_data.jsonl file after merge

.EXAMPLE
    .\merge_training_data.ps1 -DryRun
    Shows what would be merged without making changes

.EXAMPLE
    .\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -OutputFile "data\training_data.jsonl"
    Merges the files with backups

.EXAMPLE
    .\merge_training_data.ps1 -SourceFiles "data\training_data.jsonl","venv\data\training_data.jsonl" -ConfirmMove
    Merges files and moves venv\data\training_data.jsonl after confirmation
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [string[]]$SourceFiles = @("data\training_data.jsonl", "venv\data\training_data.jsonl"),
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "data\training_data.jsonl",
    
    [Parameter(Mandatory=$false)]
    [switch]$ConfirmMove
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

# Function to read JSONL file
function Read-JsonlFile {
    param(
        [string]$FilePath
    )
    
    $AbsPath = Get-AbsolutePath $FilePath
    
    if (-not (Test-Path $AbsPath)) {
        Write-Warning "File not found: $AbsPath"
        return @{
            Entries = @()
            InvalidLines = @()
        }
    }
    
    $Entries = @()
    $InvalidLines = @()
    $LineNumber = 0
    
    Get-Content $AbsPath -Encoding UTF8 | ForEach-Object {
        $LineNumber++
        $Line = $_.Trim()
        
        if ([string]::IsNullOrWhiteSpace($Line)) {
            return
        }
        
        try {
            $Entry = $_ | ConvertFrom-Json
            $Entries += $Entry
        }
        catch {
            $InvalidLines += $LineNumber
            Write-Verbose "Invalid JSON at line $LineNumber : $_"
        }
    }
    
    return @{
        Entries = $Entries
        InvalidLines = $InvalidLines
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
Write-Host "JSONL Training Data Merge Tool" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Convert paths to absolute
$AbsSourceFiles = $SourceFiles | ForEach-Object { Get-AbsolutePath $_ }
$AbsOutputFile = Get-AbsolutePath $OutputFile

# Display configuration
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Project Root: $ProjectRoot"
Write-Host "  Source Files: $($AbsSourceFiles.Count)"
foreach ($File in $AbsSourceFiles) {
    $Exists = Test-Path $File
    $Status = if ($Exists) { "✓" } else { "✗" }
    $Color = if ($Exists) { "Green" } else { "Red" }
    Write-Host "    $Status $File" -ForegroundColor $Color
}
Write-Host "  Output File: $AbsOutputFile"
Write-Host ""

# DRY RUN: Just show what would be done
if ($DryRun) {
    Write-Host "Analysis (Dry Run):" -ForegroundColor Cyan
    
    $TotalEntries = 0
    $TotalInvalid = 0
    
    foreach ($File in $AbsSourceFiles) {
        if (Test-Path $File) {
            Write-Host "  Reading: $File"
            $Result = Read-JsonlFile $File
            $TotalEntries += $Result.Entries.Count
            $TotalInvalid += $Result.InvalidLines.Count
            
            Write-Host "    Entries: $($Result.Entries.Count)" -ForegroundColor Green
            if ($Result.InvalidLines.Count -gt 0) {
                Write-Host "    Invalid lines: $($Result.InvalidLines.Count)" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
    Write-Host "Summary:" -ForegroundColor Cyan
    Write-Host "  Total entries to merge: $TotalEntries"
    Write-Host "  Invalid lines: $TotalInvalid"
    Write-Host ""
    Write-Host "To execute the merge, run without -DryRun parameter" -ForegroundColor Yellow
    exit 0
}

# ACTUAL EXECUTION: Create backups first
Write-Host "Creating backups..." -ForegroundColor Cyan
$InvalidLogPath = Join-Path $ProjectRoot "data\training_data.invalid_lines.log"

foreach ($File in $AbsSourceFiles) {
    if (Test-Path $File) {
        New-Backup $File | Out-Null
    }
}

# If output file exists and is different from sources, back it up too
if ((Test-Path $AbsOutputFile) -and ($AbsSourceFiles -notcontains $AbsOutputFile)) {
    New-Backup $AbsOutputFile | Out-Null
}

Write-Host ""

# Read all files and merge
Write-Host "Reading source files..." -ForegroundColor Cyan
$AllEntries = @()
$SeenTexts = @{}
$TotalDuplicates = 0
$AllInvalidLines = @()

foreach ($File in $AbsSourceFiles) {
    if (-not (Test-Path $File)) {
        Write-Warning "Skipping non-existent file: $File"
        continue
    }
    
    Write-Host "  Processing: $File"
    $Result = Read-JsonlFile $File
    
    Write-Host "    Read: $($Result.Entries.Count) entries" -ForegroundColor Green
    
    if ($Result.InvalidLines.Count -gt 0) {
        Write-Host "    Invalid lines: $($Result.InvalidLines.Count)" -ForegroundColor Yellow
        $AllInvalidLines += "File: $File"
        $AllInvalidLines += "Invalid lines: $($Result.InvalidLines -join ', ')"
        $AllInvalidLines += ""
    }
    
    # Deduplicate based on 'text' field
    $Duplicates = 0
    foreach ($Entry in $Result.Entries) {
        $Text = $Entry.text
        if ($null -eq $Text) {
            $Text = ""
        }
        
        $TextTrimmed = $Text.Trim()
        
        if (-not $SeenTexts.ContainsKey($TextTrimmed)) {
            $SeenTexts[$TextTrimmed] = $true
            $AllEntries += $Entry
        }
        else {
            $Duplicates++
        }
    }
    
    if ($Duplicates -gt 0) {
        Write-Host "    Duplicates removed: $Duplicates" -ForegroundColor Yellow
        $TotalDuplicates += $Duplicates
    }
}

Write-Host ""

# Write invalid lines log if any
if ($AllInvalidLines.Count -gt 0) {
    $AllInvalidLines | Set-Content -Path $InvalidLogPath -Encoding UTF8
    Write-Host "✓ Invalid lines logged to: $InvalidLogPath" -ForegroundColor Yellow
}

# Write output file
Write-Host "Writing merged output..." -ForegroundColor Cyan
Write-JsonlFile -FilePath $AbsOutputFile -Entries $AllEntries

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "Merge completed successfully!" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "  Total unique entries: $($AllEntries.Count)"
Write-Host "  Duplicates removed: $TotalDuplicates"
Write-Host "  Invalid lines: $($AllInvalidLines.Count / 3)"
Write-Host "  Output file: $AbsOutputFile"
Write-Host ""

# Optional: Move venv file
if ($ConfirmMove) {
    $VenvFile = Get-AbsolutePath "venv\data\training_data.jsonl"
    
    if (Test-Path $VenvFile) {
        Write-Host "Moving venv training data file..." -ForegroundColor Yellow
        $Confirmation = Read-Host "Do you want to move $VenvFile to .moved? (yes/no)"
        
        if ($Confirmation -eq "yes") {
            $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $MovedPath = "$VenvFile.moved.$Timestamp"
            
            Move-Item -Path $VenvFile -Destination $MovedPath -Force
            Write-Host "✓ File moved to: $MovedPath" -ForegroundColor Green
        }
        else {
            Write-Host "Skipped moving file" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "No venv file found to move" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Done! Review the output file and verify the merge was successful." -ForegroundColor Cyan
