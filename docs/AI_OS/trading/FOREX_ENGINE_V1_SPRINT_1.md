# AI_OS Forex Engine v1 - Sprint 1

## Objective

Sprint 1 creates a paper-only scaffold for AI_OS Forex Engine v1.

## Scope

Included:

- Config
- Models
- Risk rules
- Signal validation
- Confidence scaffold
- Paper execution
- Journal
- Analytics
- Demo runner
- Tests

Excluded:

- Live broker execution
- Broker credentials
- OANDA
- MT5
- TradersPost
- TradingView webhooks
- Telegram live sending
- Scheduler authority
- Worker launch authority
- Approval mutation
- Pi runtime authority
- Real-money trading

## Current Defaults

- Starting account: 500 USD
- Paper risk: 0.5 percent
- Future first-live risk target: 0.25 percent
- Daily drawdown stop: 2 percent
- Max open paper trades: 2
- Loss streak pause: 3
- Markets: EURUSD, GBPUSD, USDJPY, XAUUSD
- Mode: PAPER_ONLY

## Folder Structure

- `automation/forex_engine/`: paper-only engine package
- `automation/forex_engine/runtime/`: ignored local demo and journal output
- `tests/forex_engine/`: targeted pytest coverage

## Data Models

- `ForexSignal`
- `ConfidenceAssessment`
- `RiskDecision`
- `PaperTrade`
- `JournalEvent`
- `PerformanceSummary`

## Risk Rules

- Risk per paper trade: 0.5 percent of current paper balance
- Daily drawdown limit: 2 percent of current paper balance
- Max open paper trades: 2
- Pause after 3 consecutive losses
- Position sizing is simulation-grade only

## Paper Execution Flow

1. Load `ForexEngineConfig`.
2. Validate `PAPER_ONLY` mode.
3. Validate the signal.
4. Score deterministic confidence.
5. Apply risk gates.
6. Open a `PaperTrade`.
7. Close the paper trade with simulated PnL.
8. Write JSONL paper journal events.
9. Summarize paper performance.

## Outputs

- Operator-readable demo summary
- JSONL paper journal events
- Targeted analytics summary
- Targeted tests

## Validation

Targeted test command:

```powershell
python -m pytest tests/forex_engine
```

Demo command:

```powershell
python -m automation.forex_engine.run_paper_demo
```

## Safety Boundary

- Sprint 1 is `PAPER_ONLY`.
- No live broker execution exists.
- No broker credentials are read or stored.
- No network trading calls exist.
- No Telegram sending exists.
- No scheduler authority exists.
- No worker launch authority exists.
- No approval mutation exists.

## Known Limitations

- Position sizing is simulation-grade only.
- Pip value is not broker-ready.
- Contract size is not broker-ready.
- Lot size is not broker-ready.
- Spread is not implemented.
- Slippage is not implemented.
- Swap is not implemented.
- Commissions are not implemented.
- XAUUSD tick value is not implemented.
- Confidence scoring is deterministic scaffold logic, not trained AI.
- Regime detection is scaffold only.
- Market data ingestion begins in Sprint 2.
- Backtesting begins in Sprint 3.
- Live broker execution is intentionally blocked.

## Next Sprint

- Add local market data ingestion for paper research.
- Keep all execution paper-only.
- Preserve broker and credential boundaries.
