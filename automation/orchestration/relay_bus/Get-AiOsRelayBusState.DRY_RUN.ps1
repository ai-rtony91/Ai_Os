param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RelayActors {
    param([string]$RegistryPath)

    if (-not (Test-Path -LiteralPath $RegistryPath -PathType Leaf)) {
        return @()
    }

    try {
        $raw = Get-Content -LiteralPath $RegistryPath -Raw
        $payload = $raw | ConvertFrom-Json -ErrorAction Stop
        if ($payload -and $payload.actors) {
            return @($payload.actors)
        }
    }
    catch {
        return @()
    }

    return @()
}

function Get-RelayMessages {
    param([string]$MessagesDir)

    if (-not (Test-Path -LiteralPath $MessagesDir -PathType Container)) {
        return @()
    }

    $items = Get-ChildItem -LiteralPath $MessagesDir -Filter "*.json" -File |
        Sort-Object -Property LastWriteTime -Descending
    $messages = New-Object System.Collections.Generic.List[object]

    foreach ($item in $items) {
        try {
            $raw = Get-Content -LiteralPath $item.FullName -Raw
            $obj = $raw | ConvertFrom-Json -ErrorAction Stop
            $obj | Add-Member -NotePropertyName "message_path" -NotePropertyValue $item.FullName -Force
            $messages.Add($obj)
        }
        catch {
            continue
        }
    }

    if ($messages.Count -eq 0) {
        return @()
    }
    return ,($messages.ToArray())
}

$repoRoot = (Get-Location).Path
$registryPath = Join-Path $repoRoot "control/relay_bus/actors/AIOS_RELAY_ACTORS.json"
$inboxDir = Join-Path $repoRoot "control/relay_bus/messages/inbox"

$actors = Get-RelayActors -RegistryPath $registryPath
$enabledActors = if ($actors) { @($actors | Where-Object { $_.enabled -eq $true } | ForEach-Object { [string]$_.actor_id }) } else { @() }
$actorCount = if ($actors) { $actors.Count } else { 0 }

$messages = Get-RelayMessages -MessagesDir $inboxDir
$latestMessage = if ($messages.Count -gt 0) { $messages[0] } else { $null }

$latestPath = ""
$latestActor = ""
$latestTargetActor = ""
$latestMessageType = ""
$latestPacketId = ""
$relayStatus = "EMPTY"
$nextAction = "Use New-AiOsRelayMessage.DRY_RUN.ps1 with Mode APPLY to write the first relay message."
$pendingMessages = New-Object System.Collections.Generic.List[string]

if ($latestMessage) {
    $latestPath = [string]$latestMessage.message_path
    $latestActor = [string]$latestMessage.actor
    $latestTargetActor = [string]$latestMessage.target_actor
    $latestMessageType = [string]$latestMessage.message_type
    $latestPacketId = [string]$latestMessage.packet_id

    $latestRequiresReview = $true
    if ($latestMessage.PSObject.Properties.Name -contains "requires_human_review") {
        $latestRequiresReview = [bool]$latestMessage.requires_human_review
    }

    if ([string]$latestMessage.status -eq "blocked_needs_owner") {
        $relayStatus = "BLOCKED_NEEDS_OWNER"
        $nextAction = "Resolve owner/routing for the blocked message and re-emit it."
    }
    elseif ([string]$latestMessage.message_type -eq "reviewed_powershell") {
        $relayStatus = "READY_FOR_POWERSHELL_PASTEBACK"
        $nextAction = "Hand reviewed PowerShell payload to Anthony for manual execution."
    }
    elseif ([string]$latestMessage.message_type -eq "evidence_note") {
        $relayStatus = "REVIEW_READY"
        $nextAction = "Review the evidence message in ChatGPT for next relay step."
    }
    elseif ($latestRequiresReview) {
        $relayStatus = "NEEDS_HUMAN_REVIEW"
        $nextAction = "Run manual human review on this actor message before continuing."
    }
    else {
        $relayStatus = "NEEDS_HUMAN_REVIEW"
        $nextAction = "Run manual human review before any next relay action."
    }
}

foreach ($msg in $messages) {
    $needsReview = $true
    if ($msg.PSObject.Properties.Name -contains "requires_human_review") {
        $needsReview = [bool]$msg.requires_human_review
    }
    if ($needsReview -and ($msg.PSObject.Properties.Name -contains "message_id")) {
        $pendingMessages.Add([string]$msg.message_path)
    }
}

$result = [ordered]@{
    schema = "AIOS_RELAY_BUS_STATE.v1"
    mode = "DRY_RUN_READ_ONLY"
    actor_count = $actorCount
    enabled_actors = @($enabledActors)
    latest_message_path = $latestPath
    latest_actor = $latestActor
    latest_target_actor = $latestTargetActor
    latest_message_type = $latestMessageType
    latest_packet_id = $latestPacketId
    pending_human_review_count = $pendingMessages.Count
    pending_messages = @($pendingMessages)
    relay_status = $relayStatus
    exact_next_action = $nextAction
    writes_files = $false
    execution_allowed = $false
    can_continue_without_anthony = $false
}

$result | ConvertTo-Json -Depth 20
