[CmdletBinding()]
param(
    [string]$TaskId = "CREW-TASK-PREVIEW",
    [string]$Title = "Crew task preview",
    [string]$Purpose = "Preview an AI_OS Crew task intake record.",
    [string]$Owner = "Human Owner",
    [string[]]$AllowedPaths = @(),
    [string[]]$BlockedPaths = @(),
    [string]$StopPoint = "DRY_RUN_REPORT_ONLY"
)

$ErrorActionPreference = "Stop"

[pscustomobject]@{
    schema = "AIOS_CREW_TASK_INTAKE.v1"
    mode = "DRY_RUN_READ_ONLY"
    task_id = $TaskId
    title = $Title
    purpose = $Purpose
    owner = $Owner
    status = "PROPOSED"
    priority = "normal"
    allowed_paths = $AllowedPaths
    blocked_paths = $BlockedPaths
    stop_point = $StopPoint
    modifies_files = $false
    commits = $false
    pushes = $false
    next_safe_action = "Review this task intake preview before creating a work packet."
} | ConvertTo-Json -Depth 8
