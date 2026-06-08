# Worker Dispatcher Next Packet Draft Builder V1

## Purpose

The Dispatcher Next Packet Draft Builder is part of the Worker Dispatcher
Assignment Executor. It turns dispatcher decisions into Codex-shaped packet
drafts for Anthony review.

It does not execute drafts, launch workers, approve APPLY, approve commit,
approve push, approve merge, wake Anthony, send notifications, start scheduler,
start Night Supervisor, arm SOS, call ADB, touch broker/cloud/live trading, or
handle secrets.

## Inputs

Drafts are built from Dispatcher evidence:

- dispatcher decisions
- active-state contracts
- PR backlog classifications
- PR dependency findings
- collision findings
- lock state
- approval state
- internal walkie events

## Draft Statuses

- `DRAFT_READY_FOR_OPERATOR_REVIEW`
- `DRAFT_BLOCKED_WAITING_APPROVAL`
- `DRAFT_BLOCKED_BY_LOCK`
- `DRAFT_BLOCKED_BY_PR_DEPENDENCY`
- `DRAFT_BLOCKED_BY_PROTECTED_PATH`
- `DRAFT_REVIEW_REQUIRED`
- `DRAFT_NOT_CREATED`

## Safety Model

Drafts prefer `DRY_RUN` and include:

- source dispatcher decision
- source candidate
- source walkie event IDs
- source PR dependency status
- source lock status
- source approval status
- source collision status
- zero worker launch confirmation
- not-approval notice
- not-executable-until-operator-approval flag

The rendered text includes `CODEX-ONLY PROMPT` so it is visually recognizable as
a Codex packet draft, but uses `AI_OS EXECUTION TOKEN:
DRAFT_ONLY_NOT_OPERATOR_APPROVAL`. Anthony must approve, edit, reject, or run a
separate executable packet manually.

## Approval Boundary

Validator PASS, GitHub check PASS, PR mergeability, Dispatcher decision output,
internal walkie events, and packet drafts are evidence only. Anthony remains the
only approval authority.
