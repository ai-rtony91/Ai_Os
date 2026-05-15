Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$statePath = Join-Path $orchestrationRoot "orchestration_control_state.v1.example.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Required file was not found: $Path"
    }

    Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Write-List {
    param([object[]]$Items)

    if ($Items.Count -eq 0) {
        Write-Host "    - None"
        return
    }

    foreach ($item in $Items) {
        Write-Host "    - $item"
    }
}

$state = Read-JsonFile -Path $statePath
$heartbeats = @($state.worker_heartbeats)
$validators = @($state.validator_routing)
$prWorkflow = @($state.pr_workflow)
$queue = $state.queue_health
$telemetry = $state.telemetry

Write-Host "AI_OS Orchestration Control State Display"
Write-Host "Mode: $($state.mode)"
Write-Host "Control state: $($state.control_state_name)"
Write-Host "Purpose: $($state.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No workers, validators, scheduled tasks, startup tasks, commits, or pushes are launched."
Write-Host ""

$staleWorkers = @($heartbeats | Where-Object { $_.health_state -match "stale" })
$inactiveWorkers = @($heartbeats | Where-Object { $_.health_state -match "inactive" })
$blockedValidators = @($validators | Where-Object { $_.status -eq "blocked" })
$requiredValidators = @($validators | Where-Object { $_.required -eq $true })
$prRequired = @($prWorkflow | Where-Object { $_.pr_required -eq $true })
$approvalNeeded = @($prWorkflow | Where-Object { $_.approval_needed -eq $true })
$mergeRequired = @($prWorkflow | Where-Object { $_.merge_required -eq $true })

Write-Host "Worker heartbeat summary:"
Write-Host "  Total workers: $($heartbeats.Count)"
Write-Host "  Stale workers: $($staleWorkers.Count)"
Write-Host "  Inactive workers: $($inactiveWorkers.Count)"
Write-Host ""

foreach ($worker in $heartbeats) {
    $lastHeartbeat = if ([string]::IsNullOrWhiteSpace([string]$worker.last_heartbeat)) { "none" } else { $worker.last_heartbeat }
    $assignedPacket = if ([string]::IsNullOrWhiteSpace([string]$worker.assigned_packet_id)) { "none" } else { $worker.assigned_packet_id }

    Write-Host "  Worker: $($worker.worker_id)"
    Write-Host "    Health state: $($worker.health_state)"
    Write-Host "    Last heartbeat: $lastHeartbeat"
    Write-Host "    Stale after minutes: $($worker.stale_after_minutes)"
    Write-Host "    Assigned packet: $assignedPacket"
    Write-Host "    Notes: $($worker.notes)"
}
Write-Host ""

Write-Host "Queue health:"
Write-Host "  Packet total: $($queue.packet_total)"
Write-Host "  Available packets: $($queue.available_packets)"
Write-Host "  Assigned packets: $($queue.assigned_packets)"
Write-Host "  Blocked packets: $($queue.blocked_packets)"
Write-Host "  Stale packets: $($queue.stale_packets)"
Write-Host "  Validator-required packets: $($queue.validator_required_packets)"
Write-Host "  Approval-required packets: $($queue.approval_required_packets)"
Write-Host "  Queue pressure: $($queue.queue_pressure)"
Write-Host ""

Write-Host "Validator routing preparation:"
Write-Host "  Total validator routes: $($validators.Count)"
Write-Host "  Required validator routes: $($requiredValidators.Count)"
Write-Host "  Blocked validator routes: $($blockedValidators.Count)"
foreach ($validator in $validators) {
    Write-Host "  Validator: $($validator.validator_id)"
    Write-Host "    Category: $($validator.category)"
    Write-Host "    Assigned packet: $($validator.assigned_packet_id)"
    Write-Host "    Required: $($validator.required)"
    Write-Host "    Status: $($validator.status)"
}
Write-Host ""

Write-Host "Telemetry expansion:"
Write-Host "  Worker count: $($telemetry.worker_count)"
Write-Host "  Stale workers: $($telemetry.stale_workers)"
Write-Host "  Inactive workers: $($telemetry.inactive_workers)"
Write-Host "  Stale packets: $($telemetry.stale_packets)"
Write-Host "  Queue pressure: $($telemetry.queue_pressure)"
Write-Host "  Blocked assignments: $($telemetry.blocked_assignments)"
Write-Host "  Validation backlog: $($telemetry.validation_backlog)"
Write-Host ""

Write-Host "PR workflow integration:"
Write-Host "  PR-required packets: $($prRequired.Count)"
Write-Host "  Approval-needed states: $($approvalNeeded.Count)"
Write-Host "  Merge-required states: $($mergeRequired.Count)"
foreach ($packet in $prWorkflow) {
    Write-Host "  Packet: $($packet.packet_id)"
    Write-Host "    PR required: $($packet.pr_required)"
    Write-Host "    Approval needed: $($packet.approval_needed)"
    Write-Host "    Merge required: $($packet.merge_required)"
    Write-Host "    Status: $($packet.status)"
}
Write-Host ""

Write-Host "Blocked actions:"
Write-List -Items @($state.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review control state only; use a separate approved workflow before launching, validating, committing, pushing, or changing state."
