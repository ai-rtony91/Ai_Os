# AIOS Forex Candidate Intake to Demo Review Bridge V1

## Purpose
- Route one deterministic best paper candidate from discovery + mitigation into the canonical demo-review evidence bridge.

## Source modules consumed
- automation/forex_engine/next_candidate_discovery_u_v1.py
- automation/forex_engine/mitigation_optimization_t_v1.py
- automation/forex_engine/canonical_demo_review_evidence_bridge.py

## Candidate selected
- candidate_id: `c1-eur-buy`
- strategy: `paper_long_run_supervisor_v2`
- direction: `LONG`
- selection_reason: `champion_better_than_anchor`

## Normalized metrics
- expectancy: `200.0`
- profit_factor: `999.0`
- max_drawdown: `0.0`
- win_rate: `1.0`
- sample_size: `21`

## Proof summary
- replay_proof: `False`
- reconciliation_proof: `False`
- kill_switch_proof: `True`
- rollback_proof: `False`
- risk_proof: `True`
- demo_validation_proof: `False`
- freshness_proof: `{'timestamp': '2026-06-22T00:56:18.138378+00:00', 'age_hours': 0.0}`

## Canonical bridge verdict
- verdict: `BLOCKED_INCOMPLETE_EVIDENCE`
- blockers: `missing_replay_proof, missing_reconciliation_proof, missing_rollback_proof, missing_demo_validation_proof, walk_forward_failed, paper_evidence_not_ready, mitigation_worsened`
- next_safe_action: `Collect missing/valid proofs and refresh stale evidence before rerunning review.`

## Discovery and mitigation summaries
- discovery candidate_count: `5`
- replacement_recommendation: `retain_anchor_and_continue`
- mitigation candidate_status: `REJECT`
- walk_forward_improved: `False`

## Safety boundary
- paper_only: `True`
- broker_connected: `False`
- credentials_used: `False`
- network_used: `False`
- order_execution: `False`
- demo_trading: `False`
- live_trading: `False`

## Validation
- latest: `pytest tests/forex_engine/test_candidate_intake_demo_review_bridge.py -q`

## Explicit security statement
- no broker connectivity, no credentials, no env reads, no network access, no demo trade, no live trade, no order execution introduced.
