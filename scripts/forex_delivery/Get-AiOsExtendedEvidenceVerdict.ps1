param(
    [string]$LedgerPath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-AiOsRepoRoot {
    if ($env:AIOS_REPO_ROOT -and (Test-Path -LiteralPath $env:AIOS_REPO_ROOT)) {
        return (Resolve-Path -LiteralPath $env:AIOS_REPO_ROOT).Path
    }

    if ($PSScriptRoot) {
        $candidate = Join-Path $PSScriptRoot "../.."
        if (Test-Path -LiteralPath $candidate) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }

    $gitRoot = (& git rev-parse --show-toplevel 2>$null)
    if ($LASTEXITCODE -eq 0 -and $gitRoot) {
        return (Resolve-Path -LiteralPath $gitRoot.Trim()).Path
    }

    throw "AIOS_REPO_ROOT_UNRESOLVED"
}

$repoRoot = Resolve-AiOsRepoRoot
Set-Location -LiteralPath $repoRoot

if (-not $LedgerPath) {
    $LedgerPath = "telemetry/forex/demo_proof_ledger.jsonl"
}

$resultJson = @(
    python -m automation.forex_engine.forex_extended_evidence_campaign_v1 `
        --repo-root $repoRoot `
        --ledger $LedgerPath 2>&1
)

if ($LASTEXITCODE -ne 0) {
    $resultJson | ForEach-Object { Write-Output $_ }
    throw "EXTENDED_EVIDENCE_CAMPAIGN_EVALUATION_FAILED"
}

$result = ($resultJson -join "`n") | ConvertFrom-Json

Write-Output "STATUS=$($result.status)"
Write-Output "ACHIEVED_TIER=$($result.achieved_tier)"
Write-Output "NEXT_TARGET_TIER=$($result.next_target_tier)"
Write-Output "ENGINEERING_TRADES=$($result.summary.engineering_trades)"
Write-Output "MARKET_DEMO_TRADES=$($result.summary.market_demo_trades)"
Write-Output "FIXTURE_OR_SIMULATION_TRADES=$($result.summary.fixture_or_simulation_trades)"
Write-Output "MARKET_DEMO_DAYS=$($result.summary.market_demo_days)"
Write-Output "MARKET_DEMO_WINDOWS=$($result.summary.market_demo_windows)"
Write-Output "LATEST_MARKET_EVIDENCE_DATE=$($result.summary.latest_market_evidence_date)"
Write-Output "LATEST_MARKET_EVIDENCE_AGE_DAYS=$($result.summary.latest_market_evidence_age_days)"
Write-Output "EVIDENCE_AGE_OK=$([string]$result.summary.evidence_age_ok)"
Write-Output "EXPECTANCY_PER_TRADE=$($result.summary.expectancy_per_trade)"
Write-Output "PROFIT_FACTOR=$($result.summary.profit_factor)"
Write-Output "MAX_DRAWDOWN_PCT=$($result.summary.max_drawdown_pct)"
Write-Output "METRICS_COMPLETE=$([string]$result.summary.metrics_complete)"
Write-Output "BLOCKERS=$($result.blockers -join ';')"
Write-Output "NEXT_TARGET_BLOCKERS=$($result.next_target_blockers -join ';')"
Write-Output "NEXT_SAFE_ACTION=$($result.next_safe_action)"
Write-Output "LIVE_TRADING_ALLOWED=$([string]$result.safety.live_trading_allowed)"
Write-Output "AUTOMATIC_ORDER_EXECUTION_ALLOWED=$([string]$result.safety.automatic_order_execution_allowed)"
