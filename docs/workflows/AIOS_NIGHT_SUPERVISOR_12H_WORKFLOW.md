# AI_OS Night Supervisor 12H Workflow

Status: v1 workflow (reference / prototype). DRY_RUN-first, approval-gated.

> Authority: subordinate to `AGENTS.md` and `automation/orchestration/night_supervisor/`.
> Stricter root rule always wins. Base44 output is reference material only.

## Purpose

Run a single **~12-hour overnight** supervision window in observe-only mode: capture hour-by-hour repo/validator/queue/paper-lab state, raise preview alerts, and prepare a morning build-prep queue — so the operator wakes to a clear brief, not a surprise.

**It does NOT** execute work, mutate active runtime/packet/approval/lock state, auto-approve anything, send real notifications, run a scheduler, or trade live. Every write is sandbox-only; every alert is a preview (`delivered:false`).

## Scope

- Mode: `NIGHT_12H` (`schemas/aios/night_supervisor/aios_supervisor_session.schema.json`).
- One `aios_supervisor_session` containing ordered `aios_supervisor_hour` slices.
- Alerts as `aios_alert_event`; prepared work as `aios_build_prep_item` (capped at `ready_for_runner_preview`).
- Engine of record: `automation/orchestration/night_supervisor/night_supervisor_harness.py` (DRY_RUN).

## Window stages (per hour)

1. **Open hour** — record `window_start`, repo identity (branch/head), clean-state check.
2. **Observe** — read-only snapshots: repo state, validator status, approval inbox, lock state, paper-lab (paper-only).
3. **Validate** — JSON parse, `git diff --check`, repo integrity. Fail-closed → `AIOS_VALIDATOR_FAILED` / `AIOS_BLOCKED`.
4. **Classify alerts** — map observations to `event_type` + severity; set `wake_worthy`. No delivery.
5. **Prep** — append any `aios_build_prep_item` (LOW/MEDIUM); never execute.
6. **Close hour** — write the hour slice (sandbox), advance `hour_index`.

At window end: write the session summary + morning brief; flag wake-worthy alerts for review.

## Lifecycle

Build-prep items use canonical states from `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`, capped at
`ready_for_runner_preview`. `approval_status` is independent and never grants APPLY.

## Authority boundary / stop conditions

- Stop + alert on validator FAIL, repo/branch mismatch, secret suspicion, or forbidden-write attempt.
- MEDIUM/HIGH approvals are **held** for human review (no auto-approval, even LOW, in DRY_RUN).
- Promotion of any prep item to APPLY requires a separate approved packet.

## References

`AIOS_NIGHT_SUPERVISOR_12H_24H_VACATION_ARCHITECTURE.md` · `AI_OS_OVERNIGHT_SUPERVISOR_WORKFLOW.md` ·
`AIOS_BUILD_PROGRESS_SOS_ALERT_WORKFLOW.md` · `NIGHT_SUPERVISOR_SAFETY_POLICY.json`.
