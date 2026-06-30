# AIOS Forex Remaining-Work Closure Index V1

## Purpose
Track deterministic completion state for remaining Forex/autonomy lanes and force future packets to circle back until every lane is closed to a terminal state.

## Remaining-lane philosophy
- Keep work visible as deterministic lane IDs.
- Never lose unclosed work during handoffs.
- Every packet should consume one lane at a time with owner approval boundaries.
- A lane is only closed when it lands in one terminal completion status.

## Default remaining lanes
1. `OWNER_REVIEW_DASHBOARD_SURFACING`
2. `CAPITAL_WITHDRAWAL_OWNER_REVIEW_WORKFLOW`
3. `FOREX_EVIDENCE_DEPTH_AND_WALK_FORWARD_SUFFICIENCY`
4. `PROFIT_CANDIDATE_QUALITY_IMPROVEMENT`
5. `BROKER_DEMO_OBSERVABILITY_AND_EXCEPTION_REVIEW`
6. `RISK_KILL_SWITCH_DAILY_STOP_SURFACING`
7. `DASHBOARD_STATE_REDUCTION_AND_SOURCE_OF_TRUTH`
8. `VOICE_AI_OWNER_REVIEW_SUMMARY`
9. `SECURITY_CREDENTIAL_PERSISTENCE_GATE`
10. `FINAL_AUTONOMY_SUPERVISOR_READINESS_GATE`

Each lane includes:
- `lane_id`
- `title`
- `status`
- `priority`
- `depends_on`
- `allowed_next_action`
- `forbidden_actions`
- `owner_gate_required`
- `evidence_needed`
- `safe_packet_name`

## Recommended sequence
1. Owner-review dashboard/surface packet
2. Capital withdrawal owner-review workflow packet
3. Evidence depth / walk-forward sufficiency packet
4. Candidate quality improvement packet
5. Broker demo observability and exception review packet
6. Risk and kill-switch surfacing packet
7. Dashboard state cleanup/reduction packet
8. Voice-AI owner review summary packet
9. Security persistence gate packet
10. Final autonomy supervisor readiness gate packet

## Completion statuses
Each lane ends in one of:
- `LANDED`
- `BLOCKED_WITH_REASON`
- `DEFERRED_BY_OWNER`
- `SUPERSEDED`
- `NEEDS_MORE_EVIDENCE`

## Owner gate policy
- All lanes remain owner-gated.
- No lane can complete without explicit owner decision when required.
- Any money movement, broker API, credentials use, scheduler daemon/webhook actions are forbidden by default.

## How future Codex packets should use this index
1. Read `remaining_lanes`.
2. Run the `next_best_packet`-named packet when preconditions are met.
3. Update lane status to one allowed completion state only when evidence is present.
4. Keep `blocked_lanes` and `deferred_lanes` synchronized with payload evidence.
5. Recompute index with the new statuses.

### Loop rule
Circle back until every lane is one of:
`LANDED`, `BLOCKED_WITH_REASON`, `DEFERRED_BY_OWNER`, `SUPERSEDED`, or `NEEDS_MORE_EVIDENCE`.

The index should remain deterministic across runs and should always preserve the unresolved lane order.
