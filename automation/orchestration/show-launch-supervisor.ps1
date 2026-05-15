Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$supervisorPath = Join-Path $orchestrationRoot "launch_supervisor.v1.example.json"

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
$lanes = @($supervisor.launch_lanes)

Write-Host "AI_OS Launch Supervisor Display"
Write-Host "Mode: $($supervisor.mode)"
Write-Host "Supervisor: $($supervisor.supervisor_name)"
Write-Host "Purpose: $($supervisor.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No workers, packets, startup tasks, or scheduled tasks are launched."
Write-Host ""

$readyLanes = @($lanes | Where-Object { $_.launch_readiness -match "ready" })
$blockedLanes = @($lanes | Where-Object { $_.launch_safety_state -match "blocked" -or $_.blocked_startup_visibility -eq $true })

Write-Host "Launch summary:"
Write-Host "  Total lanes: $($lanes.Count)"
Write-Host "  Review-ready lanes: $($readyLanes.Count)"
Write-Host "  Blocked/visible lanes: $($blockedLanes.Count)"
Write-Host ""

foreach ($lane in $lanes) {
    Write-Host "Lane: $($lane.lane_id)"
    Write-Host "  Name: $($lane.lane_name)"
    Write-Host "  Worker startup visible: $($lane.worker_startup_visible)"
    Write-Host "  Assigned worker: $($lane.assigned_worker_id)"
    Write-Host "  Assigned packet: $($lane.assigned_packet_id)"
    Write-Host "  Launch readiness: $($lane.launch_readiness)"
    Write-Host "  Launch safety state: $($lane.launch_safety_state)"
    Write-Host "  Blocked startup visible: $($lane.blocked_startup_visibility)"
    Write-Host "  Block reason: $($lane.block_reason)"
    Write-Host "  Notes: $($lane.notes)"
    Write-Host ""
}

Write-Host "Blocked actions:"
Write-List -Items @($supervisor.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review launch lanes only; use a separate approved workflow before launching workers or packets."
