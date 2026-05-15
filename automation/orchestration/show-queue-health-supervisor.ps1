Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$supervisorPath = Join-Path $orchestrationRoot "queue_health_supervisor.v1.example.json"

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

$supervisor = Read-JsonFile -Path $supervisorPath
$queue = $supervisor.queue_health
$stalePackets = @($supervisor.stale_packet_visibility)
$telemetry = $supervisor.telemetry

Write-Host "AI_OS Queue Health Supervisor Display"
Write-Host "Mode: $($supervisor.mode)"
Write-Host "Supervisor: $($supervisor.supervisor_name)"
Write-Host "Purpose: $($supervisor.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No queue records are modified. No ownership is released. No validators or workers are launched."
Write-Host ""

Write-Host "Queue health:"
Write-Host "  Packet total: $($queue.packet_total)"
Write-Host "  Available packets: $($queue.available_packets)"
Write-Host "  Assigned packets: $($queue.assigned_packets)"
Write-Host "  Blocked packets: $($queue.blocked_packets)"
Write-Host "  Inactive packets: $($queue.inactive_packets)"
Write-Host "  Stale packets: $($queue.stale_packets)"
Write-Host "  Approval-required packets: $($queue.approval_required_packets)"
Write-Host "  Validator-required packets: $($queue.validator_required_packets)"
Write-Host "  Approval backlog: $($queue.approval_backlog)"
Write-Host "  Validation backlog: $($queue.validation_backlog)"
Write-Host "  Queue pressure: $($queue.queue_pressure)"
Write-Host ""

Write-Host "Stale packet visibility:"
if ($stalePackets.Count -eq 0) {
    Write-Host "  None"
} else {
    foreach ($packet in $stalePackets) {
        $lastUpdated = if ([string]::IsNullOrWhiteSpace([string]$packet.last_updated)) { "none" } else { $packet.last_updated }

        Write-Host "  Packet: $($packet.packet_id)"
        Write-Host "    Name: $($packet.packet_name)"
        Write-Host "    State: $($packet.packet_state)"
        Write-Host "    Last updated: $lastUpdated"
        Write-Host "    Stale after minutes: $($packet.stale_after_minutes)"
        Write-Host "    Visibility state: $($packet.visibility_state)"
        Write-Host "    Blocked ownership: $($packet.blocked_ownership)"
        Write-Host "    Unresolved state: $($packet.unresolved_state)"
        Write-Host "    Notes: $($packet.notes)"
    }
}
Write-Host ""

Write-Host "Telemetry expansion:"
Write-Host "  Validator count: $($telemetry.validator_count)"
Write-Host "  Validator backlog: $($telemetry.validator_backlog)"
Write-Host "  Stale packet count: $($telemetry.stale_packet_count)"
Write-Host "  Inactive packet count: $($telemetry.inactive_packet_count)"
Write-Host "  Queue pressure: $($telemetry.queue_pressure)"
Write-Host "  Blocked states: $($telemetry.blocked_states)"
Write-Host "  Approval queue size: $($telemetry.approval_queue_size)"
Write-Host "  Validation backlog: $($telemetry.validation_backlog)"
Write-Host ""

Write-Host "Blocked actions:"
Write-List -Items @($supervisor.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review queue health only; use a separate approved workflow before changing queue state or running validators."
