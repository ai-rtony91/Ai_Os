$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$specPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_28\TRADERSPOST_PAPER_ROUTE_PREVIEW_V1_SPEC.md"
$contractPath = Join-Path $repoRoot "archive\docs_aios_trading_laboratory_legacy\phase_28\TRADERSPOST_PAPER_ROUTE_PREVIEW_V1_CONTRACT.json"
$fixturePath = Join-Path $repoRoot "apps\dashboard\mock-data\traderspost-paper-route-preview-v1.example.json"

foreach ($path in @($specPath, $contractPath, $fixturePath)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required file: $path"
    }
}

$contract = Get-Content -LiteralPath $contractPath -Raw | ConvertFrom-Json
$fixture = Get-Content -LiteralPath $fixturePath -Raw | ConvertFrom-Json
$spec = Get-Content -LiteralPath $specPath -Raw

foreach ($field in $contract.required_fields) {
    if (-not ($fixture.PSObject.Properties.Name -contains $field)) {
        throw "Route preview fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    $expected = $contract.required_values.$field
    $actual = $fixture.$field
    if ($actual -ne $expected) {
        throw "Route preview $field must be $expected. Found: $actual"
    }
}

foreach ($step in $contract.required_workflow) {
    if ($fixture.workflow -notcontains $step) {
        throw "Route preview workflow missing step: $step"
    }
}

foreach ($field in $contract.prohibited_fields) {
    if ($fixture.PSObject.Properties.Name -contains $field) {
        throw "Prohibited field found in route preview fixture: $field"
    }
}

if ($fixture.mode -ne "paper_only") {
    throw "Route preview mode must remain paper_only."
}

if ($fixture.paper_only -ne $true) {
    throw "Route preview paper_only must remain true."
}

if ($fixture.live_execution_blocked -ne $true) {
    throw "Route preview live_execution_blocked must remain true."
}

if ($fixture.approval_required_before_live -ne $true) {
    throw "Route preview approval_required_before_live must remain true."
}

if ($fixture.blocked_reason -notmatch "No real TradersPost webhook" -or
    $fixture.blocked_reason -notmatch "broker" -or
    $fixture.blocked_reason -notmatch "OANDA" -or
    $fixture.blocked_reason -notmatch "API key" -or
    $fixture.blocked_reason -notmatch "real order" -or
    $fixture.blocked_reason -notmatch "live execution") {
    throw "Blocked reason must explicitly block webhook, broker, OANDA, API key, real order, and live execution paths."
}

foreach ($gate in @("real_traderspost_webhook", "broker", "oanda", "api_keys", "real_orders", "live_execution")) {
    if (-not ($fixture.safety_gates.PSObject.Properties.Name -contains $gate)) {
        throw "Route preview safety_gates missing $gate."
    }
    if ($fixture.safety_gates.$gate -ne "BLOCKED") {
        throw "Route preview safety gate $gate must remain BLOCKED."
    }
}

foreach ($blockedText in @("No real TradersPost webhook", "No broker", "No OANDA", "No API keys", "No real orders", "No live execution")) {
    if ($spec -notmatch [regex]::Escape($blockedText)) {
        throw "Spec missing blocked capability text: $blockedText"
    }
}

Write-Host "PASS: TradersPost paper route preview v1 scaffold parses, required fields exist, and live execution remains blocked."
