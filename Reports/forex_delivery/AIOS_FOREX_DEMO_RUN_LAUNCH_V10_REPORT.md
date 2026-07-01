# AIOS Forex Demo Run Launch V10 Report

## Purpose
Connect the existing paper signal loop, the real-day recorder, and the owner-facing verdict countdown into one daily demo launch seam.

## What Was Built
- `scripts/forex_delivery/Start-AiOsDemoRun.ps1`
- `scripts/forex_delivery/Get-AiOsDemoVerdict.ps1`
- `tests/forex_engine/test_forex_demo_run_day_recorder_v1.py`
- `automation/forex_engine/forex_demo_run_day_recorder_v1.py` was reused as the real-day recorder seam.

## Safety Boundary
- No broker API calls.
- No live endpoints.
- No orders.
- No money movement.
- No credential storage.
- `OANDA_PRACTICE_TOKEN` is checked only by presence and is never printed.
- `-DryRun` performs the full preflight and session preview without appending the real-day ledger.

## Recorder Semantics
- `record_type=REAL_DEMO_DAY` is the only counted real evidence row.
- `telemetry/forex/demo_proof_ledger.jsonl` remains append-only.
- The 3 existing mock lines stay in place and are marked superseded-by-real-run in the verdict output, not deleted and not counted.
- `WINDOWS` is treated as distinct ISO week buckets among real demo days. This is an inference from the existing cadence tooling.

## Owner Commands
```powershell
pwsh -NoProfile -File scripts/forex_delivery/Start-AiOsDemoRun.ps1
```

```powershell
pwsh -NoProfile -File scripts/forex_delivery/Get-AiOsDemoVerdict.ps1
```

## Broker Scope Review
- `Reports/forex_delivery/AIOS_FOREX_BROKER_PROBE_SCOPE_REVIEW_V1.md` stays value-free and leaves the APPROVE/HOLD/ADJUST block unsigned.
- The probe review scope is read-only and future-facing only.

## Validation
- `python -m py_compile automation/forex_engine/forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py tests/forex_engine/test_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py automation/forex_engine/forex_brake_trip_proof_v1.py tests/forex_engine/test_forex_brake_trip_proof_v1.py automation/forex_engine/forex_demo_run_day_recorder_v1.py tests/forex_engine/test_forex_demo_run_day_recorder_v1.py`: PASS.
- `python -m pytest tests/forex_engine/test_forex_demo_run_day_recorder_v1.py -q`: PASS, 3 passed in 0.24s.
- `python -m pytest tests/forex_engine -q`: PASS, 13353 passed in 156.23s.
- `pwsh -NoProfile -File scripts/forex_delivery/Start-AiOsDemoRun.ps1 -DryRun`: PASS, printed `FILLS=1`, `WINS=1`, `LOSSES=0`, `REALIZED_PNL_USD=1.20`, `DAYS_RECORDED_TOWARD_VERDICT=1`.
- `pwsh -NoProfile -File scripts/forex_delivery/Get-AiOsDemoVerdict.ps1`: PASS, printed `DAYS_RECORDED=0`, `TRADES_ACCUMULATED=0`, `WINDOWS=0`, `EVIDENCE_AGE_OK=false`, `CURRENT_EXPECTANCY=0.0`, `CURRENT_PROFIT_FACTOR=0.0`, `DAYS_UNTIL_VERDICT_POSSIBLE=30`, `VERDICT_STATUS=EARNING`, `MOCK_ENTRIES_SUPERSEDED_BY_REAL_RUN=3`.
- `python -m json.tool telemetry/forex/brake_trip_proof_ledger.jsonl`: PASS.
- `git diff --check`: PASS.
- `git status --short --untracked-files=all`: PASS, tree remains dirty with the expected prior V9 files plus the new V10 launch files.

## Files Touched
- `automation/forex_engine/forex_demo_run_day_recorder_v1.py`
- `automation/forex_engine/forex_brake_trip_proof_v1.py`
- `scripts/forex_delivery/Start-AiOsDemoRun.ps1`
- `scripts/forex_delivery/Get-AiOsDemoVerdict.ps1`
- `Reports/forex_delivery/AIOS_FOREX_BROKER_PROBE_SCOPE_REVIEW_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_BRAKE_TRIP_PROOF_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_DEMO_RUN_LAUNCH_V10_REPORT.md`
- `tests/forex_engine/test_forex_demo_run_day_recorder_v1.py`
- `tests/forex_engine/test_forex_brake_trip_proof_v1.py`
- `telemetry/forex/brake_trip_proof_ledger.jsonl`

## Mode Available
- `PAPER_SIMULATION` now.
- `OANDA_PRACTICE` only after the owner signs the broker probe scope.

## Notes
- The existing V9 governor and safety files remain dirty in the worktree from the prior lane and were not rewritten in this turn.
- The broker probe scope review stays unsigned; no broker call or credential read was performed.
