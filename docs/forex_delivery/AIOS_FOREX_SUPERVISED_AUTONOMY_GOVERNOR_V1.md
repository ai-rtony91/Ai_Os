# AIOS Forex Supervised Autonomy Governor V1

## Objective
This module provides a repo-safe, deterministic readiness classifier for supervised
Forex autonomy. It does not use broker APIs, network calls, credentials, or order
execution.

## Status Set
- `AUTONOMY_BLOCKED`
- `REQUIRE_MORE_EVIDENCE`
- `DEMO_SUPERVISED_READY`
- `LIVE_MICRO_EXCEPTION_REVIEW_READY`
- `LIVE_BLOCKED_BY_POLICY`

## Inputs Evaluated
- Profitability evidence status
- Sample sufficiency
- Walk-forward sufficiency
- Drawdown limit compliance
- Profit factor threshold
- Expectancy threshold
- Broker readiness
- Live bridge eligibility
- Kill-switch state
- Daily stop state
- Max-loss state
- Order-count safety
- TP/SL presence
- Monitoring readiness
- Evidence freshness
- Owner approval status

## Output Contract
The evaluator returns:
- `candidate_status`
- `autonomy_window_target`
- `live_trading_allowed`
- `profit_claim_allowed`
- `blockers`
- `warnings`
- `passed_gates`
- `failed_gates`
- `next_safe_action`
- `evidence_summary`

`live_trading_allowed` and `profit_claim_allowed` default to `false` and only become
`true` when sanitized proof inputs are explicitly supplied.

## Runner
Use:

```powershell
python scripts/forex_delivery/run_supervised_autonomy_governor_v1.py
```

Use `--input-json` for sanitized local input and `--write-report` to render the
result into a markdown report.

## Safety Rules
- No broker API calls
- No credential reads or environment reads
- No account identifier handling
- No order placement
- No live trading authorization
- No runtime start, scheduling, daemon, or webhook changes

## Validator Chain
- `python -m py_compile automation/forex_engine/supervised_autonomy_governor_v1.py`
- `python -m py_compile scripts/forex_delivery/run_supervised_autonomy_governor_v1.py`
- `python -m pytest tests/forex_engine/test_supervised_autonomy_governor_v1.py -q`
- `python scripts/forex_delivery/run_supervised_autonomy_governor_v1.py`

