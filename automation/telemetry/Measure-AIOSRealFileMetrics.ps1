$ErrorActionPreference = "Stop"

function Invoke-GitStatusShort {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $output = & git status --short 2>$null
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    if ($exitCode -ne 0) {
        return @()
    }

    return @($output)
}

function Get-RepoRoot {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $root = & git rev-parse --show-toplevel 2>$null
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference

    if ($exitCode -ne 0 -or [string]::IsNullOrWhiteSpace([string]$root)) {
        return (Resolve-Path ".").Path
    }

    return ([string]$root).Trim()
}

function Count-FilesUnderPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return 0
    }

    return @(
        Get-ChildItem -LiteralPath $Path -File -Recurse -ErrorAction SilentlyContinue
    ).Count
}

function Count-FilesModifiedTodayUnderPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [datetime]$TodayStart
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return 0
    }

    return @(
        Get-ChildItem -LiteralPath $Path -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -ge $TodayStart }
    ).Count
}

function Count-FilesCreatedTodayUnderPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [datetime]$TodayStart
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        return 0
    }

    return @(
        Get-ChildItem -LiteralPath $Path -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.CreationTime -ge $TodayStart }
    ).Count
}

$repoRoot = Get-RepoRoot
Set-Location -LiteralPath $repoRoot

$docsAiOsPath = Join-Path $repoRoot "docs\AI_OS"
$todayStart = (Get-Date).Date
$gitStatusShort = Invoke-GitStatusShort

$totalFilesScanned = Count-FilesUnderPath -Path $docsAiOsPath
$filesModifiedToday = Count-FilesModifiedTodayUnderPath -Path $docsAiOsPath -TodayStart $todayStart
$filesCreatedToday = Count-FilesCreatedTodayUnderPath -Path $docsAiOsPath -TodayStart $todayStart
$gitChangedFiles = $gitStatusShort.Count
$untrackedFiles = @($gitStatusShort | Where-Object { $_ -match '^\?\?' }).Count
$modifiedTrackedFiles = @(
    $gitStatusShort | Where-Object {
        $_ -notmatch '^\?\?' -and $_ -match '^(M.|.M)'
    }
).Count

Write-Host "AI_OS real file metrics"
Write-Host "repo_root: $repoRoot"
Write-Host "docs_aios_path: $docsAiOsPath"
Write-Host "total_files_scanned: $totalFilesScanned"
Write-Host "files_modified_today: $filesModifiedToday"
Write-Host "git_changed_files: $gitChangedFiles"
Write-Host "untracked_files: $untrackedFiles"
Write-Host "modified_tracked_files: $modifiedTrackedFiles"

if ($filesCreatedToday -gt 500 -or $filesModifiedToday -gt 500) {
    Write-Host "WARNING: unusually high file count detected. This count may be mislabeled or may include generated artifacts."
}
