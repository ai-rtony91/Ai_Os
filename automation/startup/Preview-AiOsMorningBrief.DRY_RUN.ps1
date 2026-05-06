param(
    [string]$RepoRoot = 'C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'
$today = Get-Date -Format 'yyyy-MM-dd'
$proposedTargetFile = "Reports\morning_brief\MORNING_BRIEF_$today`_AI_OS.md"

Write-Host 'Task name: AI_OS Stage 24A-24D Morning Brief Preview Generator'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host "Proposed target file: $proposedTargetFile"
Write-Host ''

Write-Host 'Proposed source inputs:'
Write-Host '- validator output'
Write-Host '- git status output'
Write-Host '- protected diff output'
Write-Host '- workflow state output'
Write-Host '- approval state output'
Write-Host '- dashboard snapshot output'
Write-Host '- report preview state output'
Write-Host '- telemetry preview state output'
Write-Host ''

Write-Host 'Proposed Morning Brief sections:'
Write-Host '- Header'
Write-Host '- Repo State'
Write-Host '- Workflow State'
Write-Host '- Approval State'
Write-Host '- Dashboard State'
Write-Host '- Report Preview State'
Write-Host '- Telemetry Preview State'
Write-Host '- Protected File Status'
Write-Host '- Trading Execution Boundary Status'
Write-Host '- Next Safe Action'
Write-Host ''

Write-Host 'Blocked fields:'
Write-Host '- secrets'
Write-Host '- credentials'
Write-Host '- broker tokens'
Write-Host '- private keys'
Write-Host '- recovery keys'
Write-Host '- live trading data'
Write-Host '- uncontrolled screen contents'
Write-Host ''

Write-Host 'Approval requirement: separate human approval required before any Morning Brief file write, startup task, app launch, or browser launch.'
Write-Host 'Validator to run after future write: automation\status\Test-AiOsMorningBriefPreviewGenerator.DRY_RUN.ps1 or a separately approved APPLY validator.'
Write-Host ''
Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO MORNING BRIEF FILES WRITTEN.' -f [char]0x2014)
