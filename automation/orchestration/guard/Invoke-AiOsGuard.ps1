param(
    [string]$ExpectedPath = "",
    [string]$ExpectedBranch = "",
    [string]$ExpectedLaneId = "",
    [ValidateSet("codex", "git_status", "git_save", "launch", "validate", "merge", "packet_update")]
    [string]$CommandType = "validate",
    [switch]$AllowMain,
    [switch]$RequireApply,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Normalize-AiOsPath {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    return [System.IO.Path]::GetFullPath($Path).TrimEnd("\", "/")
}

function Add-AiOsGuardLine {
    param(
        [System.Collections.Generic.List[object]]$Results,
        [string]$Level,
        [string]$Message
    )

    $Results.Add([pscustomobject]@{
        Level = $Level
        Message = $Message
    }) | Out-Null
}

$scriptName = Split-Path -Leaf $PSCommandPath
$results = [System.Collections.Generic.List[object]]::new()
$currentPath = (Get-Location).Path
$normalizedCurrentPath = Normalize-AiOsPath -Path $currentPath
$normalizedExpectedPath = Normalize-AiOsPath -Path $ExpectedPath
$currentBranch = ""

try {
    $currentBranch = (git branch --show-current 2>$null)
    if ($null -eq $currentBranch) {
        $currentBranch = ""
    }
    $currentBranch = $currentBranch.Trim()
}
catch {
    $currentBranch = ""
    Add-AiOsGuardLine -Results $results -Level "WARN" -Message "Git branch could not be read from this path."
}

if (-not [string]::IsNullOrWhiteSpace($ExpectedPath)) {
    if (-not [string]::Equals($normalizedCurrentPath, $normalizedExpectedPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        Add-AiOsGuardLine -Results $results -Level "FAIL" -Message "Current path does not match ExpectedPath."
    }
}

if (-not [string]::IsNullOrWhiteSpace($ExpectedBranch)) {
    if (-not [string]::Equals($currentBranch, $ExpectedBranch, [System.StringComparison]::OrdinalIgnoreCase)) {
        Add-AiOsGuardLine -Results $results -Level "FAIL" -Message "Current branch does not match ExpectedBranch."
    }
}

if ($currentBranch -eq "main" -and @("git_save", "merge") -contains $CommandType -and -not $AllowMain) {
    Add-AiOsGuardLine -Results $results -Level "FAIL" -Message "git_save and merge are blocked on main unless -AllowMain is supplied."
}

if ($CommandType -eq "codex" -and $ExpectedLaneId -eq "main_control") {
    Add-AiOsGuardLine -Results $results -Level "FAIL" -Message "Codex worker commands are blocked from CONTROL/main_control."
}

if ($RequireApply -and -not $Apply) {
    Add-AiOsGuardLine -Results $results -Level "FAIL" -Message "This command type requires -Apply, but -Apply was not supplied."
}

if ($CommandType -eq "validate") {
    $stagedFiles = @(git diff --cached --name-only 2>$null)
    if ($stagedFiles.Count -gt 0) {
        Add-AiOsGuardLine -Results $results -Level "WARN" -Message "Staged files exist during validate."
    }
}

$protectedRootFiles = @(
    "README.md",
    "ERROR_LOG.md",
    "package.json",
    "package-lock.json",
    ".gitignore"
)

$protectedChanged = @()
foreach ($protectedFile in $protectedRootFiles) {
    $statusLine = @(git status --porcelain -- $protectedFile 2>$null)
    if ($statusLine.Count -gt 0) {
        $protectedChanged += $protectedFile
    }
}

if ($protectedChanged.Count -gt 0) {
    Add-AiOsGuardLine -Results $results -Level "WARN" -Message ("Protected root file changes require explicit approval: " + ($protectedChanged -join ", "))
}

$failCount = @($results | Where-Object { $_.Level -eq "FAIL" }).Count
$warnCount = @($results | Where-Object { $_.Level -eq "WARN" }).Count
$overall = "PASS"
if ($failCount -gt 0) {
    $overall = "FAIL"
}

Write-Host ("COPY START - " + $scriptName)
Write-Host "AI_OS Guard Safety Wrapper"
Write-Host "Mode: PREVIEW / CHECK ONLY"
Write-Host "Mutation performed: NO"
Write-Host "Target command executed: NO"
Write-Host ""
Write-Host "Current path: $currentPath"
Write-Host "Current branch: $currentBranch"
Write-Host "Expected path: $ExpectedPath"
Write-Host "Expected branch: $ExpectedBranch"
Write-Host "Expected lane_id: $ExpectedLaneId"
Write-Host "CommandType: $CommandType"
Write-Host "AllowMain: $($AllowMain.IsPresent)"
Write-Host "RequireApply: $($RequireApply.IsPresent)"
Write-Host "Apply supplied: $($Apply.IsPresent)"
Write-Host ""
Write-Host "== Guard Results =="
if ($results.Count -eq 0) {
    Write-Host "PASS: expectations satisfied."
}
else {
    $results | ForEach-Object {
        Write-Host "$($_.Level): $($_.Message)"
    }
}
Write-Host ""
Write-Host "Overall: $overall"
Write-Host "Warnings: $warnCount"
Write-Host "Failures: $failCount"
Write-Host ""
Write-Host "WHERE TO RUN NEXT"
if ($overall -eq "PASS") {
    Write-Host "WHERE: visible tab/window for the intended lane"
    Write-Host "Path: $currentPath"
    Write-Host "Next: run the guarded command only after confirming the path, branch, lane, and Apply requirement above."
}
else {
    Write-Host "WHERE: CONTROL or SAVE tab"
    Write-Host "Path: expected repo root or expected lane path"
    Write-Host "Next: stop and fix the failed path, branch, lane, or Apply mismatch before running the target command."
}
Write-Host ""
Write-Host "Files staged: NO"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host ("COPY END - " + $scriptName)

if ($overall -eq "FAIL") {
    exit 1
}

exit 0
