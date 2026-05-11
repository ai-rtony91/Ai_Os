Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$decisionPath = Join-Path $repoRoot "docs\AI_OS\trading_laboratory\phase_14_3\PHASE_14_3_DECISION_RESULT_001.json"

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
        [object] $Decision,
        [Parameter(Mandatory = $true)]
        [string] $Action
    )

    if ($Decision.blocked_actions -notcontains $Action) {
        throw "Missing blocked action: $Action"
    }
}

$decision = Read-JsonFile -Path $decisionPath

foreach ($field in @(
    "decision_id",
    "mode",
    "live_execution_status",
    "execution_allowed",
    "approved_for_live_execution",
    "decision_result",
    "allowed_decision_results",
    "source_trace",
    "decision_inputs",
    "decision_rules",
    "blocked_actions",
    "safety_confirmation"
)) {
    Assert-Property -Object $decision -Name $field
}

if ($decision.mode -ne "paper_only_simulation") {
    throw "Decision mode must be paper_only_simulation."
}

if ($decision.live_execution_status -ne "BLOCKED") {
    throw "Live execution status must remain BLOCKED."
}

if ($decision.execution_allowed -eq $true) {
    throw "execution_allowed must fail validation when true."
}

if ($decision.approved_for_live_execution -eq $true) {
    throw "approved_for_live_execution must not be true."
}

if ($decision.allowed_decision_results -notcontains $decision.decision_result) {
    throw "decision_result must be one of the allowed decision results."
}

foreach ($result in @("BLOCKED", "PAPER_REVIEW_READY", "INSUFFICIENT_DATA")) {
    if ($decision.allowed_decision_results -notcontains $result) {
        throw "Missing allowed decision result: $result"
    }
}

foreach ($field in @(
    "phase_14_2_workflow_id",
    "mock_signal_id",
    "latency_id",
    "mock_regime_id",
    "profitability_regime_filter_id",
    "mock_risk_gate_id",
    "profitability_risk_gate_id",
    "paper_trade_id",
    "scorecard_id"
)) {
    Assert-Property -Object $decision.source_trace -Name $field
}

foreach ($field in @(
    "latency_status",
    "signal_confidence_tier",
    "regime_status",
    "regime_evidence_complete_for_paper_review",
    "risk_gate_status",
    "risk_evidence_complete_for_paper_review",
    "paper_trade_result_status",
    "scorecard_decision",
    "trade_count",
    "confidence_score"
)) {
    Assert-Property -Object $decision.decision_inputs -Name $field
}

foreach ($action in @(
    "broker_execution",
    "OANDA_execution",
    "API_keys",
    "real_webhooks",
    "real_orders",
    "live_market_data_dependency",
    "live_trading",
    "automatic_route_execution"
)) {
    Assert-BlockedAction -Decision $decision -Action $action
}

if ($decision.decision_result -eq "PAPER_REVIEW_READY") {
    if ($decision.decision_inputs.latency_status -notin @("acceptable", "delayed")) {
        throw "PAPER_REVIEW_READY requires acceptable or delayed latency."
    }
    if ($decision.decision_inputs.regime_evidence_complete_for_paper_review -ne $true) {
        throw "PAPER_REVIEW_READY requires complete regime paper evidence."
    }
    if ($decision.decision_inputs.risk_evidence_complete_for_paper_review -ne $true) {
        throw "PAPER_REVIEW_READY requires complete risk paper evidence."
    }
}

if ($decision.decision_result -eq "BLOCKED") {
    if ($decision.decision_inputs.signal_confidence_tier -ne "very_low" -and
        $decision.decision_inputs.regime_status -eq "approved" -and
        $decision.decision_inputs.risk_gate_status -ne "blocked" -and
        $decision.decision_inputs.scorecard_decision -ne "blocked_for_live_execution") {
        throw "BLOCKED decision requires an active blocker."
    }
}

if ($decision.safety_confirmation.live_execution_remains_blocked -ne $true) {
    throw "Safety confirmation must keep live execution blocked."
}

Write-Output "Phase 14.3 DRY_RUN decision validation passed."
Write-Output "Paper/simulation-only mode confirmed."
Write-Output "Live execution remains BLOCKED."
Write-Output "Validator performed no routing, broker, webhook, order, or internet action."
