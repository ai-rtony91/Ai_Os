Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$docPath = Join-Path $repoRoot "docs\AI_OS\trading_laboratory\phase_14_4\PHASE_14_4_SUPERTREND_MVP_SIGNAL_PREVIEW.md"
$previewPath = Join-Path $repoRoot "docs\AI_OS\trading_laboratory\phase_14_4\PHASE_14_4_SUPERTREND_SIGNAL_PREVIEW_001.json"

function Read-JsonFile {
    param(
        [Parameter(Mandatory = $true)]
        [string] $Path
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "Missing JSON file: $Path"
    }

    return Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
}

function Assert-Property {
    param(
        [Parameter(Mandatory = $true)]
        [AllowNull()]
        [object] $Object,
        [Parameter(Mandatory = $true)]
        [string] $Name
    )

    if (-not ($Object.PSObject.Properties.Name -contains $Name)) {
        throw "Missing required field: $Name"
    }
}

function Assert-BlockedAction {
    param(
        [Parameter(Mandatory = $true)]
        [object] $Preview,
        [Parameter(Mandatory = $true)]
        [string] $Action
    )

    if ($Preview.blocked_actions -notcontains $Action) {
        throw "Missing blocked action: $Action"
    }
}

function Assert-NoProhibitedFields {
    param(
        [Parameter(Mandatory = $true)]
        [AllowNull()]
        [object] $Object,
        [string[]] $Path = @()
    )

    $prohibited = @("broker", "OANDA", "api_key", "webhook_url", "live_order", "order_id", "account_id", "real_execution")
    if ($null -eq $Object) {
        return
    }
    if ($Object -is [System.Array]) {
        for ($index = 0; $index -lt $Object.Count; $index++) {
            Assert-NoProhibitedFields -Object $Object[$index] -Path ($Path + "[$index]")
        }
        return
    }
    if ($Object.PSObject.Properties) {
        foreach ($property in $Object.PSObject.Properties) {
            if ($prohibited -contains $property.Name) {
                throw "Prohibited field found: $(($Path + $property.Name) -join '.')"
            }
            Assert-NoProhibitedFields -Object $property.Value -Path ($Path + $property.Name)
        }
    }
}

if (-not (Test-Path -LiteralPath $docPath)) {
    throw "Missing SuperTrend preview document: $docPath"
}

$preview = Read-JsonFile -Path $previewPath
Assert-NoProhibitedFields -Object $preview

foreach ($field in @(
    "preview_id",
    "phase",
    "mode",
    "execution_allowed",
    "live_execution_status",
    "strategy_component",
    "component_role",
    "strategy_permission_status",
    "trend_permission",
    "direction_intent",
    "confidence_placeholder",
    "blocked_reason",
    "regime_note",
    "not_a_trigger",
    "allowed_outputs",
    "supertrend_output",
    "signal_intake",
    "latency",
    "phase_14_3_decision_engine",
    "scorecard",
    "preview_result",
    "blocked_actions",
    "safety_confirmation"
)) {
    Assert-Property -Object $preview -Name $field
}

if ($preview.mode -ne "paper_only_simulation") {
    throw "SuperTrend preview mode must be paper_only_simulation."
}

if ($preview.execution_allowed -eq $true) {
    throw "execution_allowed must not be true."
}

if ($preview.live_execution_status -ne "BLOCKED") {
    throw "live_execution_status must remain BLOCKED."
}

if ($preview.component_role -ne "trend_permission_only") {
    throw "SuperTrend component_role must be trend_permission_only."
}

if ($preview.strategy_permission_status -notin @("allowed_for_paper_review", "blocked", "insufficient_data")) {
    throw "strategy_permission_status must be allowed_for_paper_review, blocked, or insufficient_data."
}

if ($preview.trend_permission -notin @("bullish", "bearish", "neutral", "blocked")) {
    throw "trend_permission must be bullish, bearish, neutral, or blocked."
}

if ($preview.trend_permission -ne $preview.supertrend_output) {
    throw "trend_permission must match supertrend_output."
}

if (-not [string]::IsNullOrWhiteSpace($preview.direction_intent) -and $preview.direction_intent -notmatch "_REVIEW$") {
    throw "direction_intent must end with _REVIEW."
}

if ([string]::IsNullOrWhiteSpace($preview.direction_intent)) {
    throw "direction_intent must exist."
}

if ([string]::IsNullOrWhiteSpace($preview.confidence_placeholder)) {
    throw "confidence_placeholder must exist."
}

if ($preview.confidence_placeholder -match "(?i)\b(execute|execution|order|route|trigger|live)\b") {
    throw "confidence_placeholder must not imply execution."
}

if ($null -eq $preview.blocked_reason) {
    throw "blocked_reason must exist."
}

if ($preview.strategy_permission_status -eq "blocked" -and [string]::IsNullOrWhiteSpace($preview.blocked_reason)) {
    throw "blocked strategy permission requires blocked_reason."
}

if ([string]::IsNullOrWhiteSpace($preview.regime_note)) {
    throw "regime_note must exist."
}

if ($preview.not_a_trigger -ne $true) {
    throw "SuperTrend must be marked as not_a_trigger."
}

foreach ($output in @("bullish", "bearish", "neutral", "blocked")) {
    if ($preview.allowed_outputs -notcontains $output) {
        throw "Missing allowed SuperTrend output: $output"
    }
}

if ($preview.allowed_outputs -notcontains $preview.supertrend_output) {
    throw "supertrend_output must be one of the allowed outputs."
}

if ($preview.preview_result.status -ne $preview.supertrend_output) {
    throw "preview_result.status must match supertrend_output."
}

foreach ($field in @("signal_id", "source", "symbol", "timeframe", "direction", "signal_type", "paper_only")) {
    Assert-Property -Object $preview.signal_intake -Name $field
}

if ($preview.signal_intake.paper_only -ne $true) {
    throw "Signal intake must remain paper_only."
}

foreach ($field in @("latency_id", "latency_seconds", "stale_status", "clock_skew_status", "latency_source")) {
    Assert-Property -Object $preview.latency -Name $field
}

foreach ($field in @("decision_result_id", "decision_result", "decision_engine_role", "supertrend_can_override_decision_engine")) {
    Assert-Property -Object $preview.phase_14_3_decision_engine -Name $field
}

if ($preview.phase_14_3_decision_engine.decision_engine_role -ne "final paper decision authority") {
    throw "Phase 14.3 decision engine must remain final paper decision authority."
}

if ($preview.phase_14_3_decision_engine.supertrend_can_override_decision_engine -ne $false) {
    throw "SuperTrend must not override the Phase 14.3 decision engine."
}

foreach ($field in @("scorecard_id", "evidence_score", "scorecard_status", "scorecard_note")) {
    Assert-Property -Object $preview.scorecard -Name $field
}

if ($preview.preview_result.approved_for_live_execution -ne $false) {
    throw "SuperTrend preview must not approve live execution."
}

foreach ($action in @(
    "external_execution",
    "credential_use",
    "route_delivery",
    "paper_to_live_conversion",
    "live_trading",
    "automatic_route_execution"
)) {
    Assert-BlockedAction -Preview $preview -Action $action
}

foreach ($field in @(
    "paper_only",
    "live_execution_status",
    "external_connection_status",
    "credential_status",
    "route_delivery_status",
    "order_delivery_status"
)) {
    Assert-Property -Object $preview.safety_confirmation -Name $field
}

if ($preview.safety_confirmation.paper_only -ne $true) {
    throw "Safety confirmation must keep paper_only true."
}

foreach ($field in @("live_execution_status", "external_connection_status", "credential_status", "route_delivery_status", "order_delivery_status")) {
    if ($preview.safety_confirmation.$field -ne "BLOCKED") {
        throw "Safety field $field must remain BLOCKED."
    }
}

Write-Output "PASS: Phase 14.4 SuperTrend MVP signal preview DRY_RUN validation passed."
Write-Output "SuperTrend is trend permission only, not a buy/sell trigger."
Write-Output "Connected to signal intake, latency, Phase 14.3 decision engine, and scorecard."
Write-Output "Live trading and all external execution paths remain BLOCKED."
