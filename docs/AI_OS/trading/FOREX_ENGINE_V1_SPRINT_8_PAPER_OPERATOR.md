# AI_OS Forex Engine v1 — Sprint 8 Paper Operator Mode

## Objective

Sprint 8 creates local PAPER_ONLY paper-operator reporting, alert-state modeling, pause rules, and supervisor summaries.

## Why This Sprint Matters

Sprint 1 proved paper trade accounting.
Sprint 2 proved local candle loading.
Sprint 3 proved local backtesting.
Sprint 4 added regime and signal candidates.
Sprint 5 added setup confidence grading.
Sprint 6 compared strategy outputs.
Sprint 7 added walk-forward validation.
Sprint 8 gives the operator a single research-status summary.

## Scope

Included:

- PaperOperator
- DailyOperatorReport
- SupervisorSummary
- OperatorAlert
- RiskPosture
- PaperOperatorStatus
- PauseReason
- AlertState
- Paper operator demo
- Tests
- Documentation

Excluded:

- Live trading
- Broker APIs
- External data download
- Telegram sending
- Email sending
- Push notifications
- Scheduler
- Hardware
- Promotion to live trading

## Current Defaults

- Starting account: 500 USD
- Paper risk: 0.5 percent
- Daily drawdown stop: 2 percent
- Max open paper trades: 2
- Loss streak pause: 3
- Symbols: EURUSD, GBPUSD, USDJPY, XAUUSD
- Mode: PAPER_ONLY

## Files Added

- `automation/forex_engine/paper_operator.py`
- `automation/forex_engine/run_paper_operator_demo.py`
- `tests/forex_engine/test_paper_operator.py`
- `docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_8_PAPER_OPERATOR.md`

## Paper Operator Flow

1. Load config
2. Collect local research summaries
3. Evaluate alerts
4. Determine pause reason
5. Determine risk posture
6. Determine operator status
7. Build daily report
8. Build supervisor summary
9. Print next safe action

## Alert States

- PAPER_ONLY_BOUNDARY_OK
- INSUFFICIENT_DATA_ALERT
- PROFIT_MILESTONE_ALERT
- LOSS_STREAK_ALERT
- DAILY_DRAWDOWN_ALERT
- WEEKLY_DRAWDOWN_ALERT
- VALIDATION_HEALTH_ALERT
- NO_ALERTS

## Pause Rules

- Daily drawdown
- Weekly drawdown
- Loss streak
- Validation failure
- Insufficient data
- Manual review required

## Risk Posture Rules

- CONSERVATIVE
- NORMAL
- AGGRESSIVE_RESEARCH_ONLY
- PAUSED

Hard alerts force PAUSED. Insufficient data without hard alerts keeps the operator conservative.

## Supervisor Summary

- `promotion_ready` is False in Sprint 8.
- Live trading is not authorized.
- Research readiness can be true only for READY_FOR_PAPER_RESEARCH or WATCHLIST.

## Demo Command

```powershell
python -m automation.forex_engine.run_paper_operator_demo
```

## Validation

```powershell
python -m pytest tests/forex_engine
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

- Sprint 8 is PAPER_ONLY.
- No broker execution.
- No API ingestion.
- No network ingestion.
- No credentials.
- No live order path.
- No alert sending.
- No scheduling.
- No profitability claim.

## Known Limitations

- Local reporting only.
- No real alert delivery.
- No scheduler.
- No Telegram.
- No email.
- No broker.
- No live readiness.
- Fixture data is fake.
- Real historical data still required.
- No spread.
- No slippage.
- No commissions.
- No swaps.
- No pip-value correctness.
- No XAUUSD tick-value correctness.

## Success Criteria

- PaperOperator exists.
- DailyOperatorReport exists.
- SupervisorSummary exists.
- OperatorAlert exists.
- Alert states exist.
- Pause rules exist.
- Risk posture rules exist.
- Paper operator demo runs.
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
- No alert sending exists.
- `promotion_ready` is always False in Sprint 8.

## Next Sprint

Sprint 9 should add broker sandbox interface modeling only, still without live credentials or real execution.
