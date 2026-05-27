[CmdletBinding()]
param([switch]$OutputJson)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$events = @(
    [pscustomobject]@{ event = "daily_startup"; cadence = "manual_or_daily"; allowed = "preview_status"; blocked = "startup persistence" },
    [pscustomobject]@{ event = "night_shift"; cadence = "operator_requested"; allowed = "read_only_brief"; blocked = "scheduled task writes" },
    [pscustomobject]@{ event = "queue_scan"; cadence = "manual_or_hourly_preview"; allowed = "read_queue"; blocked = "queue mutation" },
    [pscustomobject]@{ event = "stale_lock_scan"; cadence = "manual_or_hourly_preview"; allowed = "read_locks"; blocked = "lock release" },
    [pscustomobject]@{ event = "pr_watcher"; cadence = "manual_or_hourly_preview"; allowed = "read_pr_checks"; blocked = "merge" },
    [pscustomobject]@{ event = "telemetry_snapshot"; cadence = "manual_preview"; allowed = "read_telemetry"; blocked = "telemetry mutation" },
    [pscustomobject]@{ event = "recovery_bootstrap"; cadence = "manual_preview"; allowed = "report_recovery"; blocked = "auto_repair" },
    [pscustomobject]@{ event = "validator_sweep"; cadence = "manual_preview"; allowed = "recommend_validators"; blocked = "auto_repair" }
)

$preview = [pscustomobject]@{
    schema = "AIOS_SCHEDULER_PREVIEW.v1"
    mode = "DRY_RUN"
    execution_enabled = $false
    persistence_enabled = $false
    task_scheduler_writes = $false
    tasker_integration_enabled = $false
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    preview_events = $events
    blocked_actions = @(
        "execution",
        "persistence",
        "installs",
        "Task Scheduler writes",
        "Tasker integration",
        "queue mutation",
        "approval mutation",
        "worker launch",
        "commit",
        "push",
        "merge",
        "secrets",
        "cloud provisioning",
        "broker/OANDA/trading/webhook/live orders"
    )
    next_safe_action = "Review scheduler preview. A separate approved packet is required before any scheduler persistence."
}

if ($OutputJson) {
    $preview | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "AI_OS Scheduler Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($preview.schema)"
Write-Host "Execution enabled: $($preview.execution_enabled)"
Write-Host "Persistence enabled: $($preview.persistence_enabled)"
Write-Host "Events:"
foreach ($item in $events) {
    Write-Host ("- {0}: allowed={1}; blocked={2}" -f $item.event, $item.allowed, $item.blocked)
}
Write-Host "Next safe action: $($preview.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
