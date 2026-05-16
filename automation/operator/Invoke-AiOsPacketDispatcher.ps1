param(
    [string]$RepoRoot = ".",
    [string]$QueuePath = "work_packets/queues/aios_phase2_queue.example.json",
    [string]$PacketRoot = ".",
    [switch]$Explain
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Stop-Dispatcher {
    param([string]$Message)
    Write-Host "DISPATCH BLOCKED: $Message" -ForegroundColor Red
    exit 1
}

function Resolve-ExistingFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$BasePath
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        $candidate = $Path
    } else {
        $candidate = Join-Path $BasePath $Path
    }

    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
        Stop-Dispatcher "File not found: $Path"
    }

    return (Resolve-Path -LiteralPath $candidate).Path
}

function Read-Json {
    param([Parameter(Mandatory = $true)][string]$Path)
    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    } catch {
        Stop-Dispatcher "JSON parse failed: $Path :: $($_.Exception.Message)"
    }
}

$resolvedRepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path
$resolvedPacketRoot = if ([System.IO.Path]::IsPathRooted($PacketRoot)) {
    (Resolve-Path -LiteralPath $PacketRoot).Path
} else {
    (Resolve-Path -LiteralPath (Join-Path $resolvedRepoRoot $PacketRoot)).Path
}
$resolvedQueuePath = Resolve-ExistingFile -Path $QueuePath -BasePath $resolvedRepoRoot
$queue = Read-Json -Path $resolvedQueuePath

Write-Host "AI_OS Packet Dispatcher DRY_RUN" -ForegroundColor Cyan
Write-Host "Repo: $resolvedRepoRoot"
Write-Host "Queue: $QueuePath"
Write-Host "Packet root: $resolvedPacketRoot"
Write-Host "Safety: read-only dispatch plan. No packet edits, launches, windows, commits, pushes, startup tasks, or scheduled tasks."

if ($queue.mode -ne "DRY_RUN") {
    Stop-Dispatcher "Phase 2 dispatcher only accepts queue mode DRY_RUN."
}

if ($Explain) {
    Write-Host ""
    Write-Host "Explanation:" -ForegroundColor Yellow
    Write-Host "  Pending packets are held for operator review or approval."
    Write-Host "  Approved packets are routed to their declared queue lane."
    Write-Host "  Blocked packets are not dispatched and keep their blocked reason."
    Write-Host "  The operator approval gate remains required before APPLY, commit, or push."
}

Write-Host ""
Write-Host "Queue state:" -ForegroundColor Yellow
Write-Host "  Queue ID: $($queue.queue_id)"
Write-Host "  Version: $($queue.version)"
Write-Host "  Mode: $($queue.mode)"
Write-Host "  Status: $($queue.queue_status)"
Write-Host "  Updated: $($queue.updated_at)"
Write-Host "  Next action: $($queue.next_action)"
Write-Host "  Stop condition: $($queue.stop_condition)"

$pendingPackets = New-Object System.Collections.Generic.List[object]
$approvedPackets = New-Object System.Collections.Generic.List[object]
$blockedPackets = New-Object System.Collections.Generic.List[object]

Write-Host ""
Write-Host "Role / lane mapping:" -ForegroundColor Yellow
foreach ($lane in @($queue.lanes)) {
    Write-Host "  $($lane.lane): $($lane.role) [$($lane.status)]"
}

Write-Host ""
Write-Host "Dispatch plan:" -ForegroundColor Yellow
foreach ($packet in @($queue.packets | Sort-Object priority)) {
    $sourcePath = Resolve-ExistingFile -Path $packet.source_file -BasePath $resolvedPacketRoot
    $sourcePacket = Read-Json -Path $sourcePath

    $decision = "hold_for_review"
    if ($packet.status -eq "blocked" -or $packet.approval_state -eq "rejected") {
        $decision = "blocked"
        $blockedPackets.Add($packet) | Out-Null
    } elseif ($packet.status -eq "approved" -and $packet.approval_state -eq "approved") {
        $decision = "dispatch_to_$($packet.lane)"
        $approvedPackets.Add($packet) | Out-Null
    } else {
        $pendingPackets.Add($packet) | Out-Null
    }

    Write-Host ""
    Write-Host "  Packet: $($packet.packet_id)" -ForegroundColor White
    Write-Host "    Title: $($packet.title)"
    Write-Host "    Source file: $($packet.source_file)"
    Write-Host "    Source packet id: $($sourcePacket.id)"
    Write-Host "    Source packet lane: $($sourcePacket.lane)"
    Write-Host "    Assigned lane: $($packet.lane)"
    Write-Host "    Assigned worker: $($packet.assigned_worker)"
    Write-Host "    Status: $($packet.status)"
    Write-Host "    Priority: $($packet.priority)"
    Write-Host "    Approval state: $($packet.approval_state)"
    Write-Host "    Validator state: $($packet.validator_state)"
    Write-Host "    Dispatch decision: $decision"
    Write-Host "    Next safe action: $($packet.next_action)"
    if (-not [string]::IsNullOrWhiteSpace([string]$packet.blocked_reason)) {
        Write-Host "    Blocked reason: $($packet.blocked_reason)"
    }
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Pending packets: $($pendingPackets.Count)"
Write-Host "  Approved packets: $($approvedPackets.Count)"
Write-Host "  Blocked packets: $($blockedPackets.Count)"
Write-Host "  Queue state changed: NO"
Write-Host "  Codex auto-launch performed: NO"
Write-Host "  Commit performed: NO"
Write-Host "  Push performed: NO"
Write-Host "  Operator approval gate: REQUIRED"
exit 0
