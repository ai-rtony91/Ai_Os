param(
    [Parameter(Mandatory = $true)][string]$PacketId,
    [string]$ReviewedPowerShellText = "",
    [string]$ReviewedPowerShellPath = "",
    [ValidateSet("DRY_RUN", "APPLY")][string]$Mode = "DRY_RUN",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Read-PastebackText {
    param([string]$Text, [string]$Path)
    if (-not [string]::IsNullOrWhiteSpace($Text)) {
        return $Text
    }
    if ([string]::IsNullOrWhiteSpace($Path)) {
        return ""
    }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "ReviewedPowerShellPath not found: $Path"
    }
    return Get-Content -LiteralPath $Path -Raw
}

function Has-SecretLikeText {
    param([string]$Text)
    $patterns = @(
        "AIOS_TG_BOT_TOKEN",
        "AIOS_TG_CHAT_ID",
        "AKIA",
        "xoxb-",
        "ghp_",
        "token=",
        "api_key",
        "secret=",
        "oauth_token"
    )
    foreach ($pattern in $patterns) {
        if ($Text -match [regex]::Escape($pattern)) {
            return $true
        }
    }
    return $false
}

function Contains-BadCommands {
    param([string]$Text)
    $bad = @(
        "git push --force",
        "git push -f",
        "git add .",
        "start-process",
        "git commit ",
        "git clean",
        "git reset --hard",
        "rm -rf",
        "runtime",
        "queue",
        "approval_inbox",
        "workers",
        "scheduler",
        "daemon",
        "telemetry",
        "cloudflare",
        "backup",
        "lock"
    )
    foreach ($token in $bad) {
        if ($Text -match [regex]::Escape($token)) {
            return $token
        }
    }
    return ""
}

$repoRoot = (Get-Location).Path
$pastebackDir = Join-Path $repoRoot "control/review_bridge/pasteback"

$reviewText = Read-PastebackText -Text $ReviewedPowerShellText -Path $ReviewedPowerShellPath
$trimmed = ($reviewText | Out-String).Trim()

$badCommand = Contains-BadCommands -Text $trimmed
$containsSecret = Has-SecretLikeText -Text $trimmed

$blockedActions = @()
$safetyPassed = $true
$reason = ""

if ([string]::IsNullOrWhiteSpace($PacketId)) {
    $blockedActions += "Missing packet id."
    $safetyPassed = $false
    $reason = "Blocked: packet id missing."
}
if ([string]::IsNullOrWhiteSpace($trimmed)) {
    $blockedActions += "Missing reviewed command block."
    $safetyPassed = $false
    $reason = "Blocked: no reviewed command text."
}
if ($containsSecret) {
    $blockedActions += "Potential secret token in reviewed command."
    $safetyPassed = $false
    $reason = "Blocked: potential secrets found."
}
if ($badCommand) {
    $blockedActions += "Unsafe command pattern: $badCommand"
    $safetyPassed = $false
    $reason = "Blocked: unsafe command detected."
}

$requiresManualExecution = $true

$fileName = ("pasteback_{0}_{1}.json" -f ($PacketId -replace "[^A-Za-z0-9._-]", "_"), (Get-Date).ToString("yyyy-MM-ddTHH-mm-ssZ"))
$pastebackPath = Join-Path $pastebackDir $fileName

$output = [ordered]@{
    schema = "AIOS_CODEX_PASTEBACK_ITEM.v1"
    mode = if ($Mode -eq "APPLY") { "APPLY" } else { "DRY_RUN_READ_ONLY" }
    packet_id = $PacketId
    pasteback_file = $pastebackPath
    writes_files = ($Mode -eq "APPLY")
    safety_scan_passed = $safetyPassed
    blocked_actions = @($blockedActions)
    exact_next_safe_action = if ($safetyPassed) {
        "No automatic execution in AI_OS. Paste the reviewed command manually in PowerShell."
    } else {
        "Fix safety issues in reviewed command, keep writeable artifact in DRY_RUN first."
    }
    reason = $reason
}

if ($Mode -eq "APPLY" -and $safetyPassed) {
    if (-not (Test-Path -LiteralPath $pastebackDir -PathType Container)) {
        New-Item -ItemType Directory -Path $pastebackDir -Force | Out-Null
    }
    $artifact = [ordered]@{
        packet_id = $PacketId
        timestamp = (Get-Date).ToString("o")
        reviewed_power_shell_text = $trimmed
        safety_scan_passed = $true
        requires_manual_execution = $requiresManualExecution
        blocked_checks = @($blockedActions)
    }
    $utf8NoBOM = New-Object System.Text.UTF8Encoding($false)
    $jsonPayload = $artifact | ConvertTo-Json -Depth 20
    [System.IO.File]::WriteAllText($pastebackPath, $jsonPayload, $utf8NoBOM)
} else {
    $output.reviewed_power_shell_text_preview = $trimmed
}

if ($OutputJson) {
    $output | ConvertTo-Json -Depth 20
    exit 0
}

Write-Output ($output | ConvertTo-Json -Depth 20)
