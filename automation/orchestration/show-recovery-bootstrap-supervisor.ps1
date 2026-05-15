Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$supervisorPath = Join-Path $orchestrationRoot "recovery_bootstrap_supervisor.v1.example.json"

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
$queueRestore = $supervisor.queue_restore
$workerRestore = @($supervisor.worker_restore)
$packetRestore = @($supervisor.packet_restore)
$checkpoints = @($supervisor.recovery_checkpoints)
$telemetry = $supervisor.telemetry

Write-Host "AI_OS Recovery Bootstrap Supervisor Display"
Write-Host "Mode: $($supervisor.mode)"
Write-Host "Supervisor: $($supervisor.supervisor_name)"
Write-Host "Purpose: $($supervisor.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No queue state is restored. No workers are restarted. No scheduled or startup tasks are created."
Write-Host ""

Write-Host "Orchestration continuity:"
Write-Host "  Active branch: $($supervisor.active_branch)"
Write-Host "  Continuity state: $($supervisor.orchestration_continuity_state)"
Write-Host ""

Write-Host "Queue restore visibility:"
Write-Host "  Restore state: $($queueRestore.restore_state)"
Write-Host "  Restore backlog: $($queueRestore.restore_backlog)"
Write-Host "  Interrupted sessions: $($queueRestore.interrupted_sessions)"
Write-Host "  Queue restore state: $($queueRestore.queue_restore_state)"
Write-Host "  Notes: $($queueRestore.notes)"
Write-Host ""

Write-Host "Worker restore visibility:"
foreach ($worker in $workerRestore) {
    $packet = if ([string]::IsNullOrWhiteSpace([string]$worker.last_known_packet)) { "none" } else { $worker.last_known_packet }

    Write-Host "  Worker: $($worker.worker_id)"
    Write-Host "    Restore state: $($worker.restore_state)"
    Write-Host "    Last known packet: $packet"
    Write-Host "    Last known branch: $($worker.last_known_branch)"
    Write-Host "    Safe restart visible: $($worker.safe_restart_visible)"
    Write-Host "    Notes: $($worker.notes)"
}
Write-Host ""

Write-Host "Packet restore visibility:"
foreach ($packet in $packetRestore) {
    Write-Host "  Packet: $($packet.packet_id)"
    Write-Host "    Restore state: $($packet.restore_state)"
    Write-Host "    Last known worker: $($packet.last_known_worker)"
    Write-Host "    Safe restart visible: $($packet.safe_restart_visible)"
    Write-Host "    Notes: $($packet.notes)"
}
Write-Host ""

Write-Host "Recovery checkpoints:"
foreach ($checkpoint in $checkpoints) {
    Write-Host "  Checkpoint: $($checkpoint.checkpoint_id)"
    Write-Host "    Path: $($checkpoint.checkpoint_path)"
    Write-Host "    State: $($checkpoint.checkpoint_state)"
}
Write-Host ""

Write-Host "Recovery telemetry:"
Write-Host "  Recovery checkpoints: $($telemetry.recovery_checkpoints)"
Write-Host "  Restore backlog: $($telemetry.restore_backlog)"
Write-Host "  Interrupted sessions: $($telemetry.interrupted_sessions)"
Write-Host "  Queue restore state: $($telemetry.queue_restore_state)"
Write-Host "  Worker restore count: $($telemetry.worker_restore_count)"
Write-Host "  Packet restore count: $($telemetry.packet_restore_count)"
Write-Host ""

Write-Host "Blocked actions:"
Write-List -Items @($supervisor.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review recovery visibility only; use a separate approved workflow before restoring queue state or restarting workers."
