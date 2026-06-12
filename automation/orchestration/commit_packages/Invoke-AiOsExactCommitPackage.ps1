[CmdletBinding()]
param(
    [string[]]$Files = @(),
    [string]$Message = "",
    [switch]$AllowOtherDirtyFiles,
    [switch]$Help
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Show-Help {
    Write-Output "AI_OS exact-file commit helper"
    Write-Output ""
    Write-Output "Usage:"
    Write-Output '  powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/commit_packages/Invoke-AiOsExactCommitPackage.ps1 -Files @("path/to/file1","path/to/file2") -Message "commit message"'
    Write-Output ""
    Write-Output "Safety:"
    Write-Output "  - stages only exact paths passed with -Files"
    Write-Output "  - refuses git add . and wildcard/pathspec staging"
    Write-Output "  - fails closed on dirty files outside -Files unless -AllowOtherDirtyFiles is set"
    Write-Output "  - runs git diff --check before staging"
    Write-Output "  - runs git diff --cached --check before commit"
    Write-Output "  - stops after one local commit; no push, PR, or merge"
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments,
        [switch]$AllowFailure
    )

    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    $lines = @($output | ForEach-Object { [string]$_ })

    if ($exitCode -ne 0 -and -not $AllowFailure) {
        throw ("git {0} failed with exit code {1}:{2}{3}" -f ($Arguments -join " "), $exitCode, [Environment]::NewLine, ($lines -join [Environment]::NewLine))
    }

    [pscustomobject]@{
        ExitCode = $exitCode
        Lines = $lines
    }
}

function ConvertTo-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    $repoPath = $Path.Replace("\", "/").Trim()
    while ($repoPath.StartsWith("./")) {
        $repoPath = $repoPath.Substring(2)
    }
    return $repoPath.TrimEnd("/")
}

function Test-UnsafePathSpec {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return "empty path"
    }

    $trimmed = $Path.Trim()
    if ($trimmed -in @(".", "./", "*", ":", ":/")) {
        return "broad staging path"
    }

    if ($trimmed -match "[\*\?\[\]]") {
        return "wildcard pathspec"
    }

    if ($trimmed.StartsWith(":(")) {
        return "git magic pathspec"
    }

    return ""
}

function ConvertFrom-GitStatusLine {
    param([Parameter(Mandatory = $true)][string]$Line)

    if ([string]::IsNullOrWhiteSpace($Line) -or $Line.Length -lt 4 -or $Line.StartsWith("##")) {
        return $null
    }

    $status = $Line.Substring(0, 2)
    $pathText = $Line.Substring(3).Trim()
    $paths = @()
    if ($pathText -match " -> ") {
        $parts = @($pathText -split " -> ")
        $paths += ConvertTo-RepoPath -Path $parts[0]
        $paths += ConvertTo-RepoPath -Path $parts[-1]
    }
    else {
        $paths += ConvertTo-RepoPath -Path $pathText
    }

    [pscustomobject]@{
        Status = $status
        RawPath = $pathText
        Paths = @($paths | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
    }
}

function Get-StatusEntries {
    $result = Invoke-Git -Arguments @("status", "--short", "--porcelain=v1", "--untracked-files=all")
    @($result.Lines | ForEach-Object { ConvertFrom-GitStatusLine -Line $_ } | Where-Object { $null -ne $_ })
}

if ($Help) {
    Show-Help
    exit 0
}

if ($Files.Count -eq 0) {
    throw "No files were provided. Pass exact paths with -Files."
}

if ([string]::IsNullOrWhiteSpace($Message)) {
    throw "No commit message was provided. Pass -Message."
}

$repoRoot = (Invoke-Git -Arguments @("rev-parse", "--show-toplevel")).Lines[0].Trim()
Set-Location -LiteralPath $repoRoot

$normalizedFiles = @()
foreach ($file in $Files) {
    $unsafeReason = Test-UnsafePathSpec -Path $file
    if (-not [string]::IsNullOrWhiteSpace($unsafeReason)) {
        throw "Refusing unsafe file path '$file': $unsafeReason."
    }

    $repoPath = ConvertTo-RepoPath -Path $file
    if ([string]::IsNullOrWhiteSpace($repoPath)) {
        throw "Refusing empty normalized path from '$file'."
    }

    $normalizedFiles += $repoPath
}

$normalizedFiles = @($normalizedFiles | Sort-Object -Unique)
if ($normalizedFiles.Count -eq 0) {
    throw "No usable file paths remain after normalization."
}

Write-Output "AI_OS exact-file commit helper"
Write-Output "Repo root: $repoRoot"
Write-Output ""
Write-Output "Initial git status:"
Invoke-Git -Arguments @("status", "--short", "--branch") | ForEach-Object { $_.Lines } | ForEach-Object { Write-Output $_ }

$statusEntries = @(Get-StatusEntries)
$dirtyPaths = @($statusEntries | ForEach-Object { $_.Paths } | Sort-Object -Unique)

foreach ($path in $normalizedFiles) {
    $exists = Test-Path -LiteralPath (Join-Path $repoRoot $path)
    $seenInGit = $dirtyPaths -contains $path
    if (-not $exists -and -not $seenInGit) {
        throw "Provided file does not exist and is not reported as changed/deleted/renamed by Git: $path"
    }
    if (-not $seenInGit) {
        throw "Provided file has no pending Git change: $path"
    }
}

if (-not $AllowOtherDirtyFiles) {
    $outsideDirty = @($dirtyPaths | Where-Object { $normalizedFiles -notcontains $_ } | Sort-Object -Unique)
    if ($outsideDirty.Count -gt 0) {
        throw ("Dirty files outside the exact file list: {0}. Re-run only after cleanup, or pass -AllowOtherDirtyFiles after manual review." -f ($outsideDirty -join ", "))
    }
}

Write-Output ""
Write-Output "Running git diff --check..."
Invoke-Git -Arguments @("diff", "--check") | ForEach-Object { $_.Lines } | ForEach-Object { Write-Output $_ }

Write-Output ""
Write-Output "Staging exact files only:"
foreach ($path in $normalizedFiles) {
    Write-Output "  $path"
}
Invoke-Git -Arguments (@("add", "--") + $normalizedFiles) | Out-Null

$cachedNames = @((Invoke-Git -Arguments @("diff", "--cached", "--name-only")).Lines | ForEach-Object { ConvertTo-RepoPath -Path $_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Sort-Object -Unique)
if ($cachedNames.Count -eq 0) {
    throw "No files are staged after exact-file staging."
}

$unexpectedCached = @($cachedNames | Where-Object { $normalizedFiles -notcontains $_ } | Sort-Object -Unique)
if ($unexpectedCached.Count -gt 0) {
    throw ("Cached diff contains files outside the exact file list: {0}" -f ($unexpectedCached -join ", "))
}

Write-Output ""
Write-Output "Cached files:"
$cachedNames | ForEach-Object { Write-Output "  $_" }

Write-Output ""
Write-Output "Running git diff --cached --check..."
Invoke-Git -Arguments @("diff", "--cached", "--check") | ForEach-Object { $_.Lines } | ForEach-Object { Write-Output $_ }

Write-Output ""
Write-Output "Committing exact package..."
Invoke-Git -Arguments @("commit", "-m", $Message) | ForEach-Object { $_.Lines } | ForEach-Object { Write-Output $_ }

Write-Output ""
Write-Output "Final git status:"
Invoke-Git -Arguments @("status", "--short", "--branch") | ForEach-Object { $_.Lines } | ForEach-Object { Write-Output $_ }

Write-Output ""
Write-Output "Stopped after local commit. Push, PR, and merge were not performed."
