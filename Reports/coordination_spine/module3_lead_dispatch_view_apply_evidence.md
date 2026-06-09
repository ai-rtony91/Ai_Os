# Module 3 Lead Dispatch View Apply Evidence

## Summary

Module 3 adds a DRY_RUN-default lead dispatcher composer under `automation/orchestration/coordination_spine/`.
It reads the existing dispatcher decision source, combines it with the queue, lock, and recovery telemetry views, and emits a telemetry-only lead dispatch view.

## Files

- `automation/orchestration/coordination_spine/Get-AiOsLeadDispatchView.DRY_RUN.ps1`
- `tests/orchestration/test_lead_dispatch_view.py`
- `telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json`
- `Reports/coordination_spine/module3_lead_dispatch_view_apply_evidence.md`

## Decision Model

- No queue candidates produces `SAFE_NO_WORK`.
- Queue blocked, lock review-required/collision, or recovery blocked produces `BLOCKED`.
- Dispatcher source recommendations are reported as evidence only.
- T2B remains a prerequisite note only and is not executed.

## Safety

- No assignment write-path calls.
- No lock claim or release calls.
- No approval mutation.
- No queue mutation.
- No T2B execution.
- No orchestrator created.
- No scheduler, SOS, ADB, dashboard, broker, webhook, or secret behavior.

## Validation

- Governance validator on `automation/orchestration/work_packets/proposed/AIOS-COORDINATION-SPINE-V1.md`
- PowerShell parser check for the new `Get-AiOsLeadDispatchView.DRY_RUN.ps1`
- Pytest for `tests/orchestration/test_lead_dispatch_view.py`
- JSON parse validation for `telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json`
- `git diff --check`

## Notes

- The telemetry output is atomic-write capable through a temp-file-then-rename pattern.
- `-Apply` is restricted to `telemetry/coordination_spine/LEAD_DISPATCH_VIEW.json`.
