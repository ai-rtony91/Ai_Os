$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$files = @(
    "docs/AI_OS/trading_laboratory/profitability/PAPER_REVIEW_LEDGER_001.json",
    "docs/AI_OS/trading_laboratory/profitability/STRATEGY_PERFORMANCE_SUMMARY_001.json",
    "docs/AI_OS/trading_laboratory/latency/REPLAY_FAILURE_SUMMARY_001.json",
    "apps/dashboard/mock-data/trading-lab-performance-review.example.json"
)

foreach ($file in $files) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path $path)) {
        throw "Missing required file: $file"
    }
    Get-Content -Raw $path | ConvertFrom-Json | Out-Null
}

$ledger = Get-Content -Raw (Join-Path $repoRoot "docs/AI_OS/trading_laboratory/profitability/PAPER_REVIEW_LEDGER_001.json") | ConvertFrom-Json
$summary = Get-Content -Raw (Join-Path $repoRoot "docs/AI_OS/trading_laboratory/profitability/STRATEGY_PERFORMANCE_SUMMARY_001.json") | ConvertFrom-Json
$failure = Get-Content -Raw (Join-Path $repoRoot "docs/AI_OS/trading_laboratory/latency/REPLAY_FAILURE_SUMMARY_001.json") | ConvertFrom-Json

if ($ledger.mode -ne "paper_only" -or $summary.mode -ne "paper_only" -or $failure.mode -ne "paper_only") {
    throw "All performance review files must be paper_only."
}

if ($summary.performance_status -ne "REVIEW_INCOMPLETE") {
    throw "Strategy performance must remain REVIEW_INCOMPLETE."
}

if ($failure.counts.clock_skew_count -lt 1) {
    throw "Replay failure summary must preserve clock skew count."
}

if ($ledger.no_profit_claim -ne $true -or $summary.no_profit_claim -ne $true) {
    throw "Paper review files must include no_profit_claim true."
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
    if ($ledger.safety.$field -ne "BLOCKED") {
        throw "Ledger $field must remain BLOCKED."
    }
    if ($summary.safety.$field -ne "BLOCKED") {
        throw "Summary $field must remain BLOCKED."
    }
    if ($failure.safety.$field -ne "BLOCKED") {
        throw "Replay failure $field must remain BLOCKED."
    }
}

Write-Host "PASS: Phase 17.1-17.3 performance review remains paper-only and review-gated."
