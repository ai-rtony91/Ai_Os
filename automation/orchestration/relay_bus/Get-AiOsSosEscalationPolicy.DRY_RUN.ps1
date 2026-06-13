param(
    [string]$RelayReviewJsonPath = "",
    [string]$PayloadText = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-JsonFile {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path) -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return $null
    }

    try {
        return Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

function Invoke-Resolver {
    param([string]$RepoRoot)

    $resolverScript = Join-Path $RepoRoot "Resolve-AiOsRelayHumanReview.DRY_RUN.ps1"
    if (-not (Test-Path -LiteralPath $resolverScript -PathType Leaf)) {
        return $null
    }

    try {
        $raw = & powershell -NoProfile -ExecutionPolicy Bypass -File $resolverScript -OutputJson 2>$null
        $rawText = ($raw | Out-String).Trim()
        if ([string]::IsNullOrWhiteSpace($rawText)) {
            return $null
        }

        return $rawText | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        return $null
    }
}

function To-SafeText {
    param([object]$Value)

    if ($null -eq $Value) {
        return ""
    }
    return [string]$Value
}

function Has-Pattern {
    param(
        [string]$Text,
        [string[]]$Patterns
    )

    foreach ($pattern in $Patterns) {
        if ([regex]::IsMatch($Text, $pattern, [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)) {
            return $true
        }
    }

    return $false
}

$repoRoot = (Get-Location).Path
$resolverOutput = $null
$status = ""
$resolverHasOutput = $false
$escalationReasons = New-Object System.Collections.Generic.List[string]
$scanText = New-Object System.Collections.Generic.List[string]
$safeNextAction = ""
$anthonyRequired = $false
$routineReviewAllowed = $false

if (-not [string]::IsNullOrWhiteSpace($RelayReviewJsonPath)) {
    $resolverOutput = Read-JsonFile -Path $RelayReviewJsonPath
    $resolverHasOutput = $resolverOutput -ne $null
    if ($null -eq $resolverOutput) {
        $escalationReasons.Add("Resolver review file could not be parsed.")
    }
}
elseif ([string]::IsNullOrWhiteSpace($PayloadText)) {
    $resolverOutput = Invoke-Resolver -RepoRoot (Split-Path -Parent $PSCommandPath)
    $resolverHasOutput = $resolverOutput -ne $null
    if ($null -eq $resolverOutput) {
        $escalationReasons.Add("Resolver output unavailable; treating as routine-only path with no escalation.")
    }
}
else {
    $resolverOutput = [ordered]@{
        schema = "AIOS_RELAY_HUMAN_REVIEW_RESOLUTION.v1"
        status = "NEEDS_HUMAN_REVIEW"
        why_human_review_needed = "Direct payload supplied for SOS classification."
        status_detail = ""
        actor = ""
        target_actor = ""
        packet_id = ""
        message_type = ""
        intent = ""
        safe_next_action = "Review the supplied payload in the normal relay workflow."
    }
}

if ($resolverOutput -ne $null) {
    $status = To-SafeText $resolverOutput.status
    $scanText.Add((To-SafeText $resolverOutput.status))
    $scanText.Add((To-SafeText $resolverOutput.why_human_review_needed))
    $scanText.Add((To-SafeText $resolverOutput.status_detail))
    $scanText.Add((To-SafeText $resolverOutput.intent))
    $scanText.Add((To-SafeText $resolverOutput.message_type))
    $scanText.Add((To-SafeText $resolverOutput.latest_message_path))
    if ($resolverOutput.PSObject.Properties.Name -contains "payload_contains_forbidden_secret_pattern") {
        if ([bool]$resolverOutput.payload_contains_forbidden_secret_pattern -eq $true) {
            $hasEscalation = $true
            $escalationReasons.Add("Resolver output indicates the payload contains a secret-like pattern.")
        }
    }
    if (-not [string]::IsNullOrWhiteSpace($resolverOutput.latest_message_path)) {
        $latestMessage = Read-JsonFile -Path $resolverOutput.latest_message_path
        if ($null -ne $latestMessage) {
            $scanText.Add((To-SafeText $latestMessage.payload_text))
            $scanText.Add((To-SafeText $latestMessage.message_type))
            $scanText.Add((To-SafeText $latestMessage.intent))
            $scanText.Add((To-SafeText $latestMessage.status))
            $scanText.Add((To-SafeText $latestMessage.actor))
            $scanText.Add((To-SafeText $latestMessage.target_actor))
        }
    }
}

if (-not [string]::IsNullOrWhiteSpace($PayloadText)) {
    $scanText.Add($PayloadText.Trim())
}

$scanBlob = [string]::Join(" ", $scanText)

$hasEscalation = $false

if (Has-Pattern -Text $scanBlob -Patterns @(
        "AIOS_TG_BOT_TOKEN",
        "token=",
        "api_key",
        "secret",
        "credential",
        "bearer"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Secret, token, API key, credential, or bearer-string material was detected.")
}

if (Has-Pattern -Text $scanBlob -Patterns @(
        "\bbroker\b",
        "\boanda\b",
        "\bwebhook\b",
        "\blive trading\b",
        "\bmoney movement\b",
        "\bplace\b.*\border\b",
        "\border\b.*\bplacement\b",
        "\breal money\b"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Broker/OANDA/webhook/order/live-trading/money movement language detected.")
}

if (Has-Pattern -Text $scanBlob -Patterns @(
        "\bdelete\b",
        "\bremove\b",
        "\boverwrite\b",
        "\breset\b",
        "\bpurge\b",
        "\bforce\s+push\b",
        "\btruncate\b"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Destructive change intent (delete/overwrite/reset/force-push) detected.")
}

if (Has-Pattern -Text $scanBlob -Patterns @(
        "\bruntime\b",
        "\bworker\b",
        "\bscheduler\b",
        "\bdaemon\b",
        "\blaunch\b"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Runtime/worker/scheduler/daemon launch intent detected.")
}

if (Has-Pattern -Text $scanBlob -Patterns @(
        "\bapproval inbox\b",
        "\bapproval inbox mutation\b",
        "\bqueue\b.*\bmutation\b",
        "\block\b.*\bmutation\b"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Approval inbox/queue/lock mutation without bounded packet scope detected.")
}

if (Has-Pattern -Text $scanBlob -Patterns @(
        "\bfailed recovery\b",
        "\brecovery failed\b",
        "\bambiguous authority\b"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Failed recovery or ambiguous authority condition detected.")
}

if (Has-Pattern -Text $scanBlob -Patterns @(
        "\bsecurity alert\b",
        "\bsecurity incident\b"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Security alert language detected.")
}

if (Has-Pattern -Text $scanBlob -Patterns @(
        "\blegal\b.*\bdecision\b",
        "\bbusiness decision\b",
        "\bcontract\b.*\brequired\b"
    )) {
    $hasEscalation = $true
    $escalationReasons.Add("Legal or business decision requiring Anthony detected.")
}

if ((-not $hasEscalation) -and ($escalationReasons.Count -eq 0)) {
    $escalationReasons.Add("No SOS escalation conditions matched.")
}

if ($status -eq "READY") {
    $escalationStatus = "NO_REVIEW_NEEDED"
    $safeNextAction = "No SOS escalation needed; continue routine operator flow."
    $anthonyRequired = $false
    $routineReviewAllowed = $false
}
elseif ([string]::IsNullOrWhiteSpace($status) -or $status -eq "EMPTY") {
    $resolverReason = if ($resolverHasOutput) { To-SafeText ($resolverOutput.why_human_review_needed) } else { "" }
    if ([string]::IsNullOrWhiteSpace($resolverReason)) {
        $escalationStatus = "NO_REVIEW_NEEDED"
        $safeNextAction = "No review context is present; continue governed routine flow."
        $anthonyRequired = $false
        $routineReviewAllowed = $false
    }
    else {
        $escalationStatus = "ROUTINE_REVIEW"
        $safeNextAction = "No SOS conditions found for this relay review; continue routine operator routing."
        $anthonyRequired = $false
        $routineReviewAllowed = $true
    }
}
elseif ($hasEscalation) {
    $escalationStatus = "SOS_ESCALATION"
    $safeNextAction = "Route this relay review for Anthony escalation before any continuation."
    $anthonyRequired = $true
    $routineReviewAllowed = $false
}
else {
    $escalationStatus = "ROUTINE_REVIEW"
    $safeNextAction = "This is routine relay review; continue through governed review flow."
    $anthonyRequired = $false
    $routineReviewAllowed = $true
}

$result = [ordered]@{
    schema = "AIOS_SOS_ESCALATION_POLICY.v1"
    mode = "DRY_RUN_READ_ONLY"
    writes_files = $false
    execution_allowed = $false
    can_continue_without_anthony = $false
    escalation_status = $escalationStatus
    escalation_reasons = @($escalationReasons)
    safe_next_action = $safeNextAction
    anthony_required = $anthonyRequired
    routine_review_allowed = $routineReviewAllowed
}

if ($OutputJson) {
    $result | ConvertTo-Json -Depth 20
}
else {
    $result | ConvertTo-Json -Depth 20
}
