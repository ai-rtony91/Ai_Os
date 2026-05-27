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
        $Path = "inputs/morning_brief_fixture.txt"
    }

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

function Get-AiOsBriefMode {
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

    if ($Text -match "(?i)\b(inspect|review|reassess|check|audit|validate)\b") {
        return "DRY_RUN"
    }

    return "DRY_RUN"
}

function Get-AiOsLane {
    param([string]$Text)

    if ($Text -match "(?i)\b(API|Tasker|Azure|Bitwarden|OpenAI|Claude|planner)\b") {
        return "api integration safety preview"
    }

    if ($Text -match "(?i)\b(commit|push|PR|pull request)\b") {
        return "commit push PR controller"
    }

    if ($Text -match "(?i)\b(morning brief|brief|packet)\b") {
        return "morning brief packet preview"
    }

    return "stage 2 foundation"
}

function Get-AiOsObjective {
    param([string]$Text)

    $normalized = ($Text -replace "`r", "" -split "`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return "No brief objective supplied."
    }

    return $normalized.Trim()
}

$briefState = Get-AiOsBriefState -Path $BriefPath
$briefText = if ($briefState.exists) { $briefState.text } else { "" }
$mode = Get-AiOsBriefMode -Text $briefText
$lane = Get-AiOsLane -Text $briefText
$objective = Get-AiOsObjective -Text $briefText
$safePacketStem = ($lane -replace "[^A-Za-z0-9]+", "-").Trim("-").ToUpperInvariant()
if ([string]::IsNullOrWhiteSpace($safePacketStem)) {
    $safePacketStem = "STAGE2"
}

$packet = [pscustomobject]@{
    schema = "AIOS_MORNING_BRIEF_PACKET_PREVIEW.v1"
    mode = "DRY_RUN"
    generated_at = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    authority_boundary = [pscustomobject]@{
        execution_enabled = $false
        allowed_autonomy_levels = @("Level 1 - AUTO READ-ONLY", "Level 2 - AUTO REPORT / PREVIEW FILES")
        blocked_autonomy_levels = @("Level 3 - AUTO PREP", "Level 4 - APPROVED EXECUTION", "Level 5 - HARD GATE")
        governance_reference = "docs/governance/AI_OS_AUTONOMY_LEVELS.md"
        preview_only = $true
        no_runtime_authority = $true
        no_execution_authority = $true
    }
    autonomy_levels_referenced = @("Level 1 - AUTO READ-ONLY", "Level 2 - AUTO REPORT / PREVIEW FILES")
    execution_enabled = $false
    brief_state = [pscustomobject]@{
        status = $briefState.status
        path = $briefState.path
        exists = $briefState.exists
        read_as_evidence_only = $briefState.read_as_evidence_only
        line_count = $briefState.line_count
    }
    inferred_objective = $objective
    recommended_lane = $lane
    recommended_mode = $mode
    proposed_packet_id = "PKT-EAST-$safePacketStem-PREVIEW-001"
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
    validator_preview = @(
        "git diff --check",
        "Get-Content schemas/aios/orchestration/planner_prompt_schema.json | ConvertFrom-Json | Out-Null",
        "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsApiPlannerAdapter.DRY_RUN.ps1 -OutputJson",
        "powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsApprovalGatedHandoff.DRY_RUN.ps1 -OutputJson"
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
        "Any request for real API calls stops this preview.",
        "Any request for approval mutation or queue mutation stops this preview.",
        "Any request for staging, commit, push, PR creation, or merge stops this preview.",
        "Any Level 5 scope requires a separate explicit human-approved packet."
    )
    next_safe_action = if ($mode -eq "HARD_GATE_REQUIRED") {
        "Stop and request a dedicated hard-gate packet with explicit human approval."
    }
    elseif ($mode -eq "CONTROLLER_PREVIEW_REQUIRED") {
        "Route to commit/push/PR controller preview only."
    }
    else {
        "Review the packet preview before any scoped APPLY packet."
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
Write-Host "Next safe action: $($packet.next_safe_action)"
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
