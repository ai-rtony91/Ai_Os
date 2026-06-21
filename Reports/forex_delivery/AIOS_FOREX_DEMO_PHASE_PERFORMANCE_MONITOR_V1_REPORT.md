# AIOS Forex Demo Phase Performance Monitor — V1

## Scope
- Built a paper/demo-only performance monitor for demo-phase evidence.
- New file: `automation/forex_engine/demo_phase_performance_monitor.py`
- New tests: `tests/forex_engine/test_demo_phase_performance_monitor.py`

## Required output contract
The monitor returns:
- `monitor_completed`
- `performance_state`
- `expectancy_trend`
- `drawdown_trend`
- `consistency_trend`
- `risk_status`
- `blocked_reasons`
- `next_safe_action`
- `safety`

## Behavior implemented
- Uses cleaned paper/demo evidence events and the existing evidence tracker safety path.
- Computes rolling trend deltas for expectancy, drawdown, and consistency.
- Detects risk expectation violations:
  - drawdown cap
  - risk cap
  - unsafe event values from tracker-level checks
- Classifies performance states:
  - `IMPROVING`
  - `STABLE`
  - `DEGRADING`
  - `RISK_VIOLATION`
  - `INSUFFICIENT_EVIDENCE`

## Safety policy
- Paper-only, no broker/client credential/network/ordering activity.
- Deterministic output and no external side effects.
