[CmdletBinding()]
param(
    [string]$LedgerPath = "telemetry/productivity/PRODUCTIVITY_TIMER_LEDGER.example.jsonl"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-AiOsJsonLine {
    param([Parameter(Mandatory = $true)][string]$Line)

    try {
        return $Line | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            parse_error = $_.Exception.Message
        }
    }
}

$entries = @()
$invalidLineCount = 0

if (Test-Path -LiteralPath $LedgerPath -PathType Leaf) {
    $lines = @(Get-Content -LiteralPath $LedgerPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    foreach ($line in $lines) {
        $item = Read-AiOsJsonLine -Line $line
        if ($item.PSObject.Properties.Name -contains "parse_error") {
            $invalidLineCount += 1
            continue
        }

        $entries += $item
    }
}

$totalElapsedMinutes = 0.0
$validatorElapsedSeconds = 0.0
$blockedCount = 0
$collectReadyCount = 0

foreach ($entry in $entries) {
    if ($null -ne $entry.elapsed_minutes) {
        $totalElapsedMinutes += [double]$entry.elapsed_minutes
    }

    if ($null -ne $entry.validator_elapsed_seconds) {
        $validatorElapsedSeconds += [double]$entry.validator_elapsed_seconds
    }

    if (-not [string]::IsNullOrWhiteSpace([string]$entry.blocked_reason)) {
        $blockedCount += 1
    }

    if ($entry.evidence_ready_for_collect -eq $true) {
        $collectReadyCount += 1
    }
}

[ordered]@{
    schema = "AIOS_PRODUCTIVITY_TIMER_SUMMARY.v1"
    mode = "DRY_RUN"
    ledger_path = $LedgerPath
    ledger_present = (Test-Path -LiteralPath $LedgerPath -PathType Leaf)
    entry_count = $entries.Count
    invalid_line_count = $invalidLineCount
    total_elapsed_minutes = [Math]::Round($totalElapsedMinutes, 2)
    total_validator_elapsed_seconds = [Math]::Round($validatorElapsedSeconds, 2)
    blocked_session_count = $blockedCount
    evidence_ready_for_collect_count = $collectReadyCount
    writes_performed = 0
    collect_enabled = "NO"
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
    next_safe_action = "Use this read-only summary as evidence before approving any persistence or collector integration."
} | ConvertTo-Json -Depth 8
