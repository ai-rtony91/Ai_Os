$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$files = @(
    "archive/docs_aios_trading_laboratory_legacy/phase_15_9/STRATEGY_RANKING_CONTRACT.json",
    "apps/trading_lab/trading_lab/results/paper_runner/PAPER_STRATEGY_RANKING_001.json",
    "apps/dashboard/mock-data/trading-lab-strategy-ranking.example.json"
)

foreach ($file in $files) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path $path)) {
        throw "Missing required file: $file"
    }
    Get-Content -Raw $path | ConvertFrom-Json | Out-Null
}

$rankingPath = Join-Path $repoRoot "apps/trading_lab/trading_lab/results/paper_runner/PAPER_STRATEGY_RANKING_001.json"
$ranking = Get-Content -Raw $rankingPath | ConvertFrom-Json

if ($ranking.mode -ne "paper_only") {
    throw "Strategy ranking mode must be paper_only."
}

if ($ranking.rank_status -notin @("REVIEW", "BLOCKED_REPLAY_REVIEW", "NOT_ENOUGH_DATA")) {
    throw "Strategy ranking status is not a safe review status."
}

if ($ranking.total_paper_trades -lt 30 -and $ranking.rank_status -ne "BLOCKED_REPLAY_REVIEW") {
    throw "Small sample ranking must stay BLOCKED_REPLAY_REVIEW."
}

if ($ranking.clock_skew_count -gt 0 -and $ranking.replay_review_status -ne "BLOCKED_FOR_REVIEW") {
    throw "Clock skew must force replay review."
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
    if ($ranking.$field -ne "BLOCKED") {
        throw "$field must remain BLOCKED."
    }
}

Write-Host "PASS: Phase 15.9 strategy ranking remains paper-only and blocked for review."
