$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$files = @(
    "docs/AI_OS/trading_laboratory/external_handoff/TV_TP_PAPER_ROUTE_CONTRACT.json",
    "docs/AI_OS/trading_laboratory/external_handoff/TV_ALERT_REFERENCE_SCHEMA.json",
    "docs/AI_OS/trading_laboratory/external_handoff/TP_PAPER_ROUTE_PREVIEW_SCHEMA.json",
    "apps/dashboard/mock-data/tv-tp-paper-route-workflow.example.json"
)

foreach ($file in $files) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required file: $file"
    }
    Get-Content -LiteralPath $path -Raw | ConvertFrom-Json | Out-Null
}

$contract = Get-Content -LiteralPath (Join-Path $repoRoot "docs/AI_OS/trading_laboratory/external_handoff/TV_TP_PAPER_ROUTE_CONTRACT.json") -Raw | ConvertFrom-Json
$fixture = Get-Content -LiteralPath (Join-Path $repoRoot "apps/dashboard/mock-data/tv-tp-paper-route-workflow.example.json") -Raw | ConvertFrom-Json

if ($contract.source_status -ne "EXTERNAL_REFERENCE_ONLY") {
    throw "source_status must be EXTERNAL_REFERENCE_ONLY."
}

if ($contract.target_platform -ne "TRADERSPOST_REFERENCE") {
    throw "target_platform must be TRADERSPOST_REFERENCE."
}

if ($contract.route_mode -ne "PAPER_PREVIEW_ONLY") {
    throw "route_mode must be PAPER_PREVIEW_ONLY."
}

$requiredSteps = @(
    "TradingView Signal Reference",
    "AI_OS Signal Intake",
    "Latency Check",
    "Clock Skew Check",
    "Regime Check",
    "Risk Gate",
    "Strategy Ranking",
    "Paper Route Preview",
    "TradersPost Paper Route Reference",
    "Paper Result Review",
    "Next Safe Action"
)

foreach ($step in $requiredSteps) {
    if ($contract.workflow_steps -notcontains $step) {
        throw "Missing contract workflow step: $step"
    }
    if ($fixture.workflow_steps.label -notcontains $step) {
        throw "Missing fixture workflow step: $step"
    }
}

$blockedFields = @(
    "live_execution_status",
    "broker_status",
    "oanda_status",
    "api_key_status",
    "secrets_status",
    "real_webhook_status",
    "real_order_status"
)

foreach ($field in $blockedFields) {
    if ($contract.required_statuses.$field -ne "BLOCKED") {
        throw "Contract $field must remain BLOCKED."
    }
    if ($fixture.safety.$field -ne "BLOCKED") {
        throw "Fixture $field must remain BLOCKED."
    }
}

if ($fixture.source_status -ne "EXTERNAL_REFERENCE_ONLY") {
    throw "Fixture source_status must be EXTERNAL_REFERENCE_ONLY."
}

if ($fixture.target_platform -ne "TRADERSPOST_REFERENCE") {
    throw "Fixture target_platform must be TRADERSPOST_REFERENCE."
}

if ($fixture.route_mode -ne "PAPER_PREVIEW_ONLY") {
    throw "Fixture route_mode must be PAPER_PREVIEW_ONLY."
}

Write-Host "PASS: Phase 20 TV/TP paper route workflow is reference-only, paper-preview-only, and safety blocked."
