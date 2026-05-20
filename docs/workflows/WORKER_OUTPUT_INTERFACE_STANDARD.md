# AI_OS Worker Output Interface Standard

Status: canonical workflow

## Purpose

This document defines how AI_OS workers should present output, authority, handoff data, approval state, findings, escalation, and next safe action.

Worker output must make the current task state readable at a glance. A human operator or future worker should be able to answer:

- Who produced this output?
- Under whose authority?
- What mode is active?
- What scope was inspected or changed?
- What findings matter?
- What approval is required?
- What is the next safe action?

## Authority Boundary

Worker output is evidence and communication. It is not independent authority.

Terminal output, logs, dashboard panels, reports, and handoff packets must not override `AGENTS.md`, `README.md`, active `docs/governance/` authority, or active workflow and security standards.

Workers and supervisors may recommend actions, summarize evidence, and request approval. They must not approve protected actions for themselves or for other workers.

Only the user can approve APPLY, protected edits, commit, push, merge, deployment, broker execution, live trading, secret handling, or a change to current authority.

## Required Identity Header

Every worker output should begin with an identity header that includes:

- worker name.
- worker role.
- authority chain.
- session or timestamp when available.
- execution mode.
- approval state.
- scope summary.

The authority chain must trace back to the user. If the chain cannot be verified, the worker must stop and mark the output `BLOCKED` or `UNKNOWN`.

## Execution Mode Labels

Worker output should use these execution mode labels:

- `DRY_RUN`: Preview, inspection, planning, or validation only. No file changes.
- `APPLY`: Approved file changes or approved action inside exact scope.
- `BLOCKED`: A prohibited or unsafe action was requested and did not proceed.
- `PAUSED`: The worker reached a checkpoint and is waiting for instruction.
- `SKIPPED`: An in-scope action was intentionally not performed because a dependency, approval, or safety condition was missing.

Workers must not default to APPLY. Any output involving file changes must make APPLY approval visible before work proceeds.

## Approval State Labels

Worker output should use these approval state labels:

- `NOT_REQUIRED`: No approval is required for the current DRY_RUN output.
- `PENDING`: Approval is required before continuing.
- `APPROVED`: The user approved the exact mode, file, path, and action.
- `DENIED`: Approval was denied or not granted.
- `EXPIRED`: Prior approval is stale and must be renewed before continuing.

Supervisor delegation is not approval for protected actions.

## Required Output Regions

Substantial worker output should include these regions in order:

1. Identity header.
2. Scope declaration.
3. Execution result.
4. Findings.
5. Audit trail.
6. Approval gate.
7. Next safe action.

Short responses may compress the format, but they must still preserve identity, mode, scope, findings, approval needs, and next safe action when those items are relevant.

## Findings And Severity Display

Findings should be short, evidence-based, and ordered by severity.

Use these labels where applicable:

- `PASS`
- `REVIEW`
- `WARNING`
- `FAIL`
- `BLOCKED`
- `UNKNOWN`
- `MISMATCH`
- `INVALID DATA`

Critical findings such as `FAIL`, `BLOCKED`, `MISMATCH`, and `INVALID DATA` should appear before warnings and passes.

No color, icon, or visual treatment may be the only carrier of meaning. Plain text must remain clear without styling.

## Audit Trail Requirements

Worker output should record enough audit detail for the next worker or user to understand what happened.

Audit detail should include:

- files inspected.
- files changed, if any.
- commands run.
- validation result.
- protected files encountered.
- approval state.
- errors.
- unknowns.
- commit status.
- push status.

If a write occurred, the output must identify the file path and the approved scope.

## Approval Gate Display

When approval is required, output must make the gate explicit.

An approval request should name:

- requested mode.
- exact files or paths.
- intended action.
- expected validation.
- rollback or recovery path when applicable.
- stop condition.

An approval gate must not be hidden in prose. It should be easy to find before any APPLY, protected edit, commit, push, merge, deployment, broker action, live trading action, secret handling, or authority change.

## Next Safe Action Display

Every worker output must end with one next safe action or an explicit stop point.

The next safe action should be one of:

- exact validation command.
- exact DRY_RUN prompt.
- exact APPLY prompt after approval.
- exact review instruction.
- exact checkpoint instruction.
- exact recovery step.
- stop point.

The next safe action must not bypass approval, validation, protected boundaries, or active authority.

## Authority Chain And Delegation Display

Delegated worker output must show the authority path back to the user.

The authority display should identify:

- current worker.
- supervising worker or orchestrator, if any.
- user authority.
- approval gate owner.

If delegation depth is unclear, excessive, or unverifiable, the worker should mark the state `REVIEW` or `BLOCKED` and ask for clarification.

Workers must not operate as autonomous authority. A worker without a traceable human instruction must stop.

## Escalation Rules

Escalate or stop when:

- a `FAIL` or `BLOCKED` finding appears.
- `MISMATCH` or `INVALID DATA` appears.
- protected files or protected actions enter scope.
- trading, broker, OANDA, webhook, live execution, or secret handling enters scope.
- delegation authority is unclear.
- an `UNKNOWN` state cannot be resolved by the current worker.
- approval is missing, stale, or denied.
- validation fails.

Escalation output should include the reason, who should review it, what was attempted, what happened, and the next safe recovery step.

## Autonomous Execution Block

Autonomous execution is not permitted.

If a worker cannot trace its task to a current user instruction and active repo authority, it must:

1. Stop.
2. Mark the state `BLOCKED` or `UNKNOWN`.
3. Report the missing authority chain.
4. Request an explicit user instruction or approved handoff.

## Terminal And Log Formatting Rules

Terminal and log output should be readable, stable, and easy to preserve as evidence.

Use:

- mode label near the top.
- short labels and values.
- one finding per line.
- critical findings first.
- exact paths when relevant.
- plain text that remains meaningful without color.
- no required horizontal scrolling for standard status output.

Use box drawing, color, or dashboard styling only as presentation. Styling must not carry unique meaning that is absent from the text.

## Dashboard Projection Rule

Dashboards may display worker output, validation evidence, lifecycle state, approval state, and next safe action.

Dashboards must not create independent findings, approvals, authority, or workflow state. If dashboard output conflicts with terminal output, logs, active workflow standards, or active governance, the conflict must be marked `MISMATCH` and resolved against active authority.

Dashboard panels should be projections of the same evidence used by terminal and log output, not a separate command source.

## Handoff Packet Display

When a worker produces or summarizes a handoff packet, the output should preserve the key packet fields:

- `task_id`
- `created_time`
- `source`
- `user_goal`
- `phase`
- `stage`
- `lane`
- `assigned_worker`
- `task_type`
- `objective`
- `allowed_paths`
- `blocked_paths`
- `required_inputs`
- `expected_outputs`
- `validation_required`
- `validation_command`
- `current_status`
- `safety_status`
- `blocked_reason`
- `user_approval_required`
- `next_action`
- `output_summary_path`
- `validation_report_path`

Unknown values must be marked `UNKNOWN`. A handoff packet must not invent authority, approval, or evidence.

## Worker Output Schema Future Direction

AI_OS may later define a machine-readable worker output schema.

That schema should mirror the required output regions, lifecycle fields, validator evidence, approval gate, authority chain, audit trail, and next safe action.

The schema should support terminal rendering, log preservation, and dashboard projection from the same evidence source. It must not grant approval or become a separate source of authority.

## Stop Conditions

Workers must stop and report when:

- authority chain is missing or unclear.
- execution mode is missing or inconsistent.
- approval state is missing for protected work.
- scope is unclear.
- findings conflict with evidence.
- dashboard, log, terminal, or packet state conflicts with active authority.
- a worker or supervisor attempts to approve a protected action.
- output implies APPLY without visible approval.
- next safe action is missing.
- protected trading, broker, OANDA, live execution, credential, secret, commit, push, merge, deployment, delete, move, rename, or reset action appears without explicit approval.
