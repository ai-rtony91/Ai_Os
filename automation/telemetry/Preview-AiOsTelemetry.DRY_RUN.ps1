param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os'
)

$ErrorActionPreference = 'Stop'
$mode = 'DRY_RUN'

Write-Host 'Task name: AI_OS Stage 23A-23D Telemetry Preview Helper'
Write-Host "Mode: $mode"
Write-Host "Repo root: $RepoRoot"
Write-Host ''

Write-Host 'Proposed telemetry fields:'
Write-Host '- timestamp'
Write-Host '- workflow_name'
Write-Host '- workflow_state'
Write-Host '- dashboard_state'
Write-Host '- approval_state'
Write-Host '- morning_brief_state'
Write-Host '- report_boundary_state'
Write-Host '- snapshot_boundary_state'
Write-Host '- protected_files_changed'
Write-Host '- telemetry_mode'
Write-Host '- production_ready'
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

Write-Host 'Approval requirement: telemetry persistence requires separate approval.'
Write-Host 'Retention concept: future retention may define target path, rotation, retention days, archival boundary, protected-file checks, and deletion rules.'
Write-Host 'Validator to run after future write: automation\status\Test-AiOsTelemetryPreviewContract.DRY_RUN.ps1 or a separately approved APPLY validator.'
Write-Host ''
Write-Host 'PASS/WARN/FAIL summary: PASS'
Write-Host ('DRY_RUN COMPLETE {0} NO TELEMETRY FILES WRITTEN.' -f [char]0x2014)
