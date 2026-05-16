param(
    [string]$PacketRoot = "automation/orchestration/work_packets",
    [switch]$QuietJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Get-LatestPacket {
    param([string]$Root)

    $files = @()
    foreach ($state in @("active", "blocked", "complete")) {
        $folder = Join-Path $Root $state
        if (Test-Path -LiteralPath $folder -PathType Container) {
            $files += Get-ChildItem -LiteralPath $folder -Filter "*.json" -File
        }
    }

    if ($files.Count -eq 0) {
        return $null
    }

    return $files | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

function Get-NextAction {
    param($Packet)

    switch ($Packet.status) {
        "active" { return "Route packet to owner lane." }
        "new" { return "Route packet to owner lane." }
        "routed" { return "Run DRY_RUN work and move packet to dry_run_done." }
        "dry_run_done" { return "Move packet to awaiting_approval." }
        "awaiting_approval" { return "Human must approve or block." }
        "approved" { return "Run APPLY work." }
        "applying" { return "Run validators." }
        "validated" { return "Move packet to complete." }
        "complete" { return "Create or review PR gate." }
        "blocked" { return "Fix blocker or reroute packet." }
        "failed" { return "Review failure and reroute packet." }
        default { return "Unknown state. Stop and inspect packet." }
    }
}

$latestFile = Get-LatestPacket -Root $PacketRoot

if ($null -eq $latestFile) {
    $result = [pscustomobject]@{
        mode = "READ_ONLY"
        latest_packet = "NONE"
        next_step = "Create a work packet."
    }
} else {
    $packet = Get-Content -Raw -LiteralPath $latestFile.FullName | ConvertFrom-Json
    $result = [pscustomobject]@{
        mode = "READ_ONLY"
        latest_packet_file = $latestFile.FullName
        packet_id = $packet.packet_id
        status = $packet.status
        owner_lane = $packet.owner_lane
        assigned_worker = $packet.assigned_worker
        next_step = Get-NextAction -Packet $packet
    }
}

if ($QuietJson) {
    $result | ConvertTo-Json -Depth 6
    exit 0
}

Write-Host "COPY START — Resolve-AiOsNextStep.DRY_RUN.ps1"
Write-Host "AI_OS Auto Next-Step Detector" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY"

$result.PSObject.Properties | ForEach-Object {
    Write-Host "$($_.Name): $($_.Value)"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END — Resolve-AiOsNextStep.DRY_RUN.ps1"
