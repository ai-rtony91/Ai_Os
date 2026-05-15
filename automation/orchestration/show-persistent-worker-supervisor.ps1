Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$supervisorPath = Join-Path $orchestrationRoot "persistent_worker_supervisor.v1.example.json"

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
$workers = @($supervisor.workers)
$telemetry = $supervisor.telemetry

Write-Host "AI_OS Persistent Worker Supervisor Display"
Write-Host "Mode: $($supervisor.mode)"
Write-Host "Supervisor: $($supervisor.supervisor_name)"
Write-Host "Purpose: $($supervisor.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No workers are launched. No heartbeats, assignments, branches, or files are changed."
Write-Host ""

if ($workers.Count -eq 0) {
    Write-Host "Workers: none found in persistent_worker_supervisor.v1.example.json"
    exit 0
}

$activeWorkers = @($workers | Where-Object { $_.visibility_state -match "active" })
$staleWorkers = @($workers | Where-Object { $_.health_state -match "stale" })
$inactiveWorkers = @($workers | Where-Object { $_.health_state -match "inactive" })
$assignedWorkers = @($workers | Where-Object { -not [string]::IsNullOrWhiteSpace([string]$_.assigned_packet_id) })

Write-Host "Worker supervision summary:"
Write-Host "  Total workers: $($workers.Count)"
Write-Host "  Active workers: $($activeWorkers.Count)"
Write-Host "  Stale workers: $($staleWorkers.Count)"
Write-Host "  Inactive workers: $($inactiveWorkers.Count)"
Write-Host "  Assigned workers: $($assignedWorkers.Count)"
Write-Host ""

foreach ($worker in ($workers | Sort-Object worker_id)) {
    $lastHeartbeat = if ([string]::IsNullOrWhiteSpace([string]$worker.last_heartbeat)) { "none" } else { $worker.last_heartbeat }
    $assignedPacket = if ([string]::IsNullOrWhiteSpace([string]$worker.assigned_packet_id)) { "none" } else { $worker.assigned_packet_id }

    Write-Host "Worker: $($worker.worker_id)"
    Write-Host "  Role: $($worker.worker_role)"
    Write-Host "  Health: $($worker.health_state)"
    Write-Host "  Last heartbeat: $lastHeartbeat"
    Write-Host "  Stale after minutes: $($worker.stale_after_minutes)"
    Write-Host "  Assigned packet: $assignedPacket"
    Write-Host "  Worker branch: $($worker.worker_branch)"
    Write-Host "  Visibility state: $($worker.visibility_state)"
    Write-Host "  Notes: $($worker.notes)"
    Write-Host ""
}

Write-Host "Worker telemetry:"
Write-Host "  Active workers: $($telemetry.active_workers)"
Write-Host "  Stale workers: $($telemetry.stale_workers)"
Write-Host "  Inactive workers: $($telemetry.inactive_workers)"
Write-Host "  Assigned workers: $($telemetry.assigned_workers)"
Write-Host "  Worker restore candidates: $($telemetry.worker_restore_candidates)"
Write-Host ""

Write-Host "Blocked actions:"
Write-List -Items @($supervisor.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review worker supervision only; use a separate approved workflow before launching workers or changing state."
