[CmdletBinding()]
param(
    [string]$BriefPath = "",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsBriefState {
    param([string]$Path)

    if ([string]::IsNullOrWhiteSpace($Path)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = ""
            exists = $false
            read_as_evidence_only = $true
            text = ""
            preview = @()
        }
    }

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = $Path
            exists = $false
            read_as_evidence_only = $true
            text = ""
            preview = @()
        }
    }

    $text = Get-Content -LiteralPath $Path -Raw
    $lines = @($text -split "`r?`n")
    return [pscustomobject]@{
        status = "FOUND"
        path = $Path
        exists = $true
        read_as_evidence_only = $true
        text = $text
        preview = @($lines | Select-Object -First 20)
    }
}

function Get-AiOsFirstMeaningfulLine {
    param([string]$Text)

    $lines = @($Text -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
    if ($lines.Count -eq 0) {
        return "No morning brief supplied."
    }

    return $lines[0].Trim()
}

function Get-AiOsPacketIdSuffix {
    param([string]$Text)

    $words = @(([regex]::Matches($Text.ToUpperInvariant(), "[A-Z0-9]+") | ForEach-Object { $_.Value }) | Select-Object -First 6)
    if ($words.Count -eq 0) {
        return "NO-BRIEF"
    }

    return ($words -join "-")
}

$briefState = Get-AiOsBriefState -Path $BriefPath
$briefText = if ($briefState.exists) { [string]$briefState.text } else { "" }
$lowerBrief = $briefText.ToLowerInvariant()

$hardGatePattern = "(api keys?|\.env|secrets?|credentials?|broker|oanda|live trading|webhooks?|real orders?)"
$commitPushPrPattern = "\b(commit|push|pr)\b|pull request"
$applyPreviewPattern = "\b(create|build|add)\b"
$dryRunPattern = "\b(inspect|review|reassess|check)\b"

$hasHardGate = $lowerBrief -match $hardGatePattern
$hasCommitPushPr = $lowerBrief -match $commitPushPrPattern
$hasApplyPreview = $lowerBrief -match $applyPreviewPattern
$hasDryRun = $lowerBrief -match $dryRunPattern

$recommendedMode = "DRY_RUN"
$recommendedLane = "inspection preview"
if ($hasHardGate) {
    $recommendedMode = "HARD_GATE_REQUIRED"
    $recommendedLane = "human approval hard gate"
}
elseif ($hasCommitPushPr) {
    $recommendedMode = "CONTROLLER_PREVIEW_REQUIRED"
    $recommendedLane = "commit push PR controller preview"
}
elseif ($hasApplyPreview) {
    $recommendedMode = "APPLY_PREVIEW_REQUIRED"
    $recommendedLane = "scoped APPLY preview"
}
elseif ($hasDryRun) {
    $recommendedMode = "DRY_RUN"
    $recommendedLane = "read-only inspection"
}

$inferredObjective = Get-AiOsFirstMeaningfulLine -Text $briefText
$proposedPacketId = "PKT-PREVIEW-" + (Get-AiOsPacketIdSuffix -Text $briefText)

$packet = [pscustomobject]@{
    schema = "AIOS_MORNING_BRIEF_PACKET_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        local_rule_based_parsing_only = $true
        governance_reference = "docs/governance/AI_OS_AUTONOMY_LEVELS.md"
        no_bypass = "Does not override AGENTS.md, README.md, security policy, branch protection, trading safety, packet scope, or human approval gates."
    }
    autonomy_levels_referenced = @(
        "Level 1 - AUTO READ-ONLY",
        "Level 2 - AUTO REPORT / PREVIEW FILES"
    )
    execution_enabled = $false
    brief_state = [pscustomobject]@{
        status = $briefState.status
        path = $briefState.path
        exists = $briefState.exists
        read_as_evidence_only = $briefState.read_as_evidence_only
        preview = @($briefState.preview)
    }
    inferred_objective = $inferredObjective
    recommended_lane = $recommendedLane
    recommended_mode = $recommendedMode
    proposed_packet_id = $proposedPacketId
    allowed_paths_preview = if ($recommendedMode -eq "DRY_RUN") {
        @("read-only repo evidence", "approved DRY_RUN helper output")
    }
    else {
        @("to be supplied by human-approved packet")
    }
    forbidden_paths_preview = @(
        "AGENTS.md",
        "README.md",
        "RISK_POLICY.md",
        "schemas/",
        "apps/",
        "services/",
        "broker/",
        "OANDA/",
        "live trading",
        "webhook",
        "secrets",
        "automation/loop_engine.py"
    )
    validator_preview = @(
        "git diff --check",
        "controller preview validation",
        "human scope review before any APPLY or protected action"
    )
    blocked_actions = @(
        "automation/loop_engine.py",
        "API key usage",
        ".env usage",
        "external model API calls",
        "Codex subprocess execution",
        "scheduled/background loops",
        "auto APPLY",
        "auto commit",
        "auto push",
        "auto PR create",
        "auto merge",
        "worker launch",
        "queue mutation",
        "approval mutation",
        "staging",
        "commit",
        "push",
        "PR creation",
        "merge",
        "broker/OANDA/live trading/webhook/secrets/dashboard scope"
    )
    stop_conditions = @(
        "Brief missing is allowed and remains MISSING.",
        "Hard-gate terms require separate human approval.",
        "Commit, push, or PR language routes to controller preview only.",
        "Create/build/add language becomes APPLY_PREVIEW_REQUIRED, not APPLY execution.",
        "Unclear brief defaults to DRY_RUN and safer level."
    )
    next_safe_action = if ($recommendedMode -eq "HARD_GATE_REQUIRED") {
        "Stop and request a dedicated human-approved hard-gate packet."
    }
    elseif ($recommendedMode -eq "CONTROLLER_PREVIEW_REQUIRED") {
        "Route to commit/push/PR controller preview; do not execute protected commands."
    }
    elseif ($recommendedMode -eq "APPLY_PREVIEW_REQUIRED") {
        "Draft a scoped APPLY preview packet for human review."
    }
    else {
        "Proceed with read-only DRY_RUN inspection or request a clearer brief."
    }
}

if ($OutputJson) {
    $packet | ConvertTo-Json -Depth 12
    exit 0
}

Write-Host "AI_OS Morning Brief Packet Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($packet.schema)"
Write-Host "Brief state: $($packet.brief_state.status)"
Write-Host "Recommended mode: $($packet.recommended_mode)"
Write-Host "Recommended lane: $($packet.recommended_lane)"
Write-Host "Execution enabled: $($packet.execution_enabled)"
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
