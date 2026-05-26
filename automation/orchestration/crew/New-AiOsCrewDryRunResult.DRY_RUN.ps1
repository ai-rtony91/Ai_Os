[CmdletBinding()]
param(
    [string]$PacketId = "PACKET_ID_REQUIRED",
    [string]$Summary = "Crew DRY_RUN result preview.",
    [string[]]$FilesToCreate = @(),
    [string[]]$FilesToModify = @(),
    [string[]]$FilesToDelete = @(),
    [string]$RiskLevel = "normal",
    [string[]]$ValidatorNeeded = @(),
    [string[]]$ApplyCommandPreview = @(),
    [string]$StopPoint = "DRY_RUN_REPORT_ONLY"
)

$ErrorActionPreference = "Stop"

[pscustomobject]@{
    schema = "AIOS_CREW_DRY_RUN_RESULT.v1"
    mode = "DRY_RUN_READ_ONLY"
    packet_id = $PacketId
    summary = $Summary
    files_to_create = $FilesToCreate
    files_to_modify = $FilesToModify
    files_to_delete = $FilesToDelete
    risk_level = $RiskLevel
    validator_needed = $ValidatorNeeded
    apply_command_preview = $ApplyCommandPreview
    stop_point = $StopPoint
    modifies_files = $false
    commits = $false
    pushes = $false
    next_safe_action = "Submit this DRY_RUN result to the approval inbox only after human review."
} | ConvertTo-Json -Depth 8
