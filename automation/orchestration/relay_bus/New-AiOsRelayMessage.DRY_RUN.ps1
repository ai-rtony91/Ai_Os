param(
    [Parameter(Mandatory = $true)][string]$Actor,
    [Parameter(Mandatory = $true)][string]$TargetActor,
    [Parameter(Mandatory = $true)][string]$PacketId,
    [Parameter(Mandatory = $true)][string]$Branch,
    [Parameter(Mandatory = $true)][string]$MessageType,
    [Parameter(Mandatory = $true)][string]$Intent,
    [Parameter(Mandatory = $true)][string]$Status,
    [string]$PayloadText = "",
    [string]$PayloadPath = "",
    [ValidateSet("DRY_RUN", "APPLY")][string]$Mode = "DRY_RUN",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-RelayActors {
    param([string]$Root)

    $registryPath = Join-Path $Root "control/relay_bus/actors/AIOS_RELAY_ACTORS.json"
    if (-not (Test-Path -LiteralPath $registryPath -PathType Leaf)) {
        return @()
    }

    try {
        $raw = Get-Content -LiteralPath $registryPath -Raw
        $payload = $raw | ConvertFrom-Json -ErrorAction Stop
        if ($payload -is [PSCustomObject] -and $payload.actors) {
            return @($payload.actors)
        }
        return @()
    }
    catch {
        return @()
    }
}

function Find-Actor {
    param([string]$ActorId, [object[]]$Actors)
    foreach ($actor in $Actors) {
        if ([string]$actor.actor_id -eq $ActorId) {
            return $actor
        }
    }
    return $null
}

function Get-PayloadText {
    param([string]$Text, [string]$Path)

    if (-not [string]::IsNullOrWhiteSpace($Text)) {
        return $Text
    }

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "PayloadPath not found: $Path"
    }
    return Get-Content -LiteralPath $Path -Raw
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
        if ($Text -match [regex]::Escape($pattern)) {
            return $true
        }
    }
    return $false
}

function Get-SafeName {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return "unknown"
    }
    return $Value -replace "[^A-Za-z0-9._-]", "_"
}

$repoRoot = (Get-Location).Path
$actors = Get-RelayActors -Root $repoRoot
$blockedReasons = New-Object System.Collections.Generic.List[string]
$warnings = New-Object System.Collections.Generic.List[string]

if (-not $actors -or $actors.Count -eq 0) {
    $blockedReasons.Add("Actor registry missing or unreadable.")
}

$actorObj = Find-Actor -ActorId $Actor -Actors $actors
$targetObj = Find-Actor -ActorId $TargetActor -Actors $actors
if ($null -eq $actorObj) {
    $blockedReasons.Add("Unknown actor: $Actor")
}
if ($null -eq $targetObj) {
    $blockedReasons.Add("Unknown target actor: $TargetActor")
}

$messagePayload = ""
try {
    $messagePayload = Get-PayloadText -Text $PayloadText -Path $PayloadPath
}
catch {
    $blockedReasons.Add($_.Exception.Message)
}

if (Has-ForbiddenSecretPattern -Text $messagePayload) {
    $blockedReasons.Add("Forbidden token/secret pattern detected in payload_text.")
}

if ([string]::IsNullOrWhiteSpace($PayloadText) -and [string]::IsNullOrWhiteSpace($PayloadPath)) {
    $warnings.Add("payload_text is empty.")
}

$createdUtc = [DateTime]::UtcNow.ToString("o")
$timestamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$filenameTimestamp = [DateTime]::UtcNow.ToString("yyyyMMddTHHmmssZ")
$safeActor = Get-SafeName -Value $Actor
$safeTarget = Get-SafeName -Value $TargetActor
$safeMessageType = Get-SafeName -Value $MessageType
$safePacketId = Get-SafeName -Value $PacketId

$messageId = "{0}_{1}_{2}_{3}" -f $timestamp, $safeActor, $safeMessageType, $safePacketId
$requiresHumanReview = $true
$executionAllowed = $false
$canContinueWithoutAnthony = $false
$nextAction = "Route this message to actor handoff tooling and continue only through AI_OS relay approvals."

$allowedActorTypes = $true
if ($actorObj -and $actorObj.PSObject.Properties.Name -contains "allowed_message_types") {
    if ($actorObj.allowed_message_types -notcontains $MessageType) {
        $warnings.Add("Actor '$Actor' is not explicitly configured for message_type '$MessageType'.")
    }
}
if ($targetObj -and $targetObj.PSObject.Properties.Name -contains "allowed_message_types") {
    if ($targetObj.allowed_message_types -notcontains $MessageType) {
        $warnings.Add("Target actor '$TargetActor' is not explicitly configured for message_type '$MessageType'.")
    }
}

if ($blockedReasons.Count -gt 0) {
    $evidence = [ordered]@{
        blocked_reasons = @($blockedReasons)
        warnings = @($warnings)
        valid_actor = [bool]($null -ne $actorObj)
        valid_target_actor = [bool]($null -ne $targetObj)
    }

    $result = [ordered]@{
        schema = "AIOS_RELAY_MESSAGE_RESULT.v1"
        mode = "DRY_RUN_READ_ONLY"
        writes_files = $false
        relay_file = ""
        message_id = $messageId
        message = [ordered]@{
            schema = "AIOS_RELAY_MESSAGE.v1"
            message_id = $messageId
            created_utc = $createdUtc
            actor = $Actor
            target_actor = $TargetActor
            packet_id = $PacketId
            branch = $Branch
            message_type = $MessageType
            intent = $Intent
            status = $Status
            payload_text = $messagePayload
            evidence = $evidence
            next_action = $nextAction
            requires_human_review = $requiresHumanReview
            execution_allowed = $executionAllowed
            can_continue_without_anthony = $canContinueWithoutAnthony
        }
        blocked = $true
    }

    if ($OutputJson) {
        $result | ConvertTo-Json -Depth 20
        exit 0
    }
    Write-Output ($result | ConvertTo-Json -Depth 20)
    exit 0
}

$message = [ordered]@{
    schema = "AIOS_RELAY_MESSAGE.v1"
    message_id = $messageId
    created_utc = $createdUtc
    actor = $Actor
    target_actor = $TargetActor
    packet_id = $PacketId
    branch = $Branch
    message_type = $MessageType
    intent = $Intent
    status = $Status
    payload_text = $messagePayload
    evidence = [ordered]@{
        actor_enabled = [bool]$actorObj.enabled
        target_actor_enabled = [bool]$targetObj.enabled
        warnings = @($warnings)
    }
    next_action = $nextAction
    requires_human_review = $requiresHumanReview
    execution_allowed = $executionAllowed
    can_continue_without_anthony = $canContinueWithoutAnthony
}

$result = [ordered]@{
    schema = "AIOS_RELAY_MESSAGE_RESULT.v1"
    mode = if ($Mode -eq "APPLY") { "APPLY" } else { "DRY_RUN_READ_ONLY" }
    writes_files = $false
    relay_file = ""
    message_id = $message.message_id
    message = $message
    blocked = $false
}

if ($Mode -eq "APPLY") {
    $inboxDir = Join-Path $repoRoot "control/relay_bus/messages/inbox"
    if (-not (Test-Path -LiteralPath $inboxDir -PathType Container)) {
        New-Item -ItemType Directory -Path $inboxDir -Force | Out-Null
    }

    $fileName = "{0}_{1}_{2}_{3}.json" -f $filenameTimestamp, $safeActor, $safeMessageType, $safePacketId
    $relayFile = Join-Path $inboxDir $fileName
    $payloadText = $message | ConvertTo-Json -Depth 20
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($relayFile, $payloadText, $encoding)
    $result.writes_files = $true
    $result.relay_file = $relayFile
}
else {
    $result.write_preview = $message
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($result | ConvertTo-Json -Depth 20)
