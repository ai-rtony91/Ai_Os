$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

$files = @(
    "apps/dashboard/mock-data/tradingview-paper-alert.example.json",
    "apps/dashboard/mock-data/traderspost-paper-route-preview.example.json",
    "apps/dashboard/mock-data/phase-28-tv-tp-paper-handoff.example.json",
    "archive/docs_aios_trading_laboratory_legacy/phase_28/TV_TP_PAPER_HANDOFF_CONTRACT.json"
)

foreach ($file in $files) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required file: $file"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$alert = Get-Content -LiteralPath (Join-Path $repoRoot "apps/dashboard/mock-data/tradingview-paper-alert.example.json") -Raw | ConvertFrom-Json
$route = Get-Content -LiteralPath (Join-Path $repoRoot "apps/dashboard/mock-data/traderspost-paper-route-preview.example.json") -Raw | ConvertFrom-Json
$handoff = Get-Content -LiteralPath (Join-Path $repoRoot "apps/dashboard/mock-data/phase-28-tv-tp-paper-handoff.example.json") -Raw | ConvertFrom-Json
$contract = Get-Content -LiteralPath (Join-Path $repoRoot "archive/docs_aios_trading_laboratory_legacy/phase_28/TV_TP_PAPER_HANDOFF_CONTRACT.json") -Raw | ConvertFrom-Json

foreach ($field in $contract.required_fields) {
    if (-not ($handoff.PSObject.Properties.Name -contains $field)) {
        throw "Phase 28 handoff fixture missing required field: $field"
    }
}

foreach ($field in $contract.required_values.PSObject.Properties.Name) {
    $expected = $contract.required_values.$field
    $actual = $handoff.$field
    if ($actual -ne $expected) {
        throw "Phase 28 handoff $field must be $expected. Found: $actual"
    }
}

foreach ($step in $contract.required_workflow) {
    if ($handoff.workflow -notcontains $step) {
        throw "Phase 28 handoff missing workflow step: $step"
    }
}

foreach ($field in @("live_execution", "broker", "real_order")) {
    if ($alert.$field -ne "BLOCKED") {
        throw "TradingView-style alert $field must remain BLOCKED."
    }
    if ($route.$field -ne "BLOCKED") {
        throw "TradersPost-style route $field must remain BLOCKED."
    }
    if ($handoff.$field -ne "BLOCKED") {
        throw "Phase 28 handoff $field must remain BLOCKED."
    }
}

if ($alert.api_key_required -ne $false -or $route.api_key_required -ne $false -or $handoff.api_key_required -ne $false) {
    throw "api_key_required must remain false in every Phase 28 fixture."
}

foreach ($field in $contract.prohibited_fields) {
    foreach ($fixture in @($alert, $route, $handoff)) {
        if ($fixture.PSObject.Properties.Name -contains $field) {
            throw "Prohibited field found in Phase 28 fixture: $field"
        }
    }
}

foreach ($latencyField in @("alert_created_time", "alert_received_time", "validation_start_time", "validation_end_time", "route_preview_time", "total_delay_seconds", "stale_status")) {
    if (-not ($handoff.latency.PSObject.Properties.Name -contains $latencyField)) {
        throw "Phase 28 latency object missing field: $latencyField"
    }
}

if ($handoff.source_platform -ne "TradingView-style") {
    throw "source_platform must be TradingView-style."
}

if ($handoff.received_by -ne "AI_OS") {
    throw "received_by must be AI_OS."
}

if ($handoff.route_style -ne "TradersPost-style paper preview") {
    throw "route_style must be TradersPost-style paper preview."
}

Write-Host "PASS: Phase 28 TV/TP paper handoff fixtures, contract, latency fields, and safety boundaries are valid."
