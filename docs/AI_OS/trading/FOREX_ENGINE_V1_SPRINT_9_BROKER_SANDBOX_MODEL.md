# AI_OS Forex Engine v1 — Sprint 9 Broker Sandbox Model

## Objective

Sprint 9 creates local broker sandbox interface modeling only.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal candidates.
Sprint 5 added setup confidence grading.
Sprint 6 compared strategy outputs.
Sprint 7 added walk-forward validation.
Sprint 8 added paper operator status.
Sprint 9 models future broker interactions without allowing them.

## Scope

Included:

- BrokerSandbox
- SandboxOrderRequest
- SandboxOrderResponse
- SandboxAccountState
- BrokerReadinessCheck
- Reject reasons
- Placeholder fill simulation
- Broker sandbox demo
- Tests
- Documentation

Excluded:

- Live trading
- Broker APIs
- External data download
- Credentials
- Telegram sending
- Email sending
- Push notifications
- Scheduler
- Hardware
- Real order placement
- run_live_trading_demo

## Current Defaults

- Starting account: 500 USD
- Paper risk: 0.5 percent
- Daily drawdown stop: 2 percent
- Max open paper trades: 2
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Mode: PAPER_ONLY
- Sandbox mode: SANDBOX_MODEL_ONLY

## Files Added

- `automation/forex_engine/broker_sandbox.py`
- `automation/forex_engine/run_broker_sandbox_demo.py`
- `tests/forex_engine/test_broker_sandbox.py`
- `docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_9_BROKER_SANDBOX_MODEL.md`

## Sandbox Model Flow

1. Create sandbox
2. Validate request
3. Reject unsafe request or simulate model fill
4. Update local sandbox state
5. Build readiness check
6. Print operator summary

## Order Request Model

- mode
- symbol
- side
- order_type
- units
- requested_price
- stop_loss
- take_profit
- client_order_id
- metadata

## Order Response Model

- mode
- client_order_id
- sandbox_order_id
- symbol
- side
- order_type
- requested_units
- filled_units
- requested_price
- fill_price
- status
- reject_reason
- message
- metadata

## Rejected Conditions

- Invalid symbol
- Invalid side
- Invalid order type
- Invalid units
- Invalid price
- Invalid mode
- Live trading blocked
- Credentials not allowed
- Network not allowed
- Risk blocked

## Readiness Check

The readiness check must state not live ready.

Separate authorization is required before any real broker work.

## Demo Command

```powershell
python -m automation.forex_engine.run_broker_sandbox_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_broker_sandbox_demo
python -m automation.forex_engine.run_paper_operator_demo
python -m automation.forex_engine.run_walk_forward_demo
python -m automation.forex_engine.run_strategy_comparison_demo
python -m automation.forex_engine.run_confidence_demo
python -m automation.forex_engine.run_signal_rules_demo
python -m automation.forex_engine.run_backtest_demo
python -m automation.forex_engine.run_market_data_demo
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 9 is local SANDBOX_MODEL_ONLY.
- No broker execution.
- No API calls.
- No network calls.
- No credentials.
- No live order path.
- No alert sending.
- No scheduling.
- No profitability claim.
- No live readiness claim.

## Known Limitations

- Model only.
- No real broker.
- No broker API.
- No credentials.
- No network.
- No real fills.
- Placeholder prices only.
- No latency.
- No slippage.
- No spread.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No live readiness.

## Success Criteria

- BrokerSandbox exists.
- SandboxOrderRequest exists.
- SandboxOrderResponse exists.
- SandboxAccountState exists.
- BrokerReadinessCheck exists.
- Valid market order simulates locally.
- Invalid symbol rejects.
- Invalid units rejects.
- Credential metadata rejects.
- Live mode blocks.
- Network disabled.
- Credentials not loaded.
- Readiness check says not live ready.
- Broker sandbox demo runs.
- Paper operator demo still runs.
- Walk-forward demo still runs.
- Strategy comparison demo still runs.
- Confidence demo still runs.
- Signal rules demo still runs.
- Backtest demo still runs.
- Market data demo still runs.
- Paper demo still runs.
- All forex_engine tests pass.
- No live execution path exists.
- No network ingestion exists.
- No run_live_trading_demo.py exists.

## Next Sprint

Sprint 10 should add risk management demo and kill-switch modeling, still without live execution or broker credentials.
