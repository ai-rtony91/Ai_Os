# AI_OS Worker Task Lifecycle Standard

Status: canonical workflow

## Purpose

This document defines the canonical queue/status lifecycle for AI_OS worker tasks.

The lifecycle keeps worker activity bounded, reviewable, and safe. It separates task intake, ownership checks, read-only preview, validation, human approval, APPLY, review, and completion.

This file is the canonical authority for operator-facing queue status. Worker inboxes, operator queues, work packets, approval inboxes, queue runners, reports, and dashboards should project this lifecycle through `current_status` instead of inventing separate command-state vocabularies.

## Authority Boundary

Worker lifecycle state is workflow evidence. It does not approve APPLY, commit, push, merge, deployment, broker execution, live trading, secret handling, or any protected action.

A worker, runner, queue, packet, or validator may recommend a next safe action. Only the user can approve APPLY or other protected actions.

Approval status is separate from queue status. The lifecycle answers "where is this task in the queue?" Approval status answers "has the operator approved the gated action?"

## Lifecycle Overview

A controlled worker task should move through this general path:

```text
user goal
-> intake packet
-> task classification
-> ownership check
-> blocked path check
-> task queue
-> runner preview
-> validator selection
-> output summary
-> next safe action
-> human approval when required
```

The runner previews what would happen. The validator checks whether rules are broken. The user approves before APPLY, commit, push, install, integration, or risky action.

## Standard Task States

Worker tasks must use this exact canonical lifecycle list for `current_status`:

- `proposed`: A task idea exists, but it is not ready to run.
- `queued`: The task has enough fields to enter the queue.
- `ownership_checked`: The assigned worker is allowed to own this lane.
- `blocked_path_checked`: The task paths were checked against blocked paths.
- `ready_for_runner_preview`: The task is safe enough for read-only preview.
- `runner_previewed`: A read-only preview has been produced.
- `ready_for_apply`: The task is ready for user approval before APPLY.
- `apply_completed`: Approved file changes were made inside approved scope.
- `validation_running`: A validator is running or should run next.
- `validation_passed`: The validator passed.
- `validation_failed`: The validator failed.
- `ready_for_review`: The user should review the result.
- `done`: The task is complete.
- `blocked`: The task requested a blocked action.
- `deferred`: The task is unclear or should wait.

Workers should not invent new state names without an approved update to this standard.

## Operator Queue Item Fields

Operator-facing queue items should preserve enough structure for humans, workers, reports, and dashboards to read the same task state without granting command authority.

Required queue item fields:

- `task_id`
- `title`
- `created_utc`
- `updated_utc`
- `source`
- `lane`
- `assigned_worker`
- `task_type`
- `objective`
- `allowed_paths`
- `blocked_paths`
- `current_status`
- `approval_status`
- `validation_required`
- `validation_command`
- `next_action`

Optional queue item fields:

- `phase`
- `stage`
- `priority`
- `repo`
- `branch`
- `worktree`
- `owner_lane`
- `required_inputs`
- `expected_outputs`
- `safety_status`
- `blocked_reason`
- `user_approval_required`
- `output_summary_path`
- `validation_report_path`
- `related_files`
- `related_packets`
- `notes`
- `legacy_status`
- `legacy_state`

If a required value is not known at intake time, keep the field and set the value to `UNKNOWN`. Do not remove useful existing metadata to fit this model.

## Approval Status Values

Approval status must stay separate from `current_status`.

Use these approval status values:

- `NOT_REQUIRED`: No operator approval is required for the current read-only or report-only step.
- `PENDING`: Operator approval is required before continuing.
- `APPROVED`: The operator approved the exact mode, files, paths, and action.
- `DENIED`: Approval was denied or not granted.
- `EXPIRED`: A prior approval is stale and must be renewed.

Approval status must not be used as a lifecycle state. `APPROVED` does not mean `ready_for_apply`, and `done` does not imply approval for commit, push, merge, deployment, or any other protected action.

## Legacy Field Mapping

Existing producers may have older status fields. They should be projected into `current_status` without deleting the legacy evidence until the owning producer is updated in a separate approved lane.

| Source | Legacy field | Canonical projection |
|---|---|---|
| Worker inbox | `status: complete` | `current_status: done` |
| Worker inbox | `status: active` | `current_status: queued` unless a more specific lifecycle state is known |
| Worker inbox | `status: blocked` | `current_status: blocked` |
| Worker inbox | `status: deferred` | `current_status: deferred` |
| Operator queue | top-level `status` | Queue/schema lifecycle marker only; item state belongs in `current_status` |
| Work packet | `status` | Preserve as `legacy_status`; add `current_status` for operator-facing queue state |
| Approval inbox | approval result/status | Map only to `approval_status`; do not map approval to `current_status` |
| Queue runner | preview/result state | Project read-only progress through `current_status`, usually `runner_previewed`, `validation_running`, `validation_passed`, `validation_failed`, or `blocked` |

When a legacy value cannot be safely mapped, use `current_status: deferred` and include the unresolved source value in `legacy_status`, `legacy_state`, `blocked_reason`, or `notes`.

## State Transition Rules

Task transitions should follow these rules:

- `proposed -> queued` only after the task has required fields.
- `queued -> ownership_checked` only if the assigned worker exists or is explicitly approved.
- `ownership_checked -> blocked_path_checked` only if the assigned worker owns the lane or has an approved handoff.
- `blocked_path_checked -> ready_for_runner_preview` only if no blocked path or blocked action was requested.
- `ready_for_runner_preview -> runner_previewed` after read-only preview.
- `runner_previewed -> ready_for_apply` only when edits are needed and human approval is pending.
- `ready_for_apply -> apply_completed` only after approved APPLY.
- `apply_completed -> validation_running` when a validator command is selected.
- `validation_running -> validation_passed` when validation passes.
- `validation_running -> validation_failed` when validation fails.
- `validation_passed -> ready_for_review` after summary and next safe action are written.
- `ready_for_review -> done` after human review is complete.

Unsafe requests move to `blocked`. Unclear requests move to `deferred` or `ready_for_review`, not APPLY.

## Deferred And Blocked Work Rules

Use `deferred` when:

- scope is unclear.
- ownership is unclear.
- required inputs are missing.
- validation cannot be selected.
- the next safe action is not known.

Use `blocked` when:

- the task requests a protected action without approval.
- the task requests live trading, broker execution, OANDA, API keys, secrets, real webhooks, real orders, background execution, startup persistence, scheduled automation, account login systems, financial claims, or profitability guarantees.
- the task requests edits outside allowed paths.
- the task attempts to bypass validation or human approval.

Blocked work must include a blocked reason and one next safe recovery step.

## Handoff Packet Requirements

A worker handoff packet should include:

- `task_id`
- `packet_id`
- `identity_marker`
- `supervisor_identity`
- `worker_identity`
- `zone`
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
- `approval_authority`
- `validator_chain`
- `lock_id`
- `required_inputs`
- `expected_outputs`
- `validation_required`
- `validation_command`
- `current_status`
- `safety_status`
- `blocked_reason`
- `user_approval_required`
- `next_action`
- `stop_point`
- `output_summary_path`
- `validation_report_path`

If a value is unknown, mark it `UNKNOWN`. Do not invent fields or facts to make a packet look complete.

## Safety Status Values

Worker lifecycle safety status should use these values:

- `SAFE_LOCAL_ONLY`: Work is local and does not request protected actions.
- `PAPER_ONLY`: Work is limited to paper-only simulation, planning, fixtures, or analysis.
- `REVIEW_REQUIRED`: Work needs human review before continuing.
- `BLOCKED`: Work requested a blocked action or lacks required safety evidence.

## Blocked Action Matrix

The following categories are blocked unless a future approved canonical document explicitly changes the boundary:

| Category | Status |
|---|---|
| Live trading | `BLOCKED` |
| Broker execution | `BLOCKED` |
| OANDA execution | `BLOCKED` |
| API keys | `BLOCKED` |
| Secrets | `BLOCKED` |
| Real webhooks | `BLOCKED` |
| Real orders | `BLOCKED` |
| Background execution | `BLOCKED` |
| Scheduled automation | `BLOCKED` |
| Startup persistence | `BLOCKED` |
| Account login systems | `BLOCKED` |
| Payments | `BLOCKED` |
| Financial claims | `BLOCKED` |
| Profitability guarantees | `BLOCKED` |
| External LLM framework install | `NOT_ENABLED` |

Blocked actions must not be routed into APPLY.

## Runner DRY_RUN Preview Rules

A runner preview is read-only. It must not edit target files, install packages, call the internet, start background work, touch secrets, trade, or connect to brokers.

Dirty generated evidence, reports, and sandbox previews may remain present during READ_ONLY or DRY_RUN preview when the dirty tree classifier marks every dirty file safe for DRY_RUN. That classification never approves APPLY. Unknown dirty files require review, protected authority dirty files stop, and security indicators require SOS escalation.

A runner preview should:

1. Select one task only.
2. Confirm the assigned worker exists or is explicitly approved.
3. Check worker lane ownership.
4. Check allowed paths.
5. Check blocked paths.
6. Check blocked words and actions.
7. Verify required input files exist when they are real paths.
8. Verify validation command exists or is explicitly planned.
9. Print or write a preview result only when output is approved for that path.
10. Recommend one next safe action.

The runner may say a task appears ready for APPLY review, but it cannot approve APPLY.

## Relationship To APPLY Routing

This lifecycle standard supports `docs/workflows/APPLY_ROUTING_CHAIN.md`.

Lifecycle state explains where a task is. APPLY routing explains how a DRY_RUN item becomes an APPLY candidate without removing operator control.

A task is not an APPLY candidate until scope, ownership, blocked paths, validation, and human approval requirements are clear.

## Relationship To Validator Execution Standard

This lifecycle standard works with `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`.

Lifecycle state determines when validation should run. Validator output provides evidence. Validator output does not approve APPLY, commit, push, merge, or protected actions.

## Relationship To Approval Model

This lifecycle standard supports `docs/security/approval-model.md`.

All worker and runner activity defaults to DRY_RUN. APPLY requires explicit human approval naming the intended files, intended change, expected validation, and rollback path where applicable.

## Stop Conditions

Stop and report when:

- current branch or repo root cannot be verified.
- task scope is unclear.
- ownership is unclear.
- required inputs are missing.
- blocked paths or blocked actions appear.
- validation command is missing or unknown.
- validation fails.
- evidence conflicts with current repo state.
- a protected action lacks approval.
- a runner attempts to mutate files.
- a worker attempts to self-approve APPLY.
- next safe action is missing.
- identity, supervisor, worker, zone, lane, approval authority, validator chain, or stop point is missing from an executable packet.
- East/West ownership overlaps without explicit reassignment and lock review.

## Next Safe Action Requirement

Every lifecycle state update, runner preview, blocked task, deferred task, and completed task must provide one next safe action.

The next safe action should be one of:

- an exact validation command.
- an exact DRY_RUN prompt.
- an exact APPLY prompt after approval.
- a review instruction.
- a checkpoint instruction.
- a stop point.

The next safe action must not be commit, push, merge, deployment, live trading, broker execution, secret handling, auto-repair, or uncontrolled automation unless the user has separately approved that protected action.
