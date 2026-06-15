# AIOS Approved Packet Executor Contract

Schema: `AIOS_APPROVED_PACKET_EXECUTOR_CONTRACT.v1`

`automation/orchestration/aios_approved_packet_executor_contract.py` transforms selected packet evidence plus Human Owner approval evidence into a pure executor decision. It is the approval gate between packet selection and any future runner.

This contract does not execute packets. It reports whether a selected packet is eligible for a future bounded execution lane.

## Scope

The contract consumes local JSON evidence:

- selected packet evidence from packet queue planning
- Human Owner approval evidence
- optional separate approval evidence for protected actions

It returns:

- `executor_status`
- `selected_packet`
- `approval_required`
- `approval_status`
- `approval_source`
- `execution_allowed`
- `command_preview_allowed`
- `codex_launch_allowed`
- `protected_action_required`
- `blocked_reasons`
- `rejected_reasons`
- `required_validators`
- `allowed_execution_mode`
- `forbidden_actions`
- side-effect proof fields
- `safety`
- `next_safe_action`

## Statuses

`allowed` means the selected packet is structurally safe, has validators, has safe scoped files, and has explicit matching Human Owner approval evidence.

`blocked` means the evidence may be repairable before execution, such as missing approval, mismatched approval, missing validators, unsafe write scope, or protected actions that need separate approval.

`rejected` means the evidence crosses a prohibited boundary, such as broker/live-trading, credentials, orders, webhooks, destructive action requests, approval mutation, queue mutation, hidden command execution, or invalid selected packet structure.

`no_packet` means there is no selected packet to evaluate.

## Allowed Rule

Execution is allowed only when all of these are true:

- `selected_packet` exists and has a packet id
- packet status is `candidate`, `ready`, or `selected`
- risk level is `low`, `medium`, `bounded`, or `preview`
- required files are local, scoped, and outside generated archive/report roots
- validators are present
- explicit Human Owner approval evidence is present
- approval references the same packet id
- broker/live-trading/credential/order/webhook boundaries are absent
- scheduler or daemon requests have separate approval
- commit, push, and merge requests have separate approval

When allowed, the contract reports `allowed_execution_mode: bounded_local_apply_preview`.

## Blocked Rule

The contract blocks execution for:

- missing approval
- approval that does not reference the selected packet id
- missing validators
- unsafe write scope
- no selected packet
- scheduler or daemon requests without separate approval
- commit, push, or merge requests without separate approval

Blocked status is reportable. It is not permission to execute.

## Rejected Rule

The contract rejects execution for:

- broker or live-trading paths
- secrets or credential paths
- order or webhook paths
- destructive action requests
- approval mutation requests
- queue mutation requests
- hidden command execution requests
- invalid selected packet structure

Rejected status must stop the future execution lane until evidence is repaired.

## Side-Effect Boundary

This contract is evidence transformation only. It does not:

- execute commands
- launch Codex
- dispatch workers
- mutate queues
- mutate approvals
- write files
- write Reports
- use the network
- start a scheduler
- start a daemon
- touch broker, live-trading, credential, order, or webhook paths
- stage, commit, push, merge, reset, or delete branches

Top-level side-effect fields remain:

- `commands_executed: []`
- `workers_dispatched: false`
- `queues_mutated: false`
- `approvals_mutated: false`
- `files_written: []`
- `safety.preview_only: true`
- `safety.evidence_only: true`

## Next Safe Integration

A future scoped packet may connect runtime self-route output to this contract after packet selection. That future integration must still stop/report by default and must not execute a selected packet without explicit matching approval evidence and the separate protected-action gates required by AIOS governance.
