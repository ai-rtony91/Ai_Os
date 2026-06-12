Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
# Archive Trading Lab docs referenced below are historical/reference-only evidence, not current authority.
# This validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.
$tracePath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_14_2\PHASE_14_2_SIGNAL_TO_SCORECARD_TRACE_001.json"
$latencyPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\latency\TRADING_LATENCY_LEDGER_001.json"

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
        [object] $Trace,
        [Parameter(Mandatory = $true)]
        [string] $Action
    )

    if ($Trace.blocked_actions -notcontains $Action) {
        throw "Missing blocked action: $Action"
    }
}

$trace = Read-JsonFile -Path $tracePath
$latency = Read-JsonFile -Path $latencyPath

foreach ($field in @(
    "workflow_id",
    "mode",
    "live_execution_status",
    "execution_allowed",
    "blocked_actions",
    "traceability",
    "latency_fields_required",
    "safety_confirmation"
)) {
    Assert-Property -Object $trace -Name $field
}

if ($trace.mode -ne "paper_only_simulation") {
    throw "Trace mode must be paper_only_simulation."
}

if ($trace.live_execution_status -ne "BLOCKED") {
    throw "Live execution status must be BLOCKED."
}

if ($trace.execution_allowed -eq $true) {
    throw "execution_allowed must not be true."
}

if ($trace.approved_for_live_execution -eq $true) {
    throw "approved_for_live_execution must not be true."
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
    Assert-BlockedAction -Trace $trace -Action $action
}

foreach ($field in $trace.latency_fields_required) {
    Assert-Property -Object $latency -Name $field
}

if ($latency.mode -ne "paper_only") {
    throw "Latency mode must be paper_only."
}

foreach ($node in @(
    $trace.traceability.signal,
    $trace.traceability.latency,
    $trace.traceability.regime,
    $trace.traceability.risk,
    $trace.traceability.paper_result,
    $trace.traceability.scorecard
)) {
    if ($null -eq $node) {
        throw "Missing signal/regime/risk/paper-result/scorecard traceability node."
    }
}

if ($trace.traceability.risk.approved_for_live_execution -eq $true) {
    throw "Risk traceability must not approve live execution."
}

if ($trace.safety_confirmation.live_execution_remains_blocked -ne $true) {
    throw "Safety confirmation must keep live execution blocked."
}

Write-Output "Phase 14.2 DRY_RUN validation passed."
Write-Output "Paper/simulation mode only confirmed."
Write-Output "Live execution remains BLOCKED."
