param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN',
    [string]$CurrentStage = 'STAGE9D_CHECKPOINT_DRAFT',
    [string]$CompletedItems = 'Session evidence and checkpoint helper draft proposed.',
    [string]$ChangedFilesPlaceholder = 'REVIEW_GIT_STATUS_OUTPUT',
    [string]$Risks = 'Existing uncommitted work must be reviewed before any git checkpoint.',
    [string]$NextAction = 'Review this console draft and approve any later APPLY report writing separately.',
    [string]$ApprovalStatus = 'DRY_RUN_ONLY_NO_WRITE_APPROVED'
)

$ErrorActionPreference = 'Stop'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'

Write-Host 'Task name: AI_OS Stage 9D Checkpoint Draft'
Write-Host 'Mode: DRY_RUN'
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, or launched.'
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Write-Host "checkpoint timestamp: $timestamp"
    Write-Host "repo root: $RepoRoot"
    Write-Host 'git status --short --branch: NOT RUN - repo root missing'
    Write-Host "current stage: $CurrentStage"
    Write-Host 'risks: Repo root missing. Human review required.'
    Write-Host 'approval status: DRY_RUN_ONLY_NO_WRITE_APPROVED'
    Write-Host ''
    Write-Host ('DRY_RUN COMPLETE {0} NO CHECKPOINT FILE WRITTEN.' -f [char]0x2014)
    exit 1
}

Push-Location -LiteralPath $RepoRoot
try {
    $gitStatus = @()
    $gitCommand = Get-Command git -ErrorAction SilentlyContinue
    if ($gitCommand) {
        $gitStatus = @(& git status --short --branch 2>&1)
        if ($LASTEXITCODE -ne 0) {
            $gitStatus = @('WARN - git status command failed.')
        }
    }
    else {
        $gitStatus = @('WARN - git command unavailable.')
    }
}
finally {
    Pop-Location
}

Write-Host 'Proposed checkpoint draft:'
Write-Host "checkpoint timestamp: $timestamp"
Write-Host "repo root: $RepoRoot"
Write-Host 'git status --short --branch:'
$gitStatus | ForEach-Object { Write-Host "  $_" }
Write-Host "current stage: $CurrentStage"
Write-Host "completed items: $CompletedItems"
Write-Host "changed files placeholder: $ChangedFilesPlaceholder"
Write-Host "risks: $Risks"
Write-Host "next action: $NextAction"
Write-Host "approval status: $ApprovalStatus"
Write-Host ''
Write-Host ('DRY_RUN COMPLETE {0} NO CHECKPOINT FILE WRITTEN.' -f [char]0x2014)
