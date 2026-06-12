$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$env:PYTHONPATH = Join-Path $repoRoot "apps\trading_lab"

$files = @(
    "apps/trading_lab/trading_lab/ingest/paper_signal_api.py",
    "apps/trading_lab/trading_lab/fixtures/paper_signal_api/PAPER_SIGNAL_API_VALID_001.json",
    "apps/trading_lab/trading_lab/fixtures/paper_signal_api/PAPER_SIGNAL_API_MISSING_FIELDS_001.json",
    "apps/trading_lab/trading_lab/fixtures/paper_signal_api/PAPER_SIGNAL_API_STALE_001.json",
    "apps/trading_lab/trading_lab/results/paper_signal_api/PAPER_SIGNAL_INTAKE_LEDGER_001.json",
    "apps/trading_lab/trading_lab/results/paper_signal_api/PAPER_SIGNAL_VALIDATION_RESULT_001.json",
    "apps/trading_lab/trading_lab/results/paper_signal_api/PAPER_ROUTE_PREVIEW_001.json",
    "archive/docs_aios_trading_laboratory_legacy/phase_21/PAPER_SIGNAL_API_CONTRACT.json",
    "apps/dashboard/mock-data/paper-signal-api-intake.example.json"
)

foreach ($file in $files) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing required file: $file"
    }
}

$jsonFiles = $files | Where-Object { $_.EndsWith(".json") }
foreach ($file in $jsonFiles) {
    Get-Content -LiteralPath (Join-Path $repoRoot $file) -Raw | ConvertFrom-Json | Out-Null
}

$missingFixture = Join-Path $repoRoot "apps/trading_lab/trading_lab/fixtures/paper_signal_api/PAPER_SIGNAL_API_MISSING_FIELDS_001.json"
$missingOutput = python -m trading_lab.ingest.paper_signal_api --fixture $missingFixture --validation-time "2026-05-12T00:05:00Z" | Out-String
if ($LASTEXITCODE -ne 0) {
    throw "Missing-fields fixture command failed."
}
$missingResult = $missingOutput | ConvertFrom-Json
if ($missingResult.validation_result.validation_status -ne "REJECTED") {
    throw "Missing-fields fixture was not rejected."
}

$staleFixture = Join-Path $repoRoot "apps/trading_lab/trading_lab/fixtures/paper_signal_api/PAPER_SIGNAL_API_STALE_001.json"
$staleOutput = python -m trading_lab.ingest.paper_signal_api --fixture $staleFixture --validation-time "2026-05-12T00:05:00Z" | Out-String
if ($LASTEXITCODE -ne 0) {
    throw "Stale fixture command failed."
}
$staleResult = $staleOutput | ConvertFrom-Json
if ($staleResult.validation_result.validation_status -ne "REJECTED") {
    throw "Stale fixture was not rejected."
}
if ($staleResult.validation_result.stale_signal_status -ne "STALE_SIGNAL_REJECTED") {
    throw "Stale fixture did not preserve stale rejection status."
}

$validFixture = Join-Path $repoRoot "apps/trading_lab/trading_lab/fixtures/paper_signal_api/PAPER_SIGNAL_API_VALID_001.json"
python -m trading_lab.ingest.paper_signal_api --fixture $validFixture --validation-time "2026-05-12T00:05:00Z" | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Valid paper signal fixture failed."
}

$ledger = Get-Content -LiteralPath (Join-Path $repoRoot "apps/trading_lab/trading_lab/results/paper_signal_api/PAPER_SIGNAL_INTAKE_LEDGER_001.json") -Raw | ConvertFrom-Json
$validation = Get-Content -LiteralPath (Join-Path $repoRoot "apps/trading_lab/trading_lab/results/paper_signal_api/PAPER_SIGNAL_VALIDATION_RESULT_001.json") -Raw | ConvertFrom-Json
$route = Get-Content -LiteralPath (Join-Path $repoRoot "apps/trading_lab/trading_lab/results/paper_signal_api/PAPER_ROUTE_PREVIEW_001.json") -Raw | ConvertFrom-Json

if ($ledger.intake_status -ne "ACCEPTED_FOR_PAPER_PREVIEW") {
    throw "Valid fixture did not reach paper preview intake."
}

if ($validation.validation_status -ne "PASS") {
    throw "Valid fixture did not pass validation."
}

if ($route.route_mode -ne "PAPER_PREVIEW_ONLY") {
    throw "Route mode must remain PAPER_PREVIEW_ONLY."
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
    if ($validation.$field -ne "BLOCKED") {
        throw "Validation $field must remain BLOCKED."
    }
    if ($route.$field -ne "BLOCKED") {
        throw "Route $field must remain BLOCKED."
    }
}

Write-Host "PASS: Phase 21 paper signal API intake accepts valid paper preview input and rejects unsafe fixtures."
