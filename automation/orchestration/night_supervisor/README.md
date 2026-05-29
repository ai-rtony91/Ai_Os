# AI_OS Night Supervisor

Fully automated **nightly** background supervision for AI_OS, built to run
unattended with built-in safety, validation, and telemetry.

> Authority: subordinate to `RISK_POLICY.md` and `AGENTS.md`. This module never
> grants APPLY, commit/push/merge, runtime mutation, trading, or secret-handling
> authority. When this README conflicts with root authority, the stricter rule
> wins.

## What it does (10-phase nightly chain)

| # | Phase | Behaviour |
|---|-------|-----------|
| 1 | `supervisor_bootstrap` | Resolve repo identity; recover the most recent validated runtime snapshot. |
| 2 | `nightly_telemetry_checkpoint` | Capture a read-only runtime snapshot + checkpoint. |
| 3 | `validator_automation` | JSON parse (BOM-tolerant), `git diff --check`, repo integrity. **Fail-closed** → alert + stop. |
| 4 | `lock_enforcement_automation` | Inspect locks; produce an expired-lock release **plan only**. |
| 5 | `approval_automation` | Classify approval inbox by risk tier. LOW auto-eligible (disabled in DRY_RUN); MEDIUM/HIGH held for human review. |
| 6 | `runtime_state_automation` | Write a **proposed** runtime-state update to the sandbox; active state untouched. |
| 7 | `resume_capability_automation` | Write a resume record for reliable morning startup. |
| 8 | `cleanup_and_ledger` | Temp-cleanup plan (nothing deleted) + append-only nightly ledger event. |
| 9 | `reporting_and_alerting` | Write nightly summary report; flag CRITICAL alerts for morning review. |
| 10 | `safety_enforcement` | Confirm no forbidden writes, no active-state mutation, no secrets, no trading. |

## Files

- `night_supervisor_harness.py` — executable, stdlib-only DRY_RUN engine. The
  source of truth for the chain in environments without PowerShell. Enforces the
  sandbox write boundary in code (`SandboxWriter._assert_sandbox`) and fails
  closed on secret-shaped content.
- `Invoke-AiOsNightSupervisor.DRY_RUN.ps1` — house-style **read-only** PowerShell
  preview that mirrors the same plan shape for the Windows orchestration suite.
- `test_night_supervisor.py` — functional tests (chain structure, sandbox
  enforcement, fail-closed secret scan).
- `NIGHT_SUPERVISOR_CONFIG.json` — paths, retention, validation, lock/approval rules.
- `NIGHT_SUPERVISOR_SAFETY_POLICY.json` — blocked actions and fail-closed rules.
- `NIGHT_SUPERVISOR_REPORT.schema.json` — schema for the nightly report.

## Run

```bash
# Full DRY_RUN chain (writes sandbox outputs under telemetry/night_supervisor/)
python3 automation/orchestration/night_supervisor/night_supervisor_harness.py

# Compute without writing
python3 automation/orchestration/night_supervisor/night_supervisor_harness.py --no-emit --quiet

# Tests
python3 -m unittest automation/orchestration/night_supervisor/test_night_supervisor.py

# PowerShell preview (Windows worktree)
pwsh automation/orchestration/night_supervisor/Invoke-AiOsNightSupervisor.DRY_RUN.ps1
```

Exit code is non-zero (`2`) when `supervisor_status == BLOCKED`, so a scheduler
stops the chain on a fail-closed condition instead of proceeding.

## Allowed write paths (hard boundary)

Every runtime write is confined to **`telemetry/night_supervisor/`**. Writes
outside it raise `ForbiddenWriteError` and increment a counter that fails the
run. The scaffold/config files in `automation/orchestration/night_supervisor/`
are authored by hand, not by the running engine.

### Deviation note — resume records

The original packet text suggested `automation/runtime/state/resume/` for resume
records. That path is **outside** the packet's own allowed write list, so resume
records are sandboxed under `telemetry/night_supervisor/resume/`. Promotion to a
canonical runtime location is deferred to a separate approved packet.

## What is automated vs. still manual

**Automated (DRY_RUN, safe):** bootstrap recovery, checkpoint/snapshot capture,
JSON + diff + integrity validation with fail-closed alerting, lock inspection,
approval-tier classification, proposed runtime-state, resume records, append-only
ledger, summary report + alerts, in-code safety enforcement.

**Still requires a human / separate approved APPLY packet:** releasing expired
locks, approving LOW-tier packets, mutating active runtime/packet/approval state,
PowerShell parse validation (no `pwsh` in the Linux container), promoting resume
records to a canonical path, and any commit/push/merge.
