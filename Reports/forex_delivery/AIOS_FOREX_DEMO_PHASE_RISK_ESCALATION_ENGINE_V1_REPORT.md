# AIOS Forex Demo Phase Risk Escalation Engine — V1

## Scope
- New implementation: `automation/forex_engine/demo_phase_risk_escalation_engine.py`
- New tests: `tests/forex_engine/test_demo_phase_risk_escalation_engine.py`
- Uses outputs from:
  - `demo_phase_performance_monitor`
  - `demo_phase_evidence_tracker`
  - `governed_demo_advancement_gate`

## Required Output Contract
The engine returns:
- `escalation_completed`
- `escalation_level`
- `performance_state`
- `risk_status`
- `recommended_action`
- `operator_review_required`
- `blocked_reasons`
- `next_safe_action`
- `safety`

## Escalation Rules Implemented
- Improving performance: `NO_ESCALATION`
- Stable performance: `NO_ESCALATION`
- Degrading performance: `WARNING`
- Risk violation / unsafe evidence / missing evidence / insufficient evidence: `RISK_ESCALATION`
- Repeated risk violations: `DEMO_PHASE_SUSPENSION_RECOMMENDED`
- Operator review required for all levels above `WARNING`.

## Safety
- Paper/demo only context checks are enforced.
- No broker/credential/network/live trading/demo activation/capital allocation behavior introduced.
