# AIOS FOREX Next Action Engine

## Purpose

`next_action_engine.py` is a canonical selector for the next safe packet to execute after the paper-only spine.

It does not execute work, does not place orders, and does not mutate dashboard truth.

## Paper-only boundary

This module is display/control-only:

- `mode = PAPER_ONLY`
- returns read-only safety payloads
- no broker/live execution
- no credentials or account IDs
- no network or scheduler behavior

## Inputs

- `repo_state`: present modules/docs and optional state flags
- `evidence_summary`: paper session/trade metrics and warnings
- `completed_packets`: packet IDs already completed
- `blockers`: external blocker strings
- `requested_goal`: optional goal text
- `metadata`: pass-through metadata

## Selection order

1. Protected actions (live/broker/credential/secret/API/brokered action terms) => `requires_approval`
2. Missing spine packets:
   - `FOREX-EVIDENCE-LEDGER`
   - `FOREX-SESSION-REPLAY`
   - `AIOS-FOREX-DASHBOARD-TRUTH-WIRING`
3. If long-run paper supervisor not complete => `FOREX-LONG-RUN-PAPER-SUPERVISOR`
4. If paper evidence is immature => `FOREX-LONG-RUN-PAPER-SUPERVISOR`
5. If paper evidence is mature => `FOREX-DEMO-CONNECTOR-READONLY`
6. If readonly connector exists but order mapping missing => `FOREX-DEMO-ORDER-MAPPING`
7. If order mapping exists but reconciliation missing => `FOREX-DEMO-RECONCILIATION`
8. If demo promotion proof incomplete => `FOREX-PAPER-TO-DEMO-PROMOTION`
9. If long-run and demo sequence complete => `AIOS-FOREX-SELF-IMPROVEMENT`

## Protected-action detection

Any `requested_goal` or `blockers` containing terms like live, broker, credential, API key, account id, webhook, real order, or OANDA submit will return:

- `decision = requires_approval`
- `protected_action_detected = True`
- `approval_required = True`
- `no_live_action_stop = True`

## Result shape

`recommend_next_action` returns:

- allowed
- decision
- mode
- next_packet_bucket
- priority
- reason
- blockers
- protected_action_detected
- approval_required
- approval_reason
- missing_prerequisites
- safe_to_auto_build
- no_live_action_stop
- evidence_used
- recommended_validator_scope
- safety
- next_safe_action
- metadata

## Relation to existing work

It reads only module/doc presence and evidence summary from the canonical modules:
session replay, evidence ledger, and dashboard truth wiring.

## Why no execution

No order submission, no broker calls, and no mutation of paper truth are performed.

## Next safe packet

Current immediate recommendation path starts at `FOREX-LONG-RUN-PAPER-SUPERVISOR` unless blocked by missing spines or approval blockers.
