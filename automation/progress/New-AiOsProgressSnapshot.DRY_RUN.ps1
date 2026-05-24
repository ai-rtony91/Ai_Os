param(
    [string]$Stage = "UNKNOWN",
    [string]$TaskId = "UNKNOWN",
    [string]$TaskName = "UNKNOWN",
    [int]$PlannedSteps = 0,
    [int]$CompletedSteps = 0,
    [string]$Status = "UNKNOWN",
    [string]$Blocked = "NO",
    [string]$Blocker = "",
    [string]$NextAction = "UNKNOWN",
    [string]$CheckpointFile = "UNKNOWN",
    [string]$CommitHash = "UNKNOWN",
    [string]$GitStatus = "UNKNOWN",
    [string]$Notes = "DRY_RUN preview only"
)

$ErrorActionPreference = "Stop"




if ($PlannedSteps -gt 0) {
    $PercentComplete = [math]::Round(($CompletedSteps / $PlannedSteps) * 100)
} else {
    $PercentComplete = "UNKNOWN"
}

$Now = Get-Date
$Snapshot = [PSCustomObject]@{
    date = $Now.ToString("yyyy-MM-dd")
    time = $Now.ToString("HH:mm:ss")
    stage = $Stage
    task_id = $TaskId
    task_name = $TaskName
    planned_steps = $PlannedSteps
    completed_steps = $CompletedSteps
    percent_complete = $PercentComplete
    status = $Status
    blocked = $Blocked
    blocker = $Blocker
    next_action = $NextAction
    checkpoint_file = $CheckpointFile
    commit_hash = $CommitHash
    git_status = $GitStatus
    notes = $Notes
}

Write-Host "AI_OS Progress Snapshot DRY_RUN"
$Snapshot | ConvertTo-Csv -NoTypeInformation
Write-Host "Result: PREVIEW_ONLY"
exit 0
