Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$orchestrationRoot = $PSScriptRoot
$continuityPath = Join-Path $orchestrationRoot "session_continuity.v1.example.json"

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

$continuity = Read-JsonFile -Path $continuityPath
$sessions = @($continuity.sessions)
$startup = $continuity.recovery_safe_startup
$checkpoints = @($startup.continuity_checkpoints)

Write-Host "AI_OS Session Continuity Display"
Write-Host "Mode: $($continuity.mode)"
Write-Host "Continuity: $($continuity.continuity_name)"
Write-Host "Purpose: $($continuity.purpose)"
Write-Host ""
Write-Host "Safety: display-only. No sessions, workers, packets, queues, branches, startup tasks, or scheduled tasks are restored or changed."
Write-Host ""

$activeSessions = @($sessions | Where-Object { $_.session_state -match "active" })
$interruptedSessions = @($sessions | Where-Object { $_.interrupted -eq $true })

Write-Host "Continuity summary:"
Write-Host "  Total sessions: $($sessions.Count)"
Write-Host "  Active sessions: $($activeSessions.Count)"
Write-Host "  Interrupted sessions: $($interruptedSessions.Count)"
Write-Host "  Recovery startup state: $($startup.startup_state)"
Write-Host "  Restore visibility: $($startup.startup_restore_visibility)"
Write-Host "  Continuity checkpoints: $($checkpoints.Count)"
Write-Host ""

foreach ($session in $sessions) {
    Write-Host "Session: $($session.session_id)"
    Write-Host "  State: $($session.session_state)"
    Write-Host "  Active branch: $($session.active_branch)"
    Write-Host "  Packet continuity: $($session.packet_continuity)"
    Write-Host "  Worker continuity: $($session.worker_continuity)"
    Write-Host "  Queue continuity: $($session.queue_continuity)"
    Write-Host "  Branch continuity: $($session.branch_continuity)"
    Write-Host "  Interrupted: $($session.interrupted)"
    Write-Host "  Notes: $($session.notes)"
    Write-Host ""
}

Write-Host "Recovery-safe startup:"
Write-Host "  Startup state: $($startup.startup_state)"
Write-Host "  Blocked startup state: $($startup.blocked_startup_state)"
Write-Host "  Startup restore visibility: $($startup.startup_restore_visibility)"
Write-Host "  Next safe action: $($startup.next_safe_action)"
Write-Host "  Continuity checkpoints:"
Write-List -Items $checkpoints
Write-Host ""

Write-Host "Blocked actions:"
Write-List -Items @($continuity.blocked_actions)
Write-Host ""

Write-Host "Next safe action: review continuity visibility only; use a separate approved workflow before restoring sessions or creating startup automation."
