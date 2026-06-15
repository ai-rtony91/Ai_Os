# AIOS Candidate Packet Evidence Adapter

Schema: `AIOS_CANDIDATE_PACKET_EVIDENCE_ADAPTER.v1`

`automation/orchestration/aios_candidate_packet_evidence_adapter.py` normalizes raw local evidence into clean candidate packet objects compatible with `AIOS_PACKET_QUEUE_PLANNER.v1`.

It is evidence transformation only. It does not write files, write Reports, execute commands, launch Codex, dispatch workers, mutate queues, mutate approvals, start schedulers or daemons, use the network, touch broker/live-trading/credential/order/webhook paths, stage, commit, push, merge, reset, or delete branches.

## Purpose

Runtime self-route needs clean candidate packet evidence instead of treating generated backlog as active work. The adapter separates:

- candidate packet records that can feed the packet queue planner
- generated backlog paths that should remain archive/noise evidence
- a default safe self-build candidate when no promoted candidate exists

## Noise Classification

These path prefixes are classified as `archive_noise` unless a record is explicitly promoted:

- `Reports/`
- `control/review_bridge/`
- `automation/orchestration/work_packets/preview/`

Generated backlog under those paths is not a primary candidate packet source. It can remain useful evidence for audits, reports, or later archive review, but it must not paralyze self-route candidate selection.

## Candidate Output

Each normalized candidate includes:

- `packet_id`
- `title`
- `lane`
- `priority`
- `milestone_value`
- `risk_level`
- `status`
- `required_files`
- `blocked_files`
- `required_approvals`
- `validators`
- `dependencies`
- `conflicts`
- `safety_flags`
- `forex_builder_alignment`

The output exposes candidates under both `candidate_packets` and `candidates` so it can be passed directly to the packet queue planner.

## Default Safe Candidate

When no promoted candidate is found and the AIOS self-building milestone still needs a next step, the adapter emits:

```text
packet_id: PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION
title: Connect candidate packet evidence adapter into self-route
lane: connect-candidate-evidence-to-selfroute
priority: high
milestone_value: high
risk_level: low
status: candidate
```

Required files:

- `automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1`
- `tests/orchestration/test_aios_persistent_runtime_supervisor.py`

Validator:

```text
python -m pytest -p no:cacheprovider tests/orchestration/test_aios_persistent_runtime_supervisor.py tests/orchestration/test_aios_packet_queue_planner.py tests/orchestration/test_aios_cycle_ledger.py tests/orchestration/test_aios_candidate_packet_evidence_adapter.py -q
```

## Forex Builder Alignment

Each candidate includes alignment evidence for the current milestone:

```text
AIOS self-building machine -> first proof target: industrial-grade forex bot builder -> no broker/live/secrets until gates prove safety
```

This field keeps candidate selection tied to the proof target without enabling broker execution, live trading, credentials, real orders, or webhooks.

## Unsafe Path Flags

Candidate paths containing broker, live, secret, credential, order, or webhook terms are preserved as candidate evidence but receive `unsafe_path:*` safety flags. The packet queue planner can then reject or block unsafe work through its existing safety rules.

## Side-Effect Proof

The adapter result preserves:

- `commands_executed: []`
- `files_written: []`
- `workers_dispatched: false`
- `queues_mutated: false`
- `approvals_mutated: false`
- `safety.preview_only: true`
- `safety.evidence_only: true`

## Next Safe Integration

A future scoped packet may wire this adapter into runtime self-route as a child process that transforms local JSON evidence into packet planner input. That integration must remain report-only and must not mutate queue state, approval state, worker state, generated Reports, scheduler state, broker/live-trading paths, credentials, orders, or webhooks.
