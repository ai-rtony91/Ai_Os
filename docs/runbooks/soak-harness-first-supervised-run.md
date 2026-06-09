# Runbook: First Supervised Soak Evidence Harness (Human-Run)

This runbook is human-run only and does **not** approve execution.
It documents the steps for a single DRY_RUN-observe soak evidence run.

## 1) Preconditions

- Confirm the working tree and branch are aligned as expected for local apply review.
- Confirm `control/cycle/last_marker.json` exists and is treated read-only.
- Confirm `telemetry/runtime/runtime_heartbeat.json` is present or intentionally missing.
- Confirm no stop marker is active:
  - `control/self_continuation/STOP`
  - `relay/STOP.flag`
- Confirm there is no active packet execution from `automation/orchestration/work_packets/active`.

## 2) Preflight checklist

- `automation/orchestration/soak/Invoke-AiOsSoakHarness.DRY_RUN.ps1` present.
- `automation/orchestration/soak/New-AiOsSoakEvidenceReport.DRY_RUN.ps1` present.
- `automation/orchestration/soak/Get-AiOsSoakSamples.DRY_RUN.ps1` present.
- `Reports/endurance_soak/soak_evidence_report.example.json` present.
- `automation/validators/aios_soak_evidence_validator.py` present.

## 3) Execution command (local DRY_RUN only)

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/soak/Invoke-AiOsSoakHarness.DRY_RUN.ps1 `
  -MaxCycles 1 `
  -IntervalSeconds 30 `
  -RunTimeoutSeconds 600
```

## 4) What this run proves

- Marker and heartbeat are sampled read-only.
- STOP markers are checked before start and each sample.
- Evidence is written to:
  - `telemetry/soak/soak_run_<UTC>.json`
  - `telemetry/soak/soak_run_latest.json`
- Evidence report is written to:
  - `Reports/endurance_soak/soak_run_<UTC>.md`
- Forbidden actions were not used in this packet design (scheduler/worker launch/notifications).

## 5) What it does not prove

- It does not run a supervised execution cycle.
- It does not start scheduler, worker loop, alerting, SOS/ADB, or external integrations.
- It does not validate live trading execution behavior.

## 6) STOP behavior

- If STOP markers are detected, run status becomes `STOPPED`.
- A partial evidence/report package is still written for review.
- The run exits cleanly without worker launch.

## 7) Validator chain

- `powershell` parse checks for new `.ps1` files.
- `python automation/validators/aios_soak_evidence_validator.py --sample-check --json`.
- Targeted pytest:
  - `tests/orchestration/test_soak_harness.py`
  - `tests/orchestration/test_soak_evidence_schema.py`

## 8) Evidence locations

- Runtime evidence: `telemetry/soak/`
- Human-readable report: `Reports/endurance_soak/`

## 9) Approval posture

This runbook is not an execution approval.
Only the separate packet approval can authorize further supervised execution.
