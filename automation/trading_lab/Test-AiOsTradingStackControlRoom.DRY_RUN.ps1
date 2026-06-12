$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$files = @(
    "archive/docs_aios_trading_laboratory_legacy/phase_16/TRADING_STACK_CONTROL_ROOM_CONTRACT.json",
    "apps/dashboard/mock-data/trading-stack-control-room.example.json"
)

foreach ($file in $files) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path $path)) {
        throw "Missing required file: $file"
    }
    Get-Content -Raw $path | ConvertFrom-Json | Out-Null
}

$fixturePath = Join-Path $repoRoot "apps/dashboard/mock-data/trading-stack-control-room.example.json"
$fixture = Get-Content -Raw $fixturePath | ConvertFrom-Json

if ($fixture.mode -ne "paper_only") {
    throw "Control room mode must be paper_only."
}

if ($fixture.control_room_status -ne "CONTROL_ROOM_REVIEW") {
    throw "Control room must remain in review."
}

$requiredSections = @(
    "Signal Queue",
    "Validation Queue",
    "Paper Bot Status",
    "Safety Boundary",
    "Runtime Workflow",
    "Next Safe Action"
)

foreach ($section in $requiredSections) {
    if ($section -notin $fixture.sections.label) {
        throw "Missing control room section: $section"
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
    if ($fixture.safety.$field -ne "BLOCKED") {
        throw "$field must remain BLOCKED."
    }
}

Write-Host "PASS: Phase 16 control room is mock-data only and paper-only."
