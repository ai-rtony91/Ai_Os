$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

Write-Host "AI_OS Phase 15 Regime Filter v1 DRY_RUN"
Write-Host "Mode: read-only validation"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$contractPath = Join-Path $repoRoot "archive/docs_aios_trading_laboratory_legacy/phase_15_regime_filter/PHASE_15_REGIME_FILTER_V1_CONTRACT.json"
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/phase-15-regime-filter-v1.example.json"

foreach ($path in @($contractPath, $fixturePath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required Phase 15 regime filter file: $path"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_regime_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Fixture missing required regime field: $field"
    }
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    $expected = $contract.required_values.$field
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Fixture $field must be $expected. Found: $actual"
    }
}

foreach ($field in @("live_execution_status", "broker_status", "oanda_status", "api_key_status", "real_webhook_status", "real_order_status")) {
    if ($fixture.safety_gates.$field -ne "BLOCKED") {
        throw "Fixture safety_gates.$field must remain BLOCKED."
    }
}

foreach ($field in $contract.prohibited_fields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in fixture: $field"
    }
}

if ($contract.allowed_regime_statuses -notcontains $fixture.regime_status) {
    throw "regime_status is not allowed: $($fixture.regime_status)"
}

if ($contract.allowed_sessions -notcontains $fixture.session) {
    throw "session is not allowed: $($fixture.session)"
}

if ($contract.allowed_trend_states -notcontains $fixture.trend_state) {
    throw "trend_state is not allowed: $($fixture.trend_state)"
}

if ($contract.allowed_volatility_states -notcontains $fixture.volatility_state) {
    throw "volatility_state is not allowed: $($fixture.volatility_state)"
}

if ($contract.allowed_liquidity_states -notcontains $fixture.liquidity_state) {
    throw "liquidity_state is not allowed: $($fixture.liquidity_state)"
}

if ($contract.allowed_spread_states -notcontains $fixture.spread_state) {
    throw "spread_state is not allowed: $($fixture.spread_state)"
}

if ($contract.allowed_news_risk_states -notcontains $fixture.news_risk_state) {
    throw "news_risk_state is not allowed: $($fixture.news_risk_state)"
}

if (-not ($fixture.regime_confidence -is [int] -or $fixture.regime_confidence -is [double] -or $fixture.regime_confidence -is [decimal])) {
    throw "regime_confidence must be numeric."
}

if ($fixture.regime_confidence -lt 0 -or $fixture.regime_confidence -gt 100) {
    throw "regime_confidence must be between 0 and 100."
}

$unsafeDetected = $false
foreach ($stateField in $contract.unsafe_states.PSObject.Properties.Name) {
    $unsafeValues = $contract.unsafe_states.$stateField
    if ($unsafeValues -contains $fixture.$stateField) {
        $unsafeDetected = $true
    }
}

if ($unsafeDetected -and $fixture.paper_route_allowed -eq $true) {
    throw "Unsafe regime state cannot allow paper route preview."
}

if ($fixture.paper_route_allowed -eq $true -and $fixture.regime_status -ne "PASS") {
    throw "paper_route_allowed can be true only when regime_status is PASS."
}

if ($fixture.regime_status -eq "PASS") {
    if ($fixture.regime_confidence -lt $contract.confidence_rules.pass_minimum) {
        throw "PASS regime requires confidence at or above $($contract.confidence_rules.pass_minimum)."
    }
    if ($unsafeDetected) {
        throw "PASS regime cannot include unsafe market states."
    }
}

if ($fixture.regime_status -eq "BLOCKED" -and [string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
    throw "BLOCKED regime requires blocked_reason."
}

if ($fixture.paper_route_allowed -eq $false -and [string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
    throw "paper_route_allowed false requires blocked_reason."
}

if ($fixture.paper_route_boundary.live_execution_allowed -ne $false) {
    throw "paper_route_boundary.live_execution_allowed must be false."
}

if ($fixture.paper_route_boundary.broker_routing_allowed -ne $false) {
    throw "paper_route_boundary.broker_routing_allowed must be false."
}

if ($fixture.paper_route_boundary.real_order_allowed -ne $false) {
    throw "paper_route_boundary.real_order_allowed must be false."
}

[DateTimeOffset]::Parse($fixture.regime_checked_at) | Out-Null

Write-Host "PASS: Phase 15 regime filter v1 fixture and contract are valid, paper-only, and execution-blocked."
