# AIOS_REPORTING_AND_CHECKPOINT_STANDARD

## PURPOSE

Defines standard reporting and checkpoint methodology for AI_OS.

Reports and checkpoints are evidence. They preserve what happened, what was validated, what failed, what changed, and what the next safe action is. They do not approve execution, replace operator approval, or authorize automation.

## CURRENT STATUS

Status label: `PARTIAL / Evidence-Only`

AI_OS has reporting and checkpoint conventions, but telemetry-backed checkpointing remains incomplete. Current checkpoint and telemetry records must be treated as audit evidence only until canonical schema reconciliation and validator coverage are implemented.

Dashboard, runtime, replay, and summary views may display checkpoint evidence only as derived status. They must not become command authority.

## REQUIRED REPORT ELEMENTS

- Date
- Stage
- Status
- Actions taken
- Files changed
- Validation results
- Errors encountered
- Risk observations
- Next steps
- Progress percentage
- Actor or worker identity when known
- Lane and branch when applicable
- Source evidence reference
- Output evidence reference
- Approval or authority reference when applicable

## REPORT TYPES

- DAILY_REPORT
- CHECKPOINT
- HEALTH_REPORT
- VALIDATOR_REPORT
- INCIDENT_REPORT
- AAR

## DAILY DATA SNAPSHOT REQUIREMENT

Every future AI_OS auto-update, checkpoint, backup, and daily status/report should include a `DAILY DATA SNAPSHOT` section sourced from `automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1`.

Required fields:

- date/time
- repo path
- current HEAD
- files changed/generated today
- artifact count
- folder count
- total bytes/KB/MB collected today
- backup size if backup ran
- skipped secrets count
- validation/governance status
- success/failure

The snapshot is evidence only. It does not approve APPLY, commit, push, merge, or runtime behavior. Consumers should reuse the shared snapshot script rather than creating a second reporting system.

## CHECKPOINT TYPES

AI_OS checkpoint records should use controlled checkpoint types:

| Checkpoint Type | Required When | Purpose |
|---|---|---|
| `pre_execution_checkpoint` | Before an approved APPLY, validation, PR, or recovery action | Preserve starting state, authority, scope, and stop conditions. |
| `post_execution_checkpoint` | After an approved action completes | Preserve files changed, result, validation state, and next safe action. |
| `validation_checkpoint` | When validators, tests, diffs, or checks are run | Preserve validation evidence and whether the result is `PASS`, `WARN`, `FAIL`, `BLOCKED`, or `PARTIAL`. |
| `pr_checkpoint` | When a PR is created, checked, blocked, or merged | Preserve branch, PR, commit, check, and review evidence. |
| `recovery_checkpoint` | When a command, tool, validation, GitHub action, or workflow blocks or fails | Preserve what failed, why it failed, what happens next, and where to reference authority. |
| `end_of_day_checkpoint` | At the close of a work session or operating day | Preserve final state, known backlog, unresolved risk, and next safe queue. |

## CHECKPOINT REQUIRED FIELDS

Each checkpoint should include:

- `checkpoint_id`
- `checkpoint_type`
- `timestamp_utc`
- `actor`
- `lane`
- `repo_path`
- `branch`
- `mode`
- `authority_reference`
- `source_evidence`
- `output_evidence`
- `files_changed`
- `validation_status`
- `result`
- `risk_level`
- `next_safe_action`

If a field is not available, the checkpoint should state `UNKNOWN`, `null`, or `requires implementation review`. Checkpoints must not invent authority.

## REPORTING RULES

- Preserve chronological evidence.
- Prefer human-readable summaries.
- Avoid oversized spreadsheet cells.
- Maintain deterministic formatting.
- Preserve DRY_RUN vs APPLY distinction.
- Identify whether evidence is mock, fixture, replay, read-only, or live.
- Link validation evidence to the action it validates.
- Preserve blocked-action evidence and failure recovery evidence.
- Do not overwrite prior evidence to hide failed or partial results.
- Do not treat dashboards, summaries, or replay views as authority.

## REQUIRED VALIDATION BEFORE CHECKPOINT

Before marking a checkpoint complete, record the applicable validation evidence:

- Git status verification
- File existence verification
- Validator completion
- Diff review
- Push verification when push is in scope
- PR/check verification when PR work is in scope
- Final clean-state or known-backlog verification

If validation is incomplete, the checkpoint status must be `PARTIAL`, `BLOCKED`, or `requires implementation review`; it must not claim completion.

## TELEMETRY ALIGNMENT

Telemetry-backed checkpoints must align with `docs/governance/telemetry-contract.md`.

Checkpoint events are evidence events. They must not:

- trigger automation by themselves;
- approve APPLY, commit, push, merge, dashboard wiring, runtime launch, worker loops, or trading behavior;
- mask failed validations;
- overwrite or delete evidence;
- treat mock or fixture records as live operational evidence.

Future telemetry must support chronological reconstruction, worker accountability, PR and branch traceability, validation evidence, blocked-action evidence, failure recovery evidence, and dashboard status provenance.

## FUTURE TELEMETRY GOALS

- Automated metrics
- Session duration
- Progress tracking
- Character-count telemetry
- Report aggregation
- Snapshot indexing
- Checkpoint event validation
- Ledger validation command
- Dashboard status provenance after schema validators are stable

## CURRENT RESTRICTION

Telemetry persistence remains non-production and approval-gated.

Telemetry and checkpoint status remains `PARTIAL / Evidence-Only` until:

1. canonical telemetry schema reconciliation is implemented;
2. checkpoint event shape is validated;
3. ledger validation is available;
4. dashboard consumers can prove source event provenance;
5. operator approval remains separate from telemetry records.

The next safe implementation PR should add telemetry event validation, canonical schema reconciliation, and ledger validation before any dashboard live wiring or automation expansion.
