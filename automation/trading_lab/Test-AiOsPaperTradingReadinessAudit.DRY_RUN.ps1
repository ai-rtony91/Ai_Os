$ErrorActionPreference = "Stop"

# Archive docs referenced below are historical/reference-only evidence, not current authority.
# This DRY_RUN validator does not approve live trading, broker execution, real webhooks, real orders, credentials, APPLY, commit, push, merge, or deployment.

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$files = @(
    "archive/docs_aios_trading_laboratory_legacy/phase_19_1/PAPER_TRADING_READINESS_AUDIT_CONTRACT.json",
    "apps/dashboard/mock-data/paper-trading-readiness-audit.example.json"
)

foreach ($file in $files) {
    $path = Join-Path $repoRoot $file
    if (-not (Test-Path $path)) {
        throw "Missing required file: $file"
    }
    Get-Content -Raw $path | ConvertFrom-Json | Out-Null
}

$auditPath = Join-Path $repoRoot "apps/dashboard/mock-data/paper-trading-readiness-audit.example.json"
$audit = Get-Content -Raw $auditPath | ConvertFrom-Json

if ($audit.mode -ne "paper_only") {
    throw "Readiness audit mode must be paper_only."
}

if ($audit.overall_readiness_status -notin @("NOT_READY", "REVIEW")) {
    throw "Readiness audit must remain NOT_READY or REVIEW."
}

if ($audit.paper_readiness_score -gt 60) {
    throw "Paper readiness score is too high while replay clock skew remains unresolved."
}

$requiredChecks = @(
    "safety_locks",
    "validator_coverage",
    "latency_reliability",
    "replay_consistency",
    "strategy_ranking",
    "dashboard_clarity",
    "mobile_usability"
)

foreach ($check in $requiredChecks) {
    if ($check -notin $audit.checks.check_id) {
        throw "Missing readiness check: $check"
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
    if ($audit.safety.$field -ne "BLOCKED") {
        throw "$field must remain BLOCKED."
    }
}

Write-Host "PASS: Phase 19.1 paper trading readiness audit remains NOT_READY and blocked."
