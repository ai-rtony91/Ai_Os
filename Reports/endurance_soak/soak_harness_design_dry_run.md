# Soak Harness Design (DRY_RUN Observe-Only)

## Purpose

This packet implements an observe-only soak harness.
It only reads runtime state and produces local evidence artifacts.
It does not execute workers, does not start any scheduler, and does not run a supervised cycle.

## Non-Scheduler Scope

- The harness does not register any scheduler.
- It does not queue recurring jobs.
- It does not start `Invoke-AiOsNightCycle` or any runtime loop.

## Non-Worker Scope

- The harness does not launch workers.
- It does not claim worker locks.
- It does not start `Start-AiOsWorkerLoop`, `Invoke-AiOsWorker`, or equivalent launch paths.

## Non-Supervised Scope

- This is a DRY_RUN-only packet.
- There is no supervised soak execution.
- It does not touch live trading or external execution paths.

## Marker and Heartbeat Sampling

- The proposal acknowledges `control/cycle/last_marker.json` already exists in this environment.
- The harness reads marker and heartbeat as samples only.
- Marker and heartbeat files are treated as read-only inputs.
- No mutation of existing marker, heartbeat, or runtime-state files is performed.

## Evidence Files

- Evidence JSON is written only under:
  - `telemetry/soak/soak_run_<UTC>.json`
  - `telemetry/soak/soak_run_latest.json`
- Markdown reports are written under:
  - `Reports/endurance_soak/soak_run_<UTC>.md`
- Report generation is deterministic and derived from the evidence payload.

## STOP Behavior

- Before start and before each sample, the harness checks:
  - `control/self_continuation/STOP`
  - `relay/STOP.flag`
- If STOP is active, the run status becomes `STOPPED`, records reasons, writes partial evidence, and exits cleanly.
- If STOP appears mid-run, the current sample is still captured and the run exits with `STOPPED`.

## Runtime Safety Coverage

- Interval minimum: 30 seconds.
- Hard timeout: enforced via `RunTimeoutSeconds`.
- Sample collection is bound to `MaxCycles` and in this first packet is limited to `1`.
- Output is written with collision-safe temporary files in allowed roots only.
- Forbidden action confirmations are included in evidence.

## Test and Validator Coverage

- Static and schema validation for the two harness scripts and the validator:
  - `tests/orchestration/test_soak_harness.py`
  - `tests/orchestration/test_soak_evidence_schema.py`
- Evidence schema validation:
  - `python automation/validators/aios_soak_evidence_validator.py --sample-check --json`

## Next Safe Action

Run the report and validator commands from the local workspace, confirm PASS, and then request a separate approval packet for supervised execution.
