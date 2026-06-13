param(
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RelayMessages {
    param([string]$Directory)

    if (-not (Test-Path -LiteralPath $Directory -PathType Container)) {
        return @()
    }

    return Get-ChildItem -LiteralPath $Directory -Filter "*.json" -File |
        Sort-Object -Property LastWriteTime -Descending
}

function Read-RelayMessage {
    param([string]$Path)

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

function Has-ForbiddenSecretPattern {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $false
    }

    $patterns = @(
        "AIOS_TG_BOT_TOKEN",
        "token=",
        "api_key",
        "secret",
        "bearer",
        "xoxb-"
    )

    foreach ($pattern in $patterns) {
        $escapedPattern = [regex]::Escape($pattern)
        if ([regex]::IsMatch($Text, $escapedPattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
            return $true
        }
    }

    return $false
}

$repoRoot = (Get-Location).Path
$inboxDir = Join-Path $repoRoot "control/relay_bus/messages/inbox"
$defaultAction = "Use New-AiOsRelayMessage.DRY_RUN.ps1 with Mode APPLY to write the first relay message."
$sosPolicyNextAction = "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Get-AiOsSosEscalationPolicy.DRY_RUN.ps1 -OutputJson"

$latestMessagePath = ""
$latestActor = ""
$latestTargetActor = ""
$latestPacketId = ""
$latestMessageType = ""
$latestIntent = ""
$latestStatus = ""
$resolutionStatus = "EMPTY"
$safeNextAction = "Use manual review to resolve this actor relay message."
$whyHumanReview = "No actor relay message found for review."
$hasPayloadSecret = $false
$isReviewNeeded = $false

$latestMessageFile = Get-RelayMessages -Directory $inboxDir | Select-Object -First 1
$latestMessage = if ($latestMessageFile) { Read-RelayMessage -Path $latestMessageFile.FullName } else { $null }

if ($null -ne $latestMessage) {
    $latestMessagePath = [string]$latestMessageFile.FullName
    $latestActor = [string]$latestMessage.actor
    $latestTargetActor = [string]$latestMessage.target_actor
    $latestPacketId = [string]$latestMessage.packet_id
    $latestMessageType = [string]$latestMessage.message_type
    $latestIntent = [string]$latestMessage.intent
    $latestStatus = [string]$latestMessage.status

    if ($latestMessage.PSObject.Properties.Name -contains "requires_human_review") {
        try {
            $isReviewNeeded = [bool]$latestMessage.requires_human_review
        }
        catch {
            $isReviewNeeded = $true
        }
    }
    else {
        $isReviewNeeded = $true
    }

    if ($latestMessage.PSObject.Properties.Name -contains "payload_text") {
        $hasPayloadSecret = Has-ForbiddenSecretPattern -Text [string]$latestMessage.payload_text
    }

    $reasons = New-Object System.Collections.Generic.List[string]
    if ([string]::IsNullOrWhiteSpace($latestStatus)) {
        $reasons.Add("Message status is missing and requires manual validation.")
    }
    elseif ([string]$latestStatus -eq "blocked_needs_owner") {
        $reasons.Add("Message status is BLOCKED_NEEDS_OWNER and needs manual operator routing.")
        $isReviewNeeded = $true
    }
    elseif ($isReviewNeeded) {
        $reasons.Add("Message is marked as requiring human review.")
    }
    else {
        $reasons.Add("Message currently has no explicit review stop reason in this resolver path.")
    }

    if ($hasPayloadSecret) {
        $reasons.Add("Message payload_text contains secret-like pattern and is blocked from review approval.")
        $isReviewNeeded = $true
    }

    if ($isReviewNeeded) {
        $resolutionStatus = "NEEDS_HUMAN_REVIEW"
        $safeNextAction = "Do not execute; open the actor relay message, resolve concerns, run SOS escalation policy classification with: $sosPolicyNextAction, then continue only with explicit Anthony approval."
    }
    else {
        $resolutionStatus = "READY"
        $safeNextAction = "Message is not marked for review by this resolver; confirm routing context before any execution."
    }

    $whyHumanReview = [string]::Join(" ", $reasons)
}

$result = [ordered]@{
    schema = "AIOS_RELAY_HUMAN_REVIEW_RESOLUTION.v1"
    mode = "DRY_RUN_READ_ONLY"
    status = $resolutionStatus
    writes_files = $false
    execution_allowed = $false
    can_continue_without_anthony = $false
    requires_human_review = $true
    sos_policy_next_action = if ($resolutionStatus -eq "NEEDS_HUMAN_REVIEW") { $sosPolicyNextAction } else { "" }
    latest_message_path = $latestMessagePath
    actor = $latestActor
    target_actor = $latestTargetActor
    packet_id = $latestPacketId
    message_type = $latestMessageType
    intent = $latestIntent
    status_detail = $latestStatus
    why_human_review_needed = $whyHumanReview
    safe_next_action = $safeNextAction
    payload_contains_forbidden_secret_pattern = $hasPayloadSecret
}

$result | ConvertTo-Json -Depth 20
