# AIOS Forex Demo Day Runner V11 Fail Closed Report

## Problem Observed

A manually pasted Day Two runner continued after a failure because native PowerShell child commands were not wrapped in explicit exit-code gates. The duplicate-day guard also crashed under StrictMode when older JSONL rows lacked `record_type`, which let orchestration continue into branch and PR logic instead of stopping.

## Root Cause

The orchestration flow relied on downstream script success instead of fail-closed wrappers around native commands such as `git`, `python`, and `pwsh`. The duplicate-day path also needed safe JSONL property inspection so legacy rows without `record_type` would be treated as mock rows instead of causing a strict property-access failure.

## Files Changed

- `tests/forex_engine/test_forex_demo_run_day_recorder_v1.py`
- `Reports/forex_delivery/AIOS_FOREX_DEMO_DAY_RUNNER_V11_FAIL_CLOSED_REPORT.md`

## Verified Existing Files

- `scripts/forex_delivery/Invoke-AiOsDemoDayEvidenceRun.ps1`
- `tests/forex_engine/test_demo_day_evidence_runner_v11_script.py`

## Safety Boundary

- No live broker code was changed.
- No broker calls were added.
- No credentials were read.
- No orders were placed.
- OANDA transport was not altered.
- Strategy logic was not changed.
- The repo telemetry ledger was not modified by the code change itself.

## Duplicate-Day Behavior

- Rows without `record_type` are treated as non-real mock rows.
- A `REAL_DEMO_DAY` row for the current UTC date prints `DAY_EVIDENCE_APPEND_BLOCKED=DUPLICATE_REAL_DEMO_DAY`.
- The duplicate-day path prints `ACTION=VERDICT_ONLY`, runs `Get-AiOsDemoVerdict.ps1`, exits `0`, and does not create a branch, commit, push, or PR.

## Native Command Fail-Closed Behavior

- Added `Invoke-CheckedNative` to gate every native `git`, `python`, and `pwsh` command in the new runner.
- The runner stops on branch mismatch, `index.lock`, fetch/fast-forward failure, dirty or unsynced main, duplicate-day detection, pytest failure, dry-run failure, apply failure, missing ledger diff after append, or post-append scope drift.
- The script uses `PSObject.Properties["record_type"]` instead of direct dot-property access in the duplicate guard.

## Validation Results

- `python -m pytest tests/forex_engine/test_demo_day_evidence_runner_v11_script.py -q` PASS
- `python -m pytest tests/forex_engine/test_forex_demo_run_day_recorder_v1.py -q` PASS
- `python -m py_compile automation/forex_engine/forex_demo_run_day_recorder_v1.py` PASS
- `git diff --check` PASS
- `git status --short --untracked-files=all` PASS

## Notes

- The runner and its source-inspection test were already present in the branch and matched the requested fail-closed contract, so no code diff was needed for those paths.

## Final Owner Command

Run this on the next unused UTC date:

```powershell
pwsh -NoProfile -File scripts/forex_delivery/Invoke-AiOsDemoDayEvidenceRun.ps1
```

## Next Unused UTC Date

Based on the current ledger contents, the next unused UTC date is `2026-07-03`.
