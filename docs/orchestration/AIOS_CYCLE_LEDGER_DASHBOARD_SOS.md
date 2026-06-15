# AIOS Cycle Ledger Dashboard SOS Contract

Schema: `AIOS_CYCLE_LEDGER_DASHBOARD_SOS.v1`

`automation/orchestration/aios_cycle_ledger.py` transforms local AIOS cycle evidence into a pure JSON-ready ledger entry plus dashboard/SOS contract. It is the control-plane memory and instrument-panel contract for the self-building loop:

```text
self-route -> packet queue planner -> Codex-ready preview -> validation evidence -> PR/check evidence -> blocker/SOS decision -> next safe action -> repeat later
```

## Scope

This contract does not build trading execution. It records whether a self-building cycle is safe to display and whether Anthony must be interrupted for an SOS-class condition.

It does not:

- write files
- write Reports
- execute commands
- launch Codex
- dispatch workers
- mutate queues
- mutate approvals
- start a scheduler
- start a daemon
- use the network
- touch broker, live-trading, credential, order, or webhook paths
- stage, commit, push, merge, reset, or delete branches

## Ledger Entry

The cycle ledger entry uses schema `AIOS_CYCLE_LEDGER_ENTRY.v1` and includes:

- `cycle_id`
- `timestamp_utc`
- `repo_branch`
- `repo_head`
- `selected_packet`
- `selected_reason`
- `codex_prompt_emitted`
- `validation_status`
- `validation_summary`
- `pr_number`
- `pr_status`
- `checks_status`
- `blocker_status`
- `sos_required`
- `sos_reason`
- `next_safe_action`
- `forex_builder_alignment`
- `safety`

## Dashboard Contract

The dashboard contract uses schema `AIOS_CYCLE_DASHBOARD_CONTRACT.v1` and exposes:

- `current_mission`
- `current_cycle`
- `current_packet`
- `progress_status`
- `tests_passed`
- `tests_failed`
- `pr_status`
- `checks_status`
- `blocker_status`
- `sos_required`
- `sos_reason`
- `next_safe_action`
- `last_updated_utc`

Dashboard consumers must treat this as display evidence only. It is not approval authority, queue authority, worker authority, or trading authority.

## SOS Rules

`sos_required` is true only for:

- blocked protected gates
- validation failure requiring owner decision
- repo corruption
- secrets or credential boundary
- broker or live-trading boundary
- approval-required action

`sos_required` is false for:

- normal progress
- no-work states
- pending safe validation
- ordinary report-only stops

## Forex Builder Alignment

Every ledger entry includes `forex_builder_alignment` for the current milestone:

```text
AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety
```

This field exists so AIOS can keep the control-plane loop aligned with the first proof target without enabling broker execution, live trading, credential access, real orders, or webhooks.

## Side-Effect Proof

The top-level contract preserves these proof fields:

- `commands_executed: []`
- `files_written: []`
- `workers_dispatched: false`
- `queues_mutated: false`
- `approvals_mutated: false`
- `safety.preview_only: true`
- `safety.evidence_only: true`

## Next Safe Integration

A future scoped packet may connect runtime self-route output to this contract as read-only evidence. That future packet must still preserve report-only behavior and stop before queue mutation, worker dispatch, approval mutation, Reports writes, scheduler activation, daemon activation, commit, push, merge, broker access, live trading, credentials, orders, or webhooks.
