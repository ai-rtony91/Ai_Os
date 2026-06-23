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
- sample_size: `30`

## Proof summary
- replay_proof: `True`
- reconciliation_proof: `True`
- kill_switch_proof: `True`
- rollback_proof: `True`
- risk_proof: `True`
- demo_validation_proof: `True`
- freshness_proof: `{'timestamp': '2026-06-23T19:11:05.963623+00:00', 'age_hours': 0.0}`

## Canonical bridge verdict
- verdict: `DEMO_REVIEW_READY`
- blockers: `none`
- next_safe_action: `Prepare demo-review packet with consolidated proof bundle.`

## Discovery and mitigation summaries
- discovery candidate_count: `5`
- replacement_recommendation: `retain_anchor_and_continue`
- mitigation candidate_status: `CONTINUE`
- walk_forward_improved: `True`

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
