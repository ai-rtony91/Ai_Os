# Worker Dispatcher Active-State Contracts V1

## Purpose

These contracts make Dispatcher Assignment Executor state surfaces explicit. The
executor reads existing files and classifies them; it does not repair, mutate,
launch workers, approve APPLY, send notifications, or wake Anthony.

## Surface Statuses

- `ACTIVE_CONTRACT`: active state surface for dispatcher decisions.
- `HISTORICAL_REFERENCE`: readable history only, not active queue input.
- `EVIDENCE_ONLY`: evidence for authority or validation, not future approval.
- `COMPLETED_RECORD`: closed record that must not become active work.
- `EMPTY_ACTIVE_REGISTRY`: active registry exists and is valid but empty.
- `PROPOSED_BACKLOG`: proposed work that is not active without approval.
- `GENERATED_OUTPUT`: generated evidence/report output.
- `UNKNOWN`: state could not be determined.
- `MISSING`: expected surface is absent.
- `MALFORMED`: expected surface exists but cannot be parsed.
- `REVIEW_REQUIRED`: conservative operator/Night Supervisor review required.

## Queue Contract

`automation/orchestration/work_packets/active/` is the canonical active work
source when present. `automation/orchestration/queue/DISPATCHER_QUEUE.json` is a
historical reference when it declares `HISTORICAL`; historical queue entries must
not become active dispatch candidates. Proposed work packets are backlog only
until explicitly approved.

## Lock Contract

`automation/orchestration/locks/FILE_LOCK_REGISTRY.json` is the lock surface when
present. `locks: []` is valid and classified as `EMPTY_ACTIVE_REGISTRY` /
`NO_ACTIVE_LOCKS`. Missing, malformed, expired, or unknown-owner locks require
review. Protected path overlap blocks candidate dispatch.

## Approval Contract

`automation/orchestration/approval_inbox/` is the active approval authority
surface. Completed authority-repair records are `EVIDENCE_ONLY`; they do not
grant future APPLY. Future APPLY requires exact scoped Anthony approval.
Validator PASS, GitHub check PASS, and Dispatcher preview output are evidence
only, not approval.

## Worker Inbox Contract

`automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` is a readable
state surface. Items marked complete, done, cancelled, historical, or superseded
are `COMPLETE_OR_SUPERSEDED` and must not become active work.

## Work Packet Contract

Work packets in `work_packets/active/` are read-only input in this lane. Missing
required fields produce `REVIEW_REQUIRED`; dispatch previews never become
executable work packets and never contain execution tokens.

## Walkie Alignment

Internal walkie events remain preview-only routing evidence. Dispatcher never
wakes Anthony directly; Watchdog/Pi5 remains the external wake gate.
