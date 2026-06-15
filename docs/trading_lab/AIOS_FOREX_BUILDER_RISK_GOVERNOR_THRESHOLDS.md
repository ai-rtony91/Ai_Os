# AIOS Forex Builder Risk Governor Thresholds

The risk governor adds a risk-to-reward + expectancy optimization layer for local paper-forward evidence.

Risk-adjusted opportunity capture does not mean overtrading, bypassing risk, tuning numbers to inflate PnL, broker paper trading, or live trading. It means the local simulator must show that valid edge was captured after fixture coverage, regime consistency, cost drag, drawdown, missed opportunity, exit efficiency, and quality gates are measured.

## Local Boundary

- Mode: `PAPER_ONLY`
- Source: deterministic local fixtures and local evidence bundles
- Default starting balance: `500.00`
- PnL and return percent are local simulation only
- Missed PnL is an estimate until rejected-signal and ideal-exit ledgers exist
- Live readiness remains blocked
- Broker-paper sandbox and live trading require separate protected approval

## Default Thresholds

- Minimum fixtures: `9`
- Minimum regimes: `7`
- Minimum intents: `50`
- Minimum simulated ledger entries: `50`
- Minimum consistency: `70.0%`
- Minimum capture rate: `65.0%`
- Minimum risk-adjusted return: `0.10`
- Maximum drawdown: `8.0%`
- Maximum cost drag: `25.0%`
- Maximum missed PnL: `35.0%`
- Maximum overtrade ratio: `1.50`
- Minimum exit efficiency: `50.0%`
- Minimum opportunity quality score: `60.0`

## Demo

```powershell
python -m automation.forex_engine.run_risk_governor_demo
```

The demo prints starting balance, ending balance, paper PnL, return percent, capture rate, missed PnL estimate, cost drag, drawdown, opportunity score, classification, live-ready status, protected gate status, and the next safe action.

## Interpretation

`PAPER_FORWARD_READY` is a local simulation classification only. It cannot authorize broker paper trading or live trading. The next protected step is stress and out-of-sample validation, then a separate future broker-paper sandbox readiness contract only if evidence earns it.
