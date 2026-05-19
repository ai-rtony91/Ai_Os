# Approval Decision Enforcement

Approval decisions are the control point between dispatcher planning and execution.

## Rule

A packet may not move from `waiting_approval` to `approved` unless an Approval Inbox record exists and has status `approved`.

## Enforcement States

- `pending` -> packet remains `waiting_approval`
- `approved` -> packet may move to `approved` and continue toward apply
- `rejected` -> packet becomes `blocked`
- `expired` -> packet becomes `blocked`
- missing approval id -> packet becomes `blocked`
- missing approval record -> packet remains `waiting_approval`

## Safety Notes

- The dispatcher must not treat requested approval as granted approval.
- File writes, file deletes, commits, pushes, system commands, and trading actions remain approval-gated.
- Rejected or expired approvals must not be retried automatically.
- Any mismatch between decision id and approval id is rejected.
