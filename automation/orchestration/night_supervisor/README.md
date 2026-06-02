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
| 3 | `validator_automation` | JSON parse (BOM-tolerant), `git diff --check`, repo integrity, and conditional PowerShell parser proof for configured critical scripts. **Fail-closed** → alert + stop. |
| 4 | `lock_enforcement_automation` | Inspect locks; produce an expired-lock release **plan only**. |
| 5 | `approval_automation` | Classify approval inbox by risk tier. LOW auto-eligible (disabled in DRY_RUN); MEDIUM/HIGH held for human review. |
| 6 | `runtime_state_automation` | Write a **proposed** runtime-state update to the sandbox; active state untouched. |
| 7 | `resume_capability_automation` | Write a resume record for reliable morning startup. |
| 8 | `cleanup_and_ledger` | Temp-cleanup plan (nothing deleted) + append-only nightly ledger event. |
| 9 | `reporting_and_alerting` | Write nightly summary report; flag CRITICAL alerts for morning review. |
| 10 | `safety_enforcement` | Confirm no forbidden writes, no active-state mutation, no secrets, no trading. |

## Execution result closeout

Each Night Supervisor report includes one `execution_result` object that closes
the operator question "what happened overnight?" without redesigning the
supervisor.

The object connects:

- worker assignment: `worker_id` and `worker_lane` from selected packet evidence.
- packet selection: `packet_selected`, `packet_id`, `packet_name`, `packet_path`,
  and `packet_status`.
- validator result: `validator_status` from the validator automation phase.
- QA result: `qa_status`, derived from validator state, alerts, forbidden writes,
  and safety checks.
- approval requirement: `approval_required`, true when human review is required
  before mutation or protected action.
- final classification: `result_classification`, one of `PASS`, `FAIL`,
  `BLOCKED`, `NEEDS_APPROVAL`, or `NOOP`.

`execution_result.next_safe_action` is the operator-facing stop point. It is
evidence only and never grants APPLY, commit, push, merge, worker launch,
scheduler, broker, OANDA, secret, or live-trading authority.

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
JSON + diff + integrity validation, conditional PowerShell parser proof with
fail-closed alerting when available, lock inspection, approval-tier
classification, proposed runtime-state, resume records, append-only ledger,
summary report + alerts, in-code safety enforcement.

**Still requires a human / separate approved APPLY packet:** releasing expired
locks, approving LOW-tier packets, mutating active runtime/packet/approval state,
promoting resume records to a canonical path, and any commit/push/merge.

### PowerShell parser proof

On Windows, the Night Supervisor attempts parser-only validation for the
configured critical script list, currently
`automation/orchestration/Invoke-AiOsNightCycle.ps1`. It prefers
`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` when present and
falls back to `pwsh` only when safely discoverable. If neither executable is
available, reports mark PowerShell parse as `DEFERRED_UNAVAILABLE` with a
non-secret reason instead of claiming the parser ran.
