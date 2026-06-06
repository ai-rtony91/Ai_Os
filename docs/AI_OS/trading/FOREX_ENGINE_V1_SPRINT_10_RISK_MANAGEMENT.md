# AI_OS Forex Engine v1 — Sprint 10 Risk Management + Kill-Switch Modeling

## Objective

Sprint 10 creates local PAPER_ONLY risk management and kill-switch modeling.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal candidates.
Sprint 5 added setup confidence grading.
Sprint 6 compared strategy outputs.
Sprint 7 added walk-forward validation.
Sprint 8 added paper operator status.
Sprint 9 added broker sandbox modeling.
Sprint 10 models risk actions and kill-switch behavior before future sandbox/live work.

## Scope

Included:

- RiskManagementEngine
- RiskManagementScenario
- RiskDecisionReport
- KillSwitchReport
- RiskAction
- KillSwitchState
- RiskBreachType
- Risk management demo
- Tests
- Documentation

Excluded:

- Live trading
- Broker APIs
- Real order closing
- External data download
- Credentials
- Telegram sending
- Email sending
- Push notifications
- Scheduler
- Hardware
- run_live_trading_demo

## Current Defaults

- Starting account: 500 USD
- Paper risk: 0.5 percent
- Daily drawdown stop: 2 percent
- Weekly drawdown threshold: 5 percent
- Max open paper trades: 2
- Loss streak pause: 3
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Mode: PAPER_ONLY

## Files Added

- `automation/forex_engine/risk_management.py`
- `automation/forex_engine/run_risk_management_demo.py`
- `tests/forex_engine/test_risk_management.py`
- `docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_10_RISK_MANAGEMENT.md`

## Risk Management Flow

1. Create scenario
2. Evaluate mode
3. Evaluate validation health
4. Evaluate daily drawdown
5. Evaluate weekly drawdown
6. Evaluate loss streak
7. Evaluate open trade exposure
8. Evaluate proposed order risk
9. Choose highest-priority action
10. Build kill-switch report
11. Print operator summary

## Risk Actions

- CONTINUE
- REDUCE_RISK
- BLOCK_ORDER
- PAUSE_TRADING
- KILL_SWITCH

## Kill-Switch Rules

- Trigger on daily drawdown breach.
- Trigger on weekly drawdown breach.
- Trigger on non-PAPER mode.
- Do not trigger on simple oversized order block.

## Drawdown Rules

- Daily drawdown: 2 percent of current balance.
- Weekly drawdown: 5 percent threshold.

## Loss-Streak Rules

Pause after configured consecutive losses.

## Order-Risk Rules

For 500 USD at 0.5 percent, proposed order risk above 2.50 USD is blocked.

## Demo Command

```powershell
python -m automation.forex_engine.run_risk_management_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
python -m automation.forex_engine.run_risk_management_demo
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

- Sprint 10 is local RISK_MODEL_ONLY.
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
- No real order closing.
- No live kill switch.
- No alert delivery.
- No scheduler.
- No latency.
- No slippage.
- No spread.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.
- No live readiness.

## Success Criteria

- RiskManagementEngine exists.
- RiskManagementScenario exists.
- RiskDecisionReport exists.
- KillSwitchReport exists.
- Normal scenario continues.
- Daily drawdown triggers kill switch.
- Weekly drawdown triggers kill switch.
- Loss streak pauses trading.
- Max open trades blocks order.
- Oversize order blocks order.
- Non-paper mode triggers kill switch.
- Risk management demo runs.
- Broker sandbox demo still runs.
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

Sprint 11 should add parameter optimization demo and overfitting guard scaffolding, still without live execution, broker credentials, or real API calls.
