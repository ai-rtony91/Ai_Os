# AIOS Completed Packet Memory

Schema: `AIOS_COMPLETED_PACKET_MEMORY_SUPPRESSION.v1`

`automation/orchestration/aios_completed_packet_memory.py` transforms candidate packet evidence plus completed-work memory into an active candidate list. Its job is to keep AIOS from repeatedly selecting packets that already landed.

This contract is evidence transformation only. It does not mutate queues, write memory files, dispatch workers, or execute packets.

## Inputs

The contract accepts local JSON evidence:

- `candidate_packets`
- `completed_packet_ids`
- `completed_packets`
- `landed_prs`
- `commit_history_summary`
- `cycle_ledger_history`
- `manual_suppression_rules`
- `today_goal_context`

If no completed memory is supplied, the contract still includes default completed memory for the landed self-building infrastructure packets through PR #731.

## Outputs

The result includes:

- `schema`
- `suppression_status`
- `active_candidates`
- `suppressed_candidates`
- `completed_packet_ids`
- `suppression_reasons`
- `next_candidate_available`
- `next_candidate`
- `memory_source`
- `forex_builder_alignment`
- `commands_executed`
- `files_written`
- `workers_dispatched`
- `queues_mutated`
- `approvals_mutated`
- `safety`
- `next_safe_action`

## Suppression Rules

A candidate is suppressed when:

- `candidate.packet_id` is in completed packet memory
- candidate title or lane matches landed PR evidence
- candidate required files are already covered by completed memory for the same lane or packet
- a manual suppression rule matches `packet_id` or lane
- cycle ledger history marks the packet complete

Suppressed candidates remain visible in `suppressed_candidates` with reasons. They are removed from `active_candidates`.

## Non-Suppression Rules

A candidate is not suppressed when:

- it is explicitly reopened
- it adds required files not covered by completed memory
- it represents validation-failed repair work
- it is a new forex-builder scaffold candidate

These exceptions prevent completed memory from hiding legitimate follow-up work.

## Default Completed Memory

Default memory includes the landed infrastructure sequence:

- packet queue planner
- self-route packet planner connector
- cycle ledger/dashboard/SOS contract
- self-route cycle ledger connector
- candidate evidence adapter
- self-route candidate evidence connector
- candidate planner JSON handoff fix
- approved packet executor contract
- self-route approved executor connector
- `PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION`

The default memory exists so self-route can stop selecting stale infrastructure packets after those lanes land.

## Forex Builder Alignment

Every result includes `forex_builder_alignment` for the current milestone:

```text
AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety
```

Completed packet memory supports the control plane only. It does not enable broker execution, live trading, credentials, real orders, or webhooks.

## Side-Effect Boundary

The contract always reports:

- `commands_executed: []`
- `files_written: []`
- `workers_dispatched: false`
- `queues_mutated: false`
- `approvals_mutated: false`
- `safety.preview_only: true`
- `safety.evidence_only: true`

Consumers must treat this result as read-only planning evidence. A future self-route integration may feed `active_candidates` to the packet queue planner, but that integration must still stop/report and must not mutate queues or approvals.
