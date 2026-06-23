# AIOS Forex 100-120 Profit Milestone First V1

## Mission Outcome

Packet: `AIOS-FOREX-100-120-PROFIT-MILESTONE-FIRST-V1`
Branch: `feature/forex-profit-milestone-first-100-120-v1`
Current status: **TARGET_NOT_PROVEN** for return milestone tracker with current evidence sample (tracker blocks when required gates and evidence are insufficient).

## Required Fields

- Target return min: `100.0`
- Target return max: `120.0`
- Execution allowed: `False`
- Demo order allowed: `False`
- Live order allowed: `False`

## Current Evidence

- Read-only money strip payload now includes additional money visibility fields in sanitizer:
  - `balance`
  - `nav`
  - `equity`
  - `margin_available`
  - `margin_used`
  - `margin_used_percent`
  - `withdrawal_limit`
  - `realized_pl`
  - `unrealized_pl`
  - `open_trade_count`
  - `open_position_count`
  - `pending_order_count`
- Backend endpoint added: `GET /api/forex/oanda/money-strip`
  - Returns fail-closed `BLOCKED` payload when controls are not enabled.
  - Uses read-only Python bridge model when controls are present.
  - Never returns credentials or account IDs and does not expose raw payload.
- Profit milestone tracker module now implemented:
  - `automation/forex_engine/profit_milestone_100_120_tracker_v1.py`
  - `tests/forex_engine/test_profit_milestone_100_120_tracker_v1.py`

## Blockers

- Milestone tracker remains blocked by evidence/gate requirements until caller supplies verified candidate evidence with broker-readiness and risk gates.
- Dashboard minimal read-only money panel was not modified in this packet.
- Read-only bridge endpoint currently depends on a local Python bridge invocation and returns sanitized blocked/read model.

## Safety Guarantees

- No credentials are read from or written to reports in this packet.
- No `.env` file reads were added.
- No account IDs are included in output payloads.
- No broker write calls were introduced.
- No live/demo orders are placed.
- No scheduler/daemon/webhook/background execution was added.
- `execution_allowed`, `demo_order_allowed`, `live_order_allowed`, and `order_placement_allowed` remain false in updated read-only surfaces.

## Next Safe Action

- Run:
  - `python -c "from automation.forex_engine.profit_milestone_100_120_tracker_v1 import evaluate_profit_milestone_100_120_tracker_v1; import pprint; pprint.pp(evaluate_profit_milestone_100_120_tracker_v1(candidate_evidence={\"candidate_id\":\"c1-eur-buy\",\"strategy_id\":\"s1\",\"instrument\":\"EUR_USD\",\"direction\":\"LONG\",\"long_only\":true,\"short_side_disabled\":true,\"starting_balance\":10000.0,\"current_balance\":20100.0,\"realized_pl\":1200.0,\"unrealized_pl\":0.0,\"open_trades\":2,\"closed_trades\":35,\"sample_size\":35,\"expectancy\":2.0,\"profit_factor\":1.6,\"max_drawdown\":12.0,\"walk_forward_status\":\"passed\",\"walk_forward_folds\":3,\"out_of_sample_folds\":3,\"min_required_trades\":30,\"min_required_walk_forward_folds\":3,\"min_required_out_of_sample_folds\":3,\"min_expectancy\":0.0,\"min_profit_factor\":1.2,\"max_drawdown_allowed\":25.0,\"broker_readiness_passed\":true,\"risk_gate_passed\":true,\"current_return_source\":\"fixture\"})")`
- Validate that endpoint is fail-closed until environment controls are enabled:
  - `http://localhost:<port>/api/forex/oanda/money-strip`

## Files Changed

- `automation/forex_engine/profit_milestone_100_120_tracker_v1.py`
- `tests/forex_engine/test_profit_milestone_100_120_tracker_v1.py`
- `automation/forex_engine/read_only_live_data_sanitizer.py`
- `src/forex_delivery/read_only_live_data_bridge.py`
- `services/orchestrator/index.js`

## Validation

- `python -m compileall src/forex_delivery automation/forex_engine scripts/forex_delivery tests/forex_engine`
- `python -m pytest tests/forex_engine -q`
- `npm --prefix apps/dashboard run build`
- `git diff --check`
- `git diff --name-only`
- `git status --short --branch`

## Remaining Blockers

- Missing proven, broker-ready, risk-cleared, walk-forward-stable evidence for 100%-120% target to produce `TARGET_READY_FOR_OWNER_REVIEW`.
- Broker read-only money endpoint requires:
  - `AIOS_FOREX_READONLY_LIVE_ENABLE=1`
  - `AIOS_FOREX_BROKER=oanda`
  - `OANDA_API_TOKEN` and `OANDA_ACCOUNT_ID` runtime presence.
