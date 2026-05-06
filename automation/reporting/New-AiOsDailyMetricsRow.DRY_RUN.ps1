param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN',
    [int]$ProgressPercent = 50,
    [string]$Mode = 'DRY_RUN',
    [string]$Notes = 'DRY_RUN proposed daily metrics row only.'
)

$ErrorActionPreference = 'Stop'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$date = Get-Date -Format 'yyyy-MM-dd'
$branch = 'UNKNOWN'
$gitStatusClean = 'UNKNOWN'
$totalFiles = 0
$totalFolders = 0
$totalBytes = 0

function Convert-ToCsvField {
    param([object]$Value)
    $text = [string]$Value
    $escaped = $text.Replace('"', '""')
    return '"' + $escaped + '"'
}

Write-Host 'Task name: AI_OS Stage 9E Daily Metrics Row Draft'
Write-Host 'Mode: DRY_RUN'
Write-Host 'Safety: Console-output only. Reports\DAILY_METRICS.csv is not edited.'
Write-Host 'Safety: No files are created, edited, moved, renamed, deleted, staged, committed, pushed, or launched.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host "WARN: Repo root does not exist: $RepoRoot"
}
else {
    $items = @(Get-ChildItem -LiteralPath $RepoRoot -Recurse -Force -ErrorAction SilentlyContinue)
    $files = @($items | Where-Object { -not $_.PSIsContainer })
    $folders = @($items | Where-Object { $_.PSIsContainer })
    $totalFiles = $files.Count
    $totalFolders = $folders.Count
    $totalBytes = ($files | Measure-Object -Property Length -Sum).Sum
    if ($null -eq $totalBytes) {
        $totalBytes = 0
    }

    Push-Location -LiteralPath $RepoRoot
    try {
        $gitCommand = Get-Command git -ErrorAction SilentlyContinue
        if ($gitCommand) {
            $branchOutput = @(& git branch --show-current 2>&1)
            if ($LASTEXITCODE -eq 0 -and $branchOutput.Count -gt 0) {
                $branch = [string]$branchOutput[0]
            }

            $gitStatus = @(& git status --short 2>&1)
            if ($LASTEXITCODE -eq 0) {
                $gitStatusClean = [string]($gitStatus.Count -eq 0).ToString().ToLowerInvariant()
            }
            else {
                $gitStatusClean = 'UNKNOWN'
            }
        }
        else {
            Write-Host 'WARN: git command unavailable.'
        }
    }
    finally {
        Pop-Location
    }
}

$totalKb = [math]::Round(($totalBytes / 1KB), 2)
$totalMb = [math]::Round(($totalBytes / 1MB), 2)

$headers = @(
    'date',
    'timestamp',
    'mode',
    'repo_root',
    'branch',
    'git_status_clean',
    'total_files',
    'total_folders',
    'total_bytes',
    'total_kb',
    'total_mb',
    'progress_percent',
    'notes'
)

$values = @(
    $date,
    $timestamp,
    $Mode,
    $RepoRoot,
    $branch,
    $gitStatusClean,
    $totalFiles,
    $totalFolders,
    $totalBytes,
    $totalKb,
    $totalMb,
    $ProgressPercent,
    $Notes
)

Write-Host 'Proposed DAILY_METRICS-compatible CSV columns:'
Write-Host ($headers -join ',')
Write-Host 'Proposed CSV row:'
Write-Host (($values | ForEach-Object { Convert-ToCsvField -Value $_ }) -join ',')
Write-Host ''
Write-Host ('DRY_RUN COMPLETE {0} NO DAILY METRICS CSV UPDATED.' -f [char]0x2014)
