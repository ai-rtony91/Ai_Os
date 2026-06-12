param(
    [string]$PacketRoot = "automation/orchestration/work_packets",
    [string]$CampaignNextTaskScript = "automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1",
    [switch]$QuietJson,
    [switch]$OutputJson
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

function Read-AiOsPacketFolder {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string]$State
    )

    $folder = Join-Path $Root $State
    if (-not (Test-Path -LiteralPath $folder -PathType Container)) {
        return @()
    }

    return @(Get-ChildItem -LiteralPath $folder -Filter "*.json" -File | ForEach-Object {
        $packet = Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json
        [pscustomobject]@{
            file = $_
            folder_state = $State
            packet = $packet
        }
    })
}

function Get-LatestPacketEntry {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [Parameter(Mandatory = $true)][string[]]$States
    )

    $entries = @()
    foreach ($state in $States) {
        $entries += @(Read-AiOsPacketFolder -Root $Root -State $state)
    }

    if ($entries.Count -eq 0) {
        return $null
    }

    return $entries | Sort-Object { $_.file.LastWriteTimeUtc }, { $_.file.Name } -Descending | Select-Object -First 1
}

function Get-CampaignRecommendation {
    param([string]$ScriptPath)

    if (-not (Test-Path -LiteralPath $ScriptPath -PathType Leaf)) {
        return $null
    }

    try {
        $raw = powershell -NoProfile -ExecutionPolicy Bypass -File $ScriptPath -OutputJson 2>$null
        $text = ($raw | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($text)) {
            return $null
        }
        return $text | ConvertFrom-Json
    }
    catch {
        return [pscustomobject]@{
            overall_readiness = "REVIEW_REQUIRED"
            reason = $_.Exception.Message
            next_safe_action = "Review campaign registry recommendation failure."
        }
    }
}

function Get-NextAction {
    param([string]$Status)

    switch ($Status) {
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
        "campaign_ready" { return "Create or review the campaign packet candidate as DRY_RUN first." }
        "no_active_packet" { return "Review campaign registry statuses and create or approve one next packet candidate." }
        default { return "Unknown state. Stop and inspect packet." }
    }
}

$activeEntry = Get-LatestPacketEntry -Root $PacketRoot -States @("active")
$blockedEntry = Get-LatestPacketEntry -Root $PacketRoot -States @("blocked")
$completeEntry = Get-LatestPacketEntry -Root $PacketRoot -States @("complete")

if ($null -ne $activeEntry) {
    $packet = $activeEntry.packet
    $effectiveStatus = if ([string]::IsNullOrWhiteSpace([string]$packet.status)) { "active" } else { [string]$packet.status }
    $result = [pscustomobject]@{
        mode = "READ_ONLY"
        source = "work_packets_active"
        latest_packet_file = $activeEntry.file.FullName
        folder_state = $activeEntry.folder_state
        packet_id = $packet.packet_id
        status = $effectiveStatus
        owner_lane = $packet.owner_lane
        assigned_worker = $packet.assigned_worker
        next_step = Get-NextAction -Status $effectiveStatus
    }
}
elseif ($null -ne $blockedEntry) {
    $packet = $blockedEntry.packet
    $effectiveStatus = if ([string]::IsNullOrWhiteSpace([string]$packet.status)) { "blocked" } else { [string]$packet.status }
    $result = [pscustomobject]@{
        mode = "READ_ONLY"
        source = "work_packets_blocked"
        latest_packet_file = $blockedEntry.file.FullName
        folder_state = $blockedEntry.folder_state
        packet_id = $packet.packet_id
        status = $effectiveStatus
        owner_lane = $packet.owner_lane
        assigned_worker = $packet.assigned_worker
        next_step = Get-NextAction -Status $effectiveStatus
    }
}
else {
    $campaign = Get-CampaignRecommendation -ScriptPath $CampaignNextTaskScript
    if ($campaign -and [string]$campaign.overall_readiness -eq "READY_FOR_PACKET_PREVIEW") {
        $result = [pscustomobject]@{
            mode = "READ_ONLY"
            source = "campaign_registry"
            latest_packet = "NONE"
            latest_complete_packet_file = if ($null -ne $completeEntry) { $completeEntry.file.FullName } else { "" }
            packet_id = [string]$campaign.next_packet_candidate
            status = "campaign_ready"
            owner_lane = [string]$campaign.recommended_lane
            assigned_worker = [string]$campaign.recommended_worker
            recommended_campaign = $campaign.recommended_campaign
            recommended_stage = $campaign.recommended_stage
            next_step = $campaign.next_safe_action
        }
    }
    else {
        $result = [pscustomobject]@{
            mode = "READ_ONLY"
            source = "campaign_registry"
            latest_packet = "NONE"
            latest_complete_packet_file = if ($null -ne $completeEntry) { $completeEntry.file.FullName } else { "" }
            packet_id = "NONE"
            status = "no_active_packet"
            owner_lane = ""
            assigned_worker = ""
            campaign_readiness = if ($campaign) { [string]$campaign.overall_readiness } else { "UNAVAILABLE" }
            campaign_reason = if ($campaign) { [string]$campaign.reason } else { "Campaign recommendation unavailable." }
            next_step = if ($campaign -and $campaign.next_safe_action) { [string]$campaign.next_safe_action } else { Get-NextAction -Status "no_active_packet" }
        }
    }
}

if ($QuietJson -or $OutputJson) {
    $result | ConvertTo-Json -Depth 8
    exit 0
}

Write-Host "COPY START - Resolve-AiOsNextStep.DRY_RUN.ps1"
Write-Host "AI_OS Auto Next-Step Detector" -ForegroundColor Cyan
Write-Host "Mode: READ_ONLY"

$result.PSObject.Properties | ForEach-Object {
    Write-Host "$($_.Name): $($_.Value)"
}

Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Resolve-AiOsNextStep.DRY_RUN.ps1"
