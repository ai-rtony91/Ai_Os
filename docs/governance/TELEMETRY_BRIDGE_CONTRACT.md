# Telemetry Bridge Contract

Date: 2026-06-01
Packet: AIOS-P25

## 1. Purpose

The telemetry bridge exports Python supervisor runtime visibility into JSON files under `telemetry/runtime/` so local orchestrator and dashboard readers have a stable read-only source.

## 2. Source: Python Supervisor

Source function: `services/python_supervisor/supervisor_engine.py::build_supervisor_report`.

The exporter imports this function only during export execution. It does not edit supervisor code and does not change supervisor authority.

## 3. Transform: runtime_state_exporter.py

Transform script: `services/python_supervisor/runtime_state_exporter.py`.

It converts supervisor report fields into runtime visibility state, heartbeat, and process stub payloads. DRY_RUN is the default; `--apply` is required before files are written.

## 4. Runtime Output Files

Output files:

- `telemetry/runtime/runtime_state.json`
- `telemetry/runtime/runtime_heartbeat.json`
- `telemetry/runtime/runtime_process.json`

These files are runtime visibility artifacts. They are evidence and status inputs, not approval authority.

## 5. Dashboard/Orchestrator Consumer Path

Dashboard client default API URL: `/api/runtime/visibility`.

The orchestrator service reads `telemetry/runtime/runtime_state.json`, `runtime_heartbeat.json`, and `runtime_process.json`, then serves runtime status, health, and visibility snapshots through `services/orchestrator/runtimeApiService.js` and `services/orchestrator/index.js`.

## 6. Apply Gate Behavior

`runtime_state_exporter.py` prints a JSON receipt in both DRY_RUN and APPLY. It writes files only when `--apply` is provided. The PowerShell wrapper `automation/orchestration/supervisor/Export-AiOsRuntimeState.DRY_RUN.ps1` passes `--apply` only when called with `-Apply`.

## 7. Forbidden Writes

The exporter must never write `telemetry/work_ledger.jsonl`, dashboard source, orchestrator source, supervisor source, approval files, active packet files, Trading Lab files, broker paths, OANDA paths, credentials, secrets, webhooks, or execution files.

## 8. What P25 Does Not Cover

P25 does not complete all AI_OS telemetry. It does not start services, wire dashboard UI behavior, append the work ledger, run broker workflows, or make runtime state authoritative for approval.

## 9. Future Telemetry Packets Still Needed

Future packets should connect validator receipts, approval receipts, clean-state verification, commit-package status, and runtime loop history into governed telemetry with retention rules.

## 10. Packet Reference

AIOS-P25 creates telemetry bridge v1 on 2026-06-01. Human approval remains required for protected actions.
