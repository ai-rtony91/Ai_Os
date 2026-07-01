param()

Set-Location -LiteralPath "C:/Dev/Ai.Os"
$ErrorActionPreference = "Stop"

$repoRoot = (Get-Location).Path
$ledgerPath = Join-Path $repoRoot "telemetry/forex/demo_proof_ledger.jsonl"

$branch = (git branch --show-current).Trim()
if ($branch -ne "main") {
    throw "VERDICT_REQUIRES_MAIN_BRANCH:$branch"
}

if (-not (Test-Path -LiteralPath $ledgerPath)) {
    throw "DEMO_PROOF_LEDGER_MISSING:$ledgerPath"
}

$python = @'
import json
import sys
from pathlib import Path

repo_root = Path(r"C:/Dev/Ai.Os")
src_root = repo_root / "src"
for path in (repo_root, src_root):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from automation.forex_engine import supervised_autonomy_governor_v1 as governor
from automation.forex_engine.forex_demo_run_day_recorder_v1 import build_demo_verdict_snapshot

summary = build_demo_verdict_snapshot(repo_root, baseline_equity_usd=1000.0)
verdict_status = str(summary["verdict_status"])
payload = {
    "schema": "aios.forex.demo_verdict_snapshot.v1",
    "days_recorded": int(summary["days_recorded_toward_verdict"]),
    "trades_accumulated": int(summary["trades_accumulated"]),
    "windows": int(summary["windows"]),
    "evidence_age_ok": bool(summary["evidence_age_ok"]),
    "current_expectancy": str(summary["current_expectancy"]),
    "current_profit_factor": str(summary["current_profit_factor"]),
    "days_until_verdict_possible": int(summary["days_until_verdict_possible"]),
    "verdict_status": verdict_status,
    "mock_entries_superseded_by_real_run": int(summary["mock_entries_superseded_by_real_run"]),
    "thresholds": {
        "minimum_total_trades": governor.MIN_SAMPLE_SIZE,
        "minimum_walk_forward_windows": governor.MIN_WALK_FORWARD_WINDOWS,
        "minimum_expectancy": governor.MIN_EXPECTANCY,
        "minimum_profit_factor": governor.MIN_PROFIT_FACTOR,
        "maximum_evidence_age_days": governor.MAX_EVIDENCE_AGE_DAYS,
        "maximum_drawdown_ratio": governor.MAX_DRAWDOWN_RATIO,
    },
    "verdict_blockers": list(summary["verdict_blockers"]),
}

if verdict_status == "VERDICT_READY":
    governor_command = (
        "python scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py "
        "--state-json Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_STATE_MODEL_V1.json "
        "--governor-input-json Reports/forex_delivery/AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json "
        "--write-state --write-report"
    )
    next_gate_command = (
        "python -c 'from automation.forex_engine.forex_profit_production_next_gate_v1 import evaluate_forex_profit_production_next_gate_v1; "
        "import json; evidence = {\"total_trades\": %d, \"expectancy\": %s, \"profit_factor\": %s, "
        "\"max_drawdown_pct\": %s, \"risk_controls_present\": True, \"risk_controls_passed\": True, "
        "\"owner_approval_required\": True, \"live_trading_requested\": False}; "
        "print(json.dumps(evaluate_forex_profit_production_next_gate_v1(evidence), indent=2, sort_keys=True))'"
        % (
            int(summary["trades_accumulated"]),
            str(summary["current_expectancy"]),
            str(summary["current_profit_factor"]),
            str(summary["max_drawdown_pct"]),
        )
    )
    payload["governor_rerun_command"] = governor_command
    payload["next_gate_command"] = next_gate_command

print(json.dumps(payload, sort_keys=True))
'@

$verdictJson = $python | python -
if ($LASTEXITCODE -ne 0) {
    throw "VERDICT_EVALUATION_FAILED"
}

$verdict = $verdictJson | ConvertFrom-Json

Write-Output "DAYS_RECORDED=$($verdict.days_recorded)"
Write-Output "TRADES_ACCUMULATED=$($verdict.trades_accumulated)"
Write-Output "WINDOWS=$($verdict.windows)"
Write-Output ("EVIDENCE_AGE_OK={0}" -f ([string]$verdict.evidence_age_ok).ToLowerInvariant())
Write-Output "CURRENT_EXPECTANCY=$($verdict.current_expectancy)"
Write-Output "CURRENT_PROFIT_FACTOR=$($verdict.current_profit_factor)"
Write-Output "DAYS_UNTIL_VERDICT_POSSIBLE=$($verdict.days_until_verdict_possible)"
Write-Output "VERDICT_STATUS=$($verdict.verdict_status)"
Write-Output "MOCK_ENTRIES_SUPERSEDED_BY_REAL_RUN=$($verdict.mock_entries_superseded_by_real_run)"

if ($verdict.verdict_status -eq "VERDICT_READY") {
    Write-Output "GOVERNOR_RERUN_COMMAND=$($verdict.governor_rerun_command)"
    Write-Output "NEXT_GATE_COMMAND=$($verdict.next_gate_command)"
} else {
    Write-Output "GOVERNOR_RERUN_COMMAND=PENDING_VERDICT_READY"
    Write-Output "NEXT_GATE_COMMAND=PENDING_VERDICT_READY"
}
