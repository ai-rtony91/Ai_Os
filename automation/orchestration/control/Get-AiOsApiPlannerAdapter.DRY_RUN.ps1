[CmdletBinding()]
param(
    [string]$FixturePath = "inputs/morning_brief_fixture.txt",
    [switch]$OutputJson
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-AiOsFixtureState {
    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return [pscustomobject]@{
            status = "MISSING"
            path = $Path
            exists = $false
            read_as_evidence_only = $true
            text = ""
            line_count = 0
        }
    }

    $text = Get-Content -LiteralPath $Path -Raw
    return [pscustomobject]@{
        status = "FOUND"
        path = $Path
        exists = $true
        read_as_evidence_only = $true
        text = $text
        line_count = @($text -split "`r?`n").Count
    }
}

function Get-AiOsPlannerMode {
    param([string]$Text)

    if ($Text -match "(?i)\b(API keys?|\.env|secrets?|broker|OANDA|live trading|webhook|real orders?)\b") {
        return "HARD_GATE_REQUIRED"
    }

    if ($Text -match "(?i)\b(commit|push|PR|pull request)\b") {
        return "CONTROLLER_PREVIEW_REQUIRED"
    }

    if ($Text -match "(?i)\b(create|build|add|write|generate)\b") {
        return "APPLY_PREVIEW_REQUIRED"
    }

    return "DRY_RUN"
}

function Get-AiOsFirstMeaningfulLine {
    param([string]$Text)

    $line = @($Text -replace "`r", "" -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
    if ($line.Count -eq 0) {
        return "No fixture objective supplied."
    }

    return [string]$line[0].Trim()
}

$fixtureState = Get-AiOsFixtureState -Path $FixturePath
$fixtureText = if ($fixtureState.exists) { $fixtureState.text } else { "" }
$mode = Get-AiOsPlannerMode -Text $fixtureText
$objective = Get-AiOsFirstMeaningfulLine -Text $fixtureText

$plannerPreview = [pscustomobject]@{
    schema = "AIOS_PLANNER_PROMPT_PREVIEW.v1"
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        preview_only = $true
        no_runtime_authority = $true
        no_execution_authority = $true
        no_api_calls = $true
        no_network = $true
        no_env = $true
        governance_reference = "docs/governance/AI_OS_AUTONOMY_LEVELS.md"
    }
    autonomy_level = "Level 1 - AUTO READ-ONLY / Level 2 - AUTO REPORT / PREVIEW FILES"
    execution_enabled = $false
    brief_input = [pscustomobject]@{
        source = $fixtureState.path
        state = $fixtureState.status
        read_as_evidence_only = $true
    }
    inferred_objective = $objective
    proposed_packet_id = "PKT-EAST-API-PLANNER-PREVIEW-001"
    proposed_lane = "api planner preview"
    proposed_mode = $mode
    allowed_paths_preview = @(
        "docs/workflows/",
        "inputs/",
        "schemas/aios/orchestration/",
        "automation/orchestration/control/"
    )
    forbidden_paths_preview = @(
        "apps/",
        "services/",
        "automation/loop_engine.py",
        "broker/OANDA/live trading/webhook/secrets/.env",
        "docs/AI_OS/llm/"
    )
    approval_requirements = @(
        "Human review required before any APPLY packet.",
        "APPROVE_COMMIT required before future staging or commit.",
        "APPROVE_PUSH required before future push.",
        "APPROVE_PR_CREATE required before future PR creation.",
        "Merge requires separate explicit human approval."
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
        "broker/OANDA/live trading/webhook/secrets/dashboard scope"
    )
    stop_conditions = @(
        "Fixture missing is allowed but marked MISSING.",
        "Any request for real API calls stops this adapter.",
        "Any request for credentials, secrets, .env files, broker, OANDA, live trading, webhooks, or real orders requires a hard gate.",
        "Any request for staging, commit, push, PR creation, or merge requires separate approval and must not execute here."
    )
    next_safe_action = if ($mode -eq "HARD_GATE_REQUIRED") {
        "Stop and request a dedicated hard-gate review packet."
    }
    else {
        "Review the planner preview as evidence only."
    }
}

$packet = [pscustomobject]@{
    schema = "AIOS_API_PLANNER_ADAPTER_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        fixture_only = $true
        no_api_calls = $true
        no_network = $true
        no_env = $true
        no_subprocess = $true
        no_execution_authority = $true
        allowed_autonomy_levels = @("Level 1 - AUTO READ-ONLY", "Level 2 - AUTO REPORT / PREVIEW FILES")
    }
    execution_enabled = $false
    fixture_state = [pscustomobject]@{
        status = $fixtureState.status
        path = $fixtureState.path
        exists = $fixtureState.exists
        read_as_evidence_only = $fixtureState.read_as_evidence_only
        line_count = $fixtureState.line_count
    }
    planner_preview = $plannerPreview
    blocked_actions = $plannerPreview.blocked_actions
    stop_conditions = $plannerPreview.stop_conditions
    next_safe_action = $plannerPreview.next_safe_action
}

if ($OutputJson) {
    $packet | ConvertTo-Json -Depth 14
    exit 0
}

Write-Host "AI_OS API Planner Adapter Preview"
Write-Host "Mode: DRY_RUN"
Write-Host "Schema: $($packet.schema)"
Write-Host "Fixture state: $($packet.fixture_state.status)"
Write-Host "Planner mode: $($packet.planner_preview.proposed_mode)"
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
