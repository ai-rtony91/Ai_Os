param(
    [switch]$DryRun
)

Set-Location -LiteralPath "C:/Dev/Ai.Os"
$ErrorActionPreference = "Stop"

$repoRoot = (Get-Location).Path
$safetyConfigPath = Join-Path $repoRoot "control/forex/forex_safety_controls_config.json"
$brakeLedgerPath = Join-Path $repoRoot "telemetry/forex/brake_trip_proof_ledger.jsonl"

$branch = (git branch --show-current).Trim()
if ($branch -ne "main") {
    throw "START_REQUIRES_MAIN_BRANCH:$branch"
}

if (-not (Test-Path -LiteralPath $safetyConfigPath)) {
    throw "SAFETY_CONFIG_MISSING:$safetyConfigPath"
}

if (-not (Test-Path -LiteralPath $brakeLedgerPath)) {
    throw "BRAKE_TRIP_PROOF_LEDGER_MISSING:$brakeLedgerPath"
}

$brakeLedger = Get-Content -LiteralPath $brakeLedgerPath -Raw | ConvertFrom-Json
if (-not ($brakeLedger | Where-Object { $_.ledger_label -eq "SIMULATED_TRIP_PROOF" -and $_.trip_passed -eq $true })) {
    throw "BRAKE_TRIP_PROOF_LEDGER_HAS_NO_PASSED_TRIPS"
}

foreach ($tripId in @("T1", "T2", "T3")) {
    $passingTrip = @(
        $brakeLedger | Where-Object {
            $_.ledger_label -eq "SIMULATED_TRIP_PROOF" -and $_.trip_id -eq $tripId -and $_.trip_passed -eq $true
        }
    )
    if ($passingTrip.Count -eq 0) {
        throw "BRAKE_TRIP_PROOF_TRIP_MISSING_OR_FAILED:$tripId"
    }
}

$env:AIOS_REPO_ROOT = $repoRoot
$env:AIOS_DEMO_DRY_RUN = if ($DryRun) { "1" } else { "0" }

$python = @'
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

repo_root = Path(os.environ["AIOS_REPO_ROOT"])
dry_run = os.environ.get("AIOS_DEMO_DRY_RUN") == "1"
src_root = repo_root / "src"
for path in (repo_root, src_root):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from forex_delivery.paper_signal_execution_loop import build_paper_signal_execution_loop_result
from automation.forex_engine.forex_demo_run_day_recorder_v1 import record_forex_demo_run_day

safety_path = repo_root / "control" / "forex" / "forex_safety_controls_config.json"
safety = json.loads(safety_path.read_text(encoding="utf-8"))
recorded_at = datetime.now(timezone.utc).replace(microsecond=0)
read_model = {
    "source_type": "paper",
    "source_label": "AIOS_DEMO_RUN_LAUNCH_V10",
    "freshness_utc": recorded_at.isoformat().replace("+00:00", "Z"),
    "stale_status": "VALID",
    "block_reason": "Demo run launch preflight passed.",
    "safety_controls": safety,
    "daily_loss_warning_usd": safety["daily_stop"]["daily_loss_warning_usd"],
    "daily_loss_stop_usd": safety["daily_stop"]["daily_loss_stop_usd"],
    "max_total_loss_usd": safety["max_loss"]["max_total_loss_usd"],
}
session_result = build_paper_signal_execution_loop_result(read_model=read_model)
realized = float(session_result.get("realized_paper_pl") or 0.0)
daily_loss = round(max(0.0, -realized), 2)
warning_threshold = float(safety["daily_stop"]["daily_loss_warning_usd"])
halt_threshold = float(safety["daily_stop"]["daily_loss_stop_usd"])
max_loss_threshold = float(safety["max_loss"]["max_total_loss_usd"])
warning_intent = daily_loss >= warning_threshold
halt_for_day = daily_loss >= halt_threshold
halt_all = daily_loss >= max_loss_threshold
receipt = record_forex_demo_run_day(
    repo_root,
    session_result,
    apply=not dry_run,
    recorded_at_utc=recorded_at,
    session_date=recorded_at.date().isoformat(),
    baseline_equity_usd=float(safety.get("baseline_equity_usd", 1000.0)),
)

payload = {
    "warning_intent": warning_intent,
    "halt_for_day": halt_for_day,
    "halt_all": halt_all,
    "summary": {
        "fills": int(receipt["session_summary"]["fills"]),
        "wins": int(receipt["session_summary"]["wins"]),
        "losses": int(receipt["session_summary"]["losses"]),
        "realized_pnl_usd": float(receipt["session_summary"]["realized_pnl_usd"]),
        "days_recorded_toward_verdict": int(receipt["days_recorded_toward_verdict"]),
    },
}
print(json.dumps(payload, sort_keys=True))
'@

$demoJson = $python | python -
if ($LASTEXITCODE -ne 0) {
    throw "DEMO_RUN_SESSION_FAILED"
}

$demo = $demoJson | ConvertFrom-Json

if ($demo.warning_intent) {
    Write-Output "WARNING_INTENT=TRUE"
}
if ($demo.halt_for_day) {
    Write-Output "HALT_FOR_DAY=TRUE"
}
if ($demo.halt_all) {
    Write-Output "HALT_ALL=TRUE"
}

Write-Output "FILLS=$($demo.summary.fills)"
Write-Output "WINS=$($demo.summary.wins)"
Write-Output "LOSSES=$($demo.summary.losses)"
Write-Output ("REALIZED_PNL_USD={0:0.00}" -f [double]$demo.summary.realized_pnl_usd)
Write-Output "DAYS_RECORDED_TOWARD_VERDICT=$($demo.summary.days_recorded_toward_verdict)"
