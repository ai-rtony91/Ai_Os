param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$taskName = 'AI_OS Stage 9C Repo Health Verification Chain'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
$warnings = New-Object System.Collections.Generic.List[string]
$failures = New-Object System.Collections.Generic.List[string]

function Write-Section {
    param([string]$Title)
    Write-Host ''
    Write-Host "== $Title =="
}

function Test-ExpectedPath {
    param(
        [string]$Label,
        [string]$Path,
        [string]$Kind
    )

    $exists = $false
    if ($Kind -eq 'Directory') {
        $exists = Test-Path -LiteralPath $Path -PathType Container
    }
    else {
        $exists = Test-Path -LiteralPath $Path -PathType Leaf
    }

    if ($exists) {
        Write-Host "[PASS] $Label"
    }
    else {
        Write-Host "[FAIL] $Label"
        $script:failures.Add("Missing $Kind`: $Path") | Out-Null
    }
}

Write-Host 'Task name: AI_OS Stage 9C Repo Health Verification Chain'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host "Current timestamp: $timestamp"
Write-Host ''
Write-Host 'Safety: DRY_RUN only. This script is read-only and does not create, edit, move, rename, delete, stage, commit, or push files.'

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host ''
    Write-Host 'Final summary: FAIL'
    Write-Host "Reason: Repo path does not exist: $RepoRoot"
    exit 1
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
Set-Location -LiteralPath $resolvedRepoRoot

Write-Section 'Git Status'
$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Host '[FAIL] git command unavailable.'
    $failures.Add('git command unavailable.') | Out-Null
}
else {
    try {
        $gitStatus = & git status --short --branch 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host '[FAIL] git status failed.'
            $gitStatus | ForEach-Object { Write-Host $_ }
            $failures.Add('git status failed.') | Out-Null
        }
        else {
            $gitStatus | ForEach-Object { Write-Host $_ }
            if ($gitStatus.Count -gt 1) {
                Write-Host '[WARN] Working tree has listed changes. Review them before APPLY work.'
                $warnings.Add('Working tree has listed changes.') | Out-Null
            }
            else {
                Write-Host '[PASS] Working tree has no listed changes.'
            }
        }
    }
    catch {
        Write-Host '[FAIL] git status could not be completed.'
        Write-Host $_.Exception.Message
        $failures.Add('git status could not be completed.') | Out-Null
    }
}

Write-Section 'Top-Level Folder Presence Check'
$topLevelFolders = @(
    'agent',
    'apps',
    'automation',
    'docs',
    'inputs',
    'internal',
    'Reports',
    'services'
)

foreach ($folder in $topLevelFolders) {
    Test-ExpectedPath -Label $folder -Path (Join-Path $resolvedRepoRoot $folder) -Kind 'Directory'
}

Write-Section 'Protected Root File Presence Check'
$protectedRootFiles = @(
    'README.md',
    'AGENTS.md',
    'RISK_POLICY.md',
    'SOURCE_LOG.md',
    'ERROR_LOG.md',
    'HALLUCINATION_LOG.md',
    'AAR.md',
    'DAILY_REPORT.md',
    'WHITEPAPER.md'
)

foreach ($file in $protectedRootFiles) {
    Test-ExpectedPath -Label $file -Path (Join-Path $resolvedRepoRoot $file) -Kind 'File'
}

Write-Section 'Reports Folder Presence Check'
$reportsFolders = @(
    'Reports',
    'Reports\daily',
    'Reports\checkpoints',
    'Reports\health'
)

foreach ($folder in $reportsFolders) {
    Test-ExpectedPath -Label $folder -Path (Join-Path $resolvedRepoRoot $folder) -Kind 'Directory'
}

Write-Section 'Stage 8 Helper Script Presence Check'
$stage8Helpers = @(
    'automation\reporting\Test-AiOsRepoCleanStatus.DRY_RUN.ps1',
    'automation\reporting\Test-AiOsFolderPurposeCoverage.DRY_RUN.ps1',
    'automation\reporting\Test-AiOsFinalCleanStop.DRY_RUN.ps1',
    'automation\reporting\New-AiOsReport.ps1'
)

foreach ($file in $stage8Helpers) {
    Test-ExpectedPath -Label $file -Path (Join-Path $resolvedRepoRoot $file) -Kind 'File'
}

Write-Section 'Unsafe Action Warning List'
$unsafeActions = @(
    'No git add was attempted.',
    'No git commit was attempted.',
    'No git push was attempted.',
    'No delete, move, rename, or overwrite action was attempted.',
    'No broker, trading execution, credential, secret, registry, firewall, VPN, BIOS/UEFI, BitLocker, Task Scheduler, startup setting, app launch, or browser launch action was attempted.'
)

foreach ($item in $unsafeActions) {
    Write-Host "[PASS] $item"
}

Write-Section 'Final PASS/WARN/FAIL Summary'
if ($failures.Count -gt 0) {
    Write-Host 'Final summary: FAIL'
    Write-Host 'Failures:'
    $failures | ForEach-Object { Write-Host "- $_" }
    if ($warnings.Count -gt 0) {
        Write-Host 'Warnings:'
        $warnings | ForEach-Object { Write-Host "- $_" }
    }
    exit 1
}

if ($warnings.Count -gt 0) {
    Write-Host 'Final summary: WARN'
    Write-Host 'Warnings:'
    $warnings | ForEach-Object { Write-Host "- $_" }
    exit 0
}

Write-Host 'Final summary: PASS'
exit 0
