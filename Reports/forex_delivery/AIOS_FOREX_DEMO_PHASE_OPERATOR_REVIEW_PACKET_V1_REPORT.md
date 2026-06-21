# AIOS Demo Phase Operator Review Packet V1

## Objective
Create a deterministic operator-review packet builder that converts demo-phase monitoring and risk-escalation outputs into a fixed schema for operator decisions.

## Scope
- `automation/forex_engine/demo_phase_operator_review_packet.py`
- `tests/forex_engine/test_demo_phase_operator_review_packet.py`

## Required Output Mapping
- `review_packet_completed` indicates the packet generation result completed.
- `operator_review_required` indicates whether escalation or safety conditions require human review.
- `recommended_operator_decision` maps to:
  - `APPROVE_CONTINUE_DEMO_PHASE`
  - `REQUEST_MORE_EVIDENCE`
  - `SUSPEND_DEMO_PHASE`
  - `REJECT_DEMO_ADVANCEMENT`
- `performance_state`, `escalation_level`, `review_reasons`, `blocked_reasons`, and `next_safe_action` are passed through from deterministic escalation engine output.
- `safety` returns an explicit paper/demo-safe boundary map.

## Behavior Notes
- Improving/stable performance with no escalation -> `APPROVE_CONTINUE_DEMO_PHASE`.
- Warning signals -> `REQUEST_MORE_EVIDENCE`.
- Risk escalation without hard unsafe evidence -> `REQUEST_MORE_EVIDENCE` with review required.
- Repeated risk escalation -> `SUSPEND_DEMO_PHASE`.
- Unsafe evidence, safety violations, or validation failures -> `REJECT_DEMO_ADVANCEMENT`.
- Missing evidence -> `REQUEST_MORE_EVIDENCE`.
- No broker/network/live/demo-activation paths or credential reads are used.

## Validation
- `python -m pytest tests/forex_engine/test_demo_phase_operator_review_packet.py -q`
- `python -m py_compile automation/forex_engine/demo_phase_operator_review_packet.py tests/forex_engine/test_demo_phase_operator_review_packet.py`
