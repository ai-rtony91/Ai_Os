[CmdletBinding()]
param(
    [string]$SessionId = "",
    [string]$DateKey = "",
    [string]$OperatorStartTime = "",
    [string]$OperatorStopTime = "",
    [string]$ActivePacketId = "UNKNOWN",
    [string]$WorkerLane = "UNKNOWN",
    [string]$TaskLabel = "UNKNOWN",
    [string]$ValidatorStartedAt = "",
    [string]$ValidatorFinishedAt = "",
    [string]$OutputSummary = "DRY_RUN timer entry preview only.",
    [AllowEmptyString()][string]$BlockedReason = "",
    [string]$EvidenceReadyForCollect = "false"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function ConvertTo-AiOsUtcString {
    param([AllowEmptyString()][string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $null
    }

    return ([datetime]::Parse($Value).ToUniversalTime()).ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Get-AiOsElapsedMinutes {
    param(
        [AllowNull()][string]$Start,
        [AllowNull()][string]$Stop
    )

    if ([string]::IsNullOrWhiteSpace($Start) -or [string]::IsNullOrWhiteSpace($Stop)) {
        return $null
    }

    $startTime = [datetime]::Parse($Start).ToUniversalTime()
    $stopTime = [datetime]::Parse($Stop).ToUniversalTime()
    return [Math]::Round(($stopTime - $startTime).TotalMinutes, 2)
}

function Get-AiOsElapsedSeconds {
    param(
        [AllowNull()][string]$Start,
        [AllowNull()][string]$Stop
    )

    if ([string]::IsNullOrWhiteSpace($Start) -or [string]::IsNullOrWhiteSpace($Stop)) {
        return $null
    }

    $startTime = [datetime]::Parse($Start).ToUniversalTime()
    $stopTime = [datetime]::Parse($Stop).ToUniversalTime()
    return [Math]::Round(($stopTime - $startTime).TotalSeconds, 2)
}

function ConvertTo-AiOsBoolean {
    param([AllowEmptyString()][string]$Value)

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return $false
    }

    return $Value.Trim().ToLowerInvariant() -in @("true", "1", "yes", "y")
}

$nowUtc = (Get-Date).ToUniversalTime()
if ([string]::IsNullOrWhiteSpace($DateKey)) {
    $DateKey = $nowUtc.ToString("yyyy-MM-dd")
}

if ([string]::IsNullOrWhiteSpace($SessionId)) {
    $SessionId = "AIOS-$DateKey-DRYRUN-PREVIEW"
}

$entry = [ordered]@{
    session_id = $SessionId
    date_key = $DateKey
    operator_start_time = ConvertTo-AiOsUtcString -Value $OperatorStartTime
    operator_stop_time = ConvertTo-AiOsUtcString -Value $OperatorStopTime
    elapsed_minutes = Get-AiOsElapsedMinutes -Start $OperatorStartTime -Stop $OperatorStopTime
    active_packet_id = $ActivePacketId
    worker_lane = $WorkerLane
    task_label = $TaskLabel
    validator_started_at = ConvertTo-AiOsUtcString -Value $ValidatorStartedAt
    validator_finished_at = ConvertTo-AiOsUtcString -Value $ValidatorFinishedAt
    validator_elapsed_seconds = Get-AiOsElapsedSeconds -Start $ValidatorStartedAt -Stop $ValidatorFinishedAt
    output_summary = $OutputSummary
    blocked_reason = if ([string]::IsNullOrWhiteSpace($BlockedReason)) { $null } else { $BlockedReason }
    evidence_ready_for_collect = ConvertTo-AiOsBoolean -Value $EvidenceReadyForCollect
}

[ordered]@{
    schema = "AIOS_PRODUCTIVITY_TIMER_ENTRY_PREVIEW.v1"
    mode = "DRY_RUN"
    writes_performed = 0
    ledger_append_performed = "NO"
    collect_enabled = "NO"
    entry = $entry
    blocked_actions = @(
        "file_write",
        "ledger_append",
        "scheduler_change",
        "runtime_launch",
        "worker_launch",
        "packet_movement",
        "approval_mutation",
        "backup_execution",
        "git_stage_commit_or_push"
    )
    next_safe_action = "Review the previewed timer entry before approving a separate APPLY packet for ledger persistence."
} | ConvertTo-Json -Depth 8
