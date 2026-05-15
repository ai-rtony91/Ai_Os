Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$startupPath = Join-Path $orchestrationRoot "startup_orchestration.v1.example.json"

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

$startup = Read-JsonFile -Path $startupPath
$packets = @($startup.startup_packets)

Write-Host "AI_OS Startup Orchestration Display"
Write-Host "Mode: $($startup.mode)"
Write-Host "Startup: $($startup.startup_name)"
Write-Host "Purpose: $($startup.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No startup tasks or scheduled tasks are created. Nothing is launched or restored."
Write-Host ""

$blockedPackets = @($packets | Where-Object { $_.blocked_startup_state -eq $true })
$recoveryPackets = @($packets | Where-Object { $_.startup_recovery_visibility -match "review|recovery" })

Write-Host "Startup summary:"
Write-Host "  Active branch: $($startup.active_branch)"
Write-Host "  Startup-safe branch visibility: $($startup.startup_safe_branch_visibility)"
Write-Host "  Startup continuity state: $($startup.startup_continuity_state)"
Write-Host "  Startup packets: $($packets.Count)"
Write-Host "  Recovery-visible packets: $($recoveryPackets.Count)"
Write-Host "  Blocked startup packets: $($blockedPackets.Count)"
Write-Host ""

foreach ($packet in $packets) {
    Write-Host "Startup packet: $($packet.packet_id)"
    Write-Host "  Name: $($packet.packet_name)"
    Write-Host "  Startup state: $($packet.startup_state)"
    Write-Host "  Queue visibility: $($packet.startup_queue_visibility)"
    Write-Host "  Recovery visibility: $($packet.startup_recovery_visibility)"
    Write-Host "  Startup-safe branch: $($packet.startup_safe_branch)"
    Write-Host "  Blocked startup state: $($packet.blocked_startup_state)"
    Write-Host "  Notes: $($packet.notes)"
    Write-Host ""
}

Write-Host "Blocked actions:"
Write-List -Items @($startup.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review startup visibility only; use a separate approved workflow before creating startup automation."
