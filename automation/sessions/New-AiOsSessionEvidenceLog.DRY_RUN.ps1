param(
    [string]$RepoRoot = 'C:\Dev\Ai.Os',
    [string]$SessionType = 'AI_OS_WORK_SESSION',
    [string]$Stage = 'STAGE9D',
    [string]$Mode = 'DRY_RUN',
    [string]$Operator = 'human_approved',
    [string]$EvidenceType = 'PROPOSED_SESSION_EVIDENCE_INDEX',
    [string]$EvidenceLocation = 'NONE_WRITTEN',
    [string]$Notes = 'DRY_RUN proposed session evidence log row only.',
    [string]$ApprovalRequired = 'YES'
)

$ErrorActionPreference = 'Stop'
$timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'

Write-Host 'Task name: AI_OS Stage 9D Session Evidence Log Draft'
Write-Host 'Mode: DRY_RUN'
Write-Host 'Safety: Console-output only. No files are created, edited, moved, renamed, deleted, staged, committed, pushed, or launched.'
Write-Host ''
Write-Host 'Proposed session evidence log row:'
Write-Host "timestamp: $timestamp"
Write-Host "repo_root: $RepoRoot"
Write-Host "session_type: $SessionType"
Write-Host "stage: $Stage"
Write-Host "mode: $Mode"
Write-Host "operator: $Operator"
Write-Host "evidence_type: $EvidenceType"
Write-Host "evidence_location: $EvidenceLocation"
Write-Host "notes: $Notes"
Write-Host "approval_required: $ApprovalRequired"
Write-Host ''
Write-Host ('DRY_RUN COMPLETE {0} NO SESSION LOG WRITTEN.' -f [char]0x2014)
