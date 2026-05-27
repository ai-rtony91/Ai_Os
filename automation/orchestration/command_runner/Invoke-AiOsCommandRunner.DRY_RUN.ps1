[CmdletBinding()]
param(
    [string]$CommandRequestPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-AiOsSampleCommandRequest {
    [pscustomobject]@{
        schema = "AIOS_COMMAND_REQUEST.v1"
        command_id = "CMD-PREVIEW-SAMPLE"
        packet_id = "PKT-PREVIEW-SAMPLE"
        requester = "EAST_OCC_01"
        supervisor = "Codex East"
        lane = "autonomy runtime mega-pack"
        worker = "EAST_OCC_01"
        cwd = "C:\Dev\Ai.Os"
        command_preview = "git status --short --branch"
        command_class = "READ_ONLY"
        autonomy_level = "LEVEL_1_AUTO_READ_ONLY"
        approval_required = $false
        approval_token_required = $null
        approval_token_status = "NOT_REQUIRED"
        timeout_seconds = 30
        allowed_paths = @("C:\Dev\Ai.Os")
        blocked_paths = @("secrets", ".env", "broker", "OANDA", "webhook", "live orders")
        dry_run_first = $true
        stdout_path = $null
        stderr_path = $null
        exit_code = $null
        result = "REQUESTED"
        receipt_id = $null
        telemetry_event_id = $null
        stop_point = "Stop after preview. Do not execute commands."
        created_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        expires_at = $null
    }
}

function Get-AiOsCommandRequest {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return [pscustomobject]@{
            source = "sample"
            status = "SAMPLE_USED"
            request = (New-AiOsSampleCommandRequest)
            error = ""
        }
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            source = $Path
            status = "MISSING"
            request = $null
            error = "Command request file not found."
        }
    }

    try {
        $request = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
        return [pscustomobject]@{
            source = $Path
            status = "FOUND"
            request = $request
            error = ""
        }
    }
    catch {
        return [pscustomobject]@{
            source = $Path
            status = "INVALID_JSON"
            request = $null
            error = $_.Exception.Message
        }
    }
}

function Test-AiOsBlockedCommand {
    param([string]$Command)

    $patterns = @(
        "(?i)\b(remove|delete|del|rm|rmdir)\b",
        "(?i)\b(move|rename|mv)\b",
        "(?i)^git\s+reset\s+--hard\b",
        "(?i)^git\s+clean\b",
        "(?i)\b(npm|pnpm|yarn|pip|pipx|choco|winget|docker)\s+(install|add|run|compose|build)\b",
        "(?i)\b(az|azure)\s+",
        "(?i)\b(secret|credential|token|password|\.env|id_rsa|keyvault|bitwarden)\b",
        "(?i)\b(broker|oanda|trading|webhook|live\s*order|real\s*order)\b",
        "(?i)^gh\s+pr\s+merge\b",
        "(?i)^git\s+push\b",
        "(?i)^powershell\b.*-File\s+(?!.*\.DRY_RUN\.ps1\b)",
        "(?i)^pwsh\b.*-File\s+(?!.*\.DRY_RUN\.ps1\b)",
        "(?i)^&\s+.*\.ps1\b"
    )

    foreach ($pattern in $patterns) {
        if ($Command -match $pattern) {
            return $true
        }
    }

    return $false
}

function Test-AiOsAllowlistedCommand {
    param([string]$Command)

    $allowPatterns = @(
        "^git status($|\s+--short\s+--branch$)",
        "^git diff --check$",
        "^git diff --cached --check$",
        "^git diff --cached --name-only$",
        "^gh pr view \d+\b",
        "^gh pr checks \d+\b",
        "^Test-Path\s+",
        "^Get-Content\s+",
        "^powershell\s+-NoProfile\s+-ExecutionPolicy\s+Bypass\s+-File\s+automation/.+\.DRY_RUN\.ps1\b",
        "^powershell\s+-ExecutionPolicy\s+Bypass\s+-File\s+automation/.+\.DRY_RUN\.ps1\b",
        "^\.\\aios\.ps1\s+-Mode\s+(help|status|control|finish-pr|hud|supervisor|runner|queue|telemetry)\b"
    )

    foreach ($pattern in $allowPatterns) {
        if ($Command -match $pattern) {
            return $true
        }
    }

    return $false
}

$requestState = Get-AiOsCommandRequest -Path $CommandRequestPath
$request = $requestState.request
$command = if ($request) { [string]$request.command_preview } else { "" }
$isBlocked = if ([string]::IsNullOrWhiteSpace($command)) { $true } else { Test-AiOsBlockedCommand -Command $command }
$isAllowlisted = if ($isBlocked) { $false } else { Test-AiOsAllowlistedCommand -Command $command }
$classification = if ($requestState.status -eq "INVALID_JSON" -or $requestState.status -eq "MISSING") {
    "BLOCKED"
}
elseif ($isBlocked) {
    "BLOCKED"
}
elseif ($isAllowlisted) {
    "ALLOWLISTED_PREVIEW"
}
else {
    "BLOCKED"
}

$preview = [pscustomobject]@{
    schema = "AIOS_COMMAND_RUNNER_PREVIEW.v1"
    mode = "DRY_RUN"
    execution_enabled = $false
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    request_source = $requestState.source
    request_status = $requestState.status
    command_id = if ($request) { $request.command_id } else { $null }
    packet_id = if ($request) { $request.packet_id } else { $null }
    command_preview = $command
    classification = $classification
    allowlisted = $isAllowlisted
    blocked = ($classification -eq "BLOCKED")
    blocked_actions = @(
        "arbitrary shell",
        "remove/delete",
        "move/rename",
        "git reset --hard",
        "git clean",
        "installs",
        "cloud provisioning",
        "secret access",
        "broker/OANDA/trading/webhook/live orders",
        "merge execution",
        "push execution",
        "unknown scripts"
    )
    files_changed_by_runner = @()
    approvals_mutated = $false
    queues_mutated = $false
    stdout_path = $null
    stderr_path = $null
    exit_code = $null
    next_safe_action = if ($classification -eq "ALLOWLISTED_PREVIEW") {
        "Review preview only. A separate approved runner is required before execution."
    } else {
        "Stop. Command is missing, invalid, blocked, or not allowlisted."
    }
    error = $requestState.error
}

if ($OutputJson) {
    $preview | ConvertTo-Json -Depth 10
    exit 0
}

Write-Host "AI_OS Command Runner Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($preview.schema)"
Write-Host "Execution enabled: $($preview.execution_enabled)"
Write-Host "Command: $($preview.command_preview)"
Write-Host "Classification: $($preview.classification)"
Write-Host "Allowlisted: $($preview.allowlisted)"
Write-Host "Next safe action: $($preview.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
