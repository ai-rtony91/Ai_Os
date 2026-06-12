$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$contractPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_15_4\RISK_GATE_DECISION_CONTRACT_V1.json"
$fixturePath = Join-Path $repoRoot "apps\dashboard\mock-data\risk-gate-decision-v1.example.json"

foreach ($path in @($contractPath, $fixturePath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required file: $path"
    }
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Risk gate decision fixture missing required field: $field"
    }
}

if ($fixture.mode -ne "paper_only") {
    throw "Risk gate decision mode must remain paper_only."
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Risk gate decision fixture missing required safety field: $field"
    }

    $expected = $contract.required_values.$field
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Risk gate decision $field must be $expected. Found: $actual"
    }
}

if ($contract.allowed_risk_gate_statuses -notcontains $fixture.risk_gate_status) {
    throw "Risk gate status is not allowed: $($fixture.risk_gate_status)"
}

foreach ($field in @("drawdown_status", "spread_status", "volatility_status", "session_status", "latency_status")) {
    if ($contract.allowed_context_statuses -notcontains $fixture.$field) {
        throw "$field is not allowed: $($fixture.$field)"
    }
}

if ($fixture.paper_route_allowed -eq $true) {
    if ($fixture.risk_gate_status -ne $contract.paper_route_rules.paper_route_allowed_requires_risk_gate_status) {
        throw "paper_route_allowed true requires risk_gate_status PASS."
    }
    if ($fixture.stale_signal -ne $contract.paper_route_rules.paper_route_allowed_requires_stale_signal) {
        throw "paper_route_allowed true requires stale_signal false."
    }
}

if ($fixture.risk_gate_status -in @("WARN", "FAIL", "REVIEW_REQUIRED") -and $fixture.paper_route_allowed -ne $false) {
    throw "WARN, FAIL, and REVIEW_REQUIRED risk decisions must keep paper_route_allowed false."
}

if ($fixture.paper_route_allowed -eq $false -and [string]::IsNullOrWhiteSpace($fixture.blocked_reason)) {
    throw "blocked_reason is required when paper_route_allowed is false."
}

foreach ($field in $contract.prohibited_fields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in risk gate decision fixture: $field"
    }
}

foreach ($gate in @("broker", "oanda", "api_keys", "real_orders", "live_execution")) {
    if (-not ($fixture.safety_gates.PSObject.Properties.Name -contains $gate)) {
        throw "Risk gate decision safety_gates missing $gate."
    }
    if ($fixture.safety_gates.$gate -ne "BLOCKED") {
        throw "Risk gate decision safety gate $gate must remain BLOCKED."
    }
}

if ($fixture.safety_gates.paper_only -ne $true) {
    throw "Risk gate decision safety_gates.paper_only must remain true."
}

Write-Host "PASS: Phase 15 risk gate decision v1 contract and fixture parse, required fields exist, and live execution remains blocked."
