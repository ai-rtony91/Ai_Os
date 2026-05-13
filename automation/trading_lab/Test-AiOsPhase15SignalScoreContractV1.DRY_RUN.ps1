$ErrorActionPreference = "Stop"

Write-Host "AI_OS Phase 15 Signal Score Contract v1 DRY_RUN"
Write-Host "Mode: read-only validation"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$contractPath = Join-Path $repoRoot "docs/AI_OS/trading_laboratory/signal_logs/PHASE_15_SIGNAL_SCORE_CONTRACT_V1.json"
$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/phase-15-signal-score-v1.example.json"

foreach ($path in @($contractPath, $fixturePath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required Phase 15 signal score file: $path"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Phase 15 signal score fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_safety_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Phase 15 signal score fixture missing required safety field: $field"
    }
}

foreach ($field in $contract.prohibited_fields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in Phase 15 signal score fixture: $field"
    }
}

foreach ($field in $contract.allowed_values.PSObject.Properties.Name) {
    $allowed = @($contract.allowed_values.$field)
    if ($allowed -notcontains $fixture.$field) {
        throw "Phase 15 signal score fixture $field has invalid value: $($fixture.$field)"
    }
}

foreach ($field in @("live_execution_status", "broker_status", "oanda_status", "api_key_status", "real_webhook_status", "real_order_status")) {
    if ($fixture.safety_gates.$field -ne "BLOCKED") {
        throw "Phase 15 signal score fixture safety_gates.$field must remain BLOCKED."
    }
}

if ($fixture.safety_gates.paper_only -ne $true) {
    throw "Phase 15 signal score fixture safety_gates.paper_only must be true."
}

if ($contract.allowed_direction_intents -notcontains $fixture.direction_intent) {
    throw "direction_intent is not allowed: $($fixture.direction_intent)"
}

foreach ($scoreField in @("confluence_score", "confidence_score")) {
    $value = $fixture.$scoreField
    if ($value -isnot [int] -and $value -isnot [long] -and $value -isnot [double]) {
        throw "$scoreField must be numeric."
    }
    if ($value -lt $contract.score_rules.score_min -or $value -gt $contract.score_rules.score_max) {
        throw "$scoreField must be between $($contract.score_rules.score_min) and $($contract.score_rules.score_max)."
    }
}

[DateTimeOffset]::Parse($fixture.score_created_at) | Out-Null

$paperRouteEligible = (
    $contract.score_rules.allowed_regime_statuses_for_paper_route -contains $fixture.regime_status -and
    $fixture.confluence_score -ge $contract.score_rules.minimum_confluence_score_for_paper_route -and
    $fixture.confidence_score -ge $contract.score_rules.minimum_confidence_score_for_paper_route -and
    $contract.score_rules.allowed_latency_statuses_for_paper_route -contains $fixture.latency_status -and
    $contract.score_rules.allowed_risk_gate_statuses_for_paper_route -contains $fixture.risk_gate_status -and
    $fixture.stale_signal -eq $false
)

if ($fixture.paper_route_allowed -ne $paperRouteEligible) {
    throw "paper_route_allowed must match contract score, regime, latency, risk, and stale-signal gates."
}

if ($fixture.paper_route_allowed -eq $false -and [string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
    throw "blocked_reason is required when paper_route_allowed is false."
}

if ($fixture.stale_signal -eq $true -and $fixture.paper_route_allowed -eq $true) {
    throw "stale_signal true must block paper_route_allowed."
}

if ($fixture.blocked_reason -notmatch "Live execution remains BLOCKED") {
    throw "blocked_reason must explicitly keep live execution blocked."
}

Write-Host "PASS: Phase 15 signal score contract and fixture are valid, JSON parses, score fields are complete, paper route gating is enforced, and live execution is blocked."
