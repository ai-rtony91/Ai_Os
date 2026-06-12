$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

$fixtureRoot = "apps/trading_lab/trading_lab/fixtures/paper_signal_test_pack"
$resultRoot = "apps/trading_lab/trading_lab/results/paper_signal_test_pack"
$requiredFiles = @(
    "apps/trading_lab/trading_lab/ingest/paper_signal_test_pack_runner.py",
    "$fixtureRoot/PAPER_SIGNAL_VALID_LONG_001.json",
    "$fixtureRoot/PAPER_SIGNAL_VALID_SHORT_001.json",
    "$fixtureRoot/PAPER_SIGNAL_MISSING_FIELD_001.json",
    "$fixtureRoot/PAPER_SIGNAL_STALE_001.json",
    "$fixtureRoot/PAPER_SIGNAL_FUTURE_CLOCK_SKEW_001.json",
    "$fixtureRoot/PAPER_SIGNAL_BAD_DIRECTION_001.json",
    "$fixtureRoot/PAPER_SIGNAL_LOW_CONFIDENCE_001.json",
    "$fixtureRoot/PAPER_SIGNAL_UNSUPPORTED_SYMBOL_001.json",
    "$fixtureRoot/PAPER_SIGNAL_UNSUPPORTED_TIMEFRAME_001.json",
    "$fixtureRoot/PAPER_SIGNAL_DUPLICATE_001.json",
    "$resultRoot/PAPER_SIGNAL_TEST_PACK_LEDGER_001.json",
    "$resultRoot/PAPER_SIGNAL_TEST_PACK_SCORECARD_001.json",
    "$resultRoot/PAPER_SIGNAL_TEST_PACK_VALIDATION_REPORT_001.json",
    "archive/docs_aios_trading_laboratory_legacy/phase_22/PHASE_22_PAPER_SIGNAL_TEST_PACK.md",
    "archive/docs_aios_trading_laboratory_legacy/phase_22/PAPER_SIGNAL_TEST_PACK_CONTRACT.json",
    "apps/dashboard/mock-data/paper-signal-test-pack.example.json"
)

foreach ($file in $requiredFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $file))) {
        throw "Missing required file: $file"
    }
}

Get-ChildItem -LiteralPath (Join-Path $repoRoot $fixtureRoot) -Filter "*.json" -File | ForEach-Object {
    Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json | Out-Null
}
Get-ChildItem -LiteralPath (Join-Path $repoRoot $resultRoot) -Filter "*.json" -File | ForEach-Object {
    Get-Content -LiteralPath $_.FullName -Raw | ConvertFrom-Json | Out-Null
}
Get-Content -LiteralPath (Join-Path $repoRoot "archive/docs_aios_trading_laboratory_legacy/phase_22/PAPER_SIGNAL_TEST_PACK_CONTRACT.json") -Raw | ConvertFrom-Json | Out-Null
Get-Content -LiteralPath (Join-Path $repoRoot "apps/dashboard/mock-data/paper-signal-test-pack.example.json") -Raw | ConvertFrom-Json | Out-Null

python -m trading_lab.ingest.paper_signal_test_pack_runner --json | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Paper signal test pack runner failed."
}

$ledger = Get-Content -LiteralPath (Join-Path $repoRoot "$resultRoot/PAPER_SIGNAL_TEST_PACK_LEDGER_001.json") -Raw | ConvertFrom-Json
$scorecard = Get-Content -LiteralPath (Join-Path $repoRoot "$resultRoot/PAPER_SIGNAL_TEST_PACK_SCORECARD_001.json") -Raw | ConvertFrom-Json
$report = Get-Content -LiteralPath (Join-Path $repoRoot "$resultRoot/PAPER_SIGNAL_TEST_PACK_VALIDATION_REPORT_001.json") -Raw | ConvertFrom-Json

if ($scorecard.total_signals -ne 10) {
    throw "Expected 10 total signals."
}
if ($scorecard.accepted -ne 2) {
    throw "Expected 2 accepted signals."
}
if ($scorecard.rejected -ne 8) {
    throw "Expected 8 rejected signals."
}
if ($report.result -ne "PASS") {
    throw "Validation report did not pass."
}

$requiredReasons = @(
    "Missing required fields: timeframe.",
    "Signal is stale.",
    "Clock skew detected: alert time is too far ahead.",
    "Direction is not a paper review value.",
    "Confidence is below paper review threshold.",
    "Symbol is not in the paper test allowlist.",
    "Timeframe is not in the paper test allowlist.",
    "Duplicate signal id."
)
foreach ($reason in $requiredReasons) {
    if ($scorecard.blocked_reasons -notcontains $reason) {
        throw "Missing blocked reason: $reason"
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
    if ($ledger.$field -ne "BLOCKED") {
        throw "Ledger $field must remain BLOCKED."
    }
    if ($scorecard.$field -ne "BLOCKED") {
        throw "Scorecard $field must remain BLOCKED."
    }
    if ($report.$field -ne "BLOCKED") {
        throw "Report $field must remain BLOCKED."
    }
}

Write-Host "PASS: Phase 22 paper signal test pack processed 10 local paper signals with expected accept/reject results."
