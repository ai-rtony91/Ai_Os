param(
    [string]$TaskId = "UNKNOWN",
    [string]$TaskName = "UNKNOWN",
    [int]$PlannedSteps = 0,
    [int]$CompletedSteps = 0,
    [string]$Status = "UNKNOWN",
    [string]$Blocker = "",
    [string]$CheckpointPath = "UNKNOWN",
    [string]$CommitHash = "UNKNOWN",
    [string]$GitStatus = "UNKNOWN"
)

$ErrorActionPreference = "Stop"

if ($PlannedSteps -gt 0) {
    $PercentComplete = [math]::Round(($CompletedSteps / $PlannedSteps) * 100)
} else {
    $PercentComplete = "UNKNOWN"
}

$Blocked = if ([string]::IsNullOrWhiteSpace($Blocker)) { "NO" } else { "YES" }
$Now = Get-Date

$Row = [PSCustomObject]@{
    date = $Now.ToString("yyyy-MM-dd")
    time = $Now.ToString("HH:mm:ss")
    stage = "SYSTEM_WIDE"
    task_id = $TaskId
    task_name = $TaskName
    planned_steps = $PlannedSteps
    completed_steps = $CompletedSteps
    percent_complete = $PercentComplete
    status = $Status
    blocked = $Blocked
    blocker = $Blocker
    next_action = "DRY_RUN preview only; approve APPLY before writing ledger rows"
    checkpoint_file = $CheckpointPath
    commit_hash = $CommitHash
    git_status = $GitStatus
    notes = "No ledger file was modified"
}

Write-Host "AI_OS Progress Ledger Update DRY_RUN"
$Row | ConvertTo-Csv -NoTypeInformation
Write-Host "Result: PREVIEW_ONLY"
exit 0
