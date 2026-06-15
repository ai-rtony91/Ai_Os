# AIOS Forex Builder Paper-Forward Evidence V2

## Purpose

V2 broadens local paper-forward evidence from a single demo fixture into deterministic multi-regime comparison.

It adds:

- expanded deterministic local fixtures across trend, chop, pullback, reversal, volatile, low-volatility, and range regimes.
- multi-fixture paper-forward simulation.
- per-fixture simulated ledger summaries.
- aggregate paper PnL and consistency scoring.
- regime consistency scoring.
- compact readiness and dashboard summaries.

## Fixtures

V2 uses local Python data only:

- `EURUSD_5M_TREND_SAMPLE`
- `EURUSD_5M_CHOP_SAMPLE`
- `EURUSD_5M_PULLBACK_SAMPLE`
- `EURUSD_5M_REVERSAL_SAMPLE`
- `EURUSD_5M_VOLATILE_SAMPLE`
- `EURUSD_5M_LOW_VOL_SAMPLE`
- `EURUSD_15M_TREND_SAMPLE`
- `GBPUSD_5M_TREND_SAMPLE`
- `USDJPY_5M_RANGE_SAMPLE`

Each fixture validates through `automation/forex_engine/schema_contracts.py`, has `network_allowed = false`, and uses source `deterministic_local_fixture`.

## Classifications

Allowed V2 classifications are:

- `FAIL`
- `WATCHLIST`
- `PAPER_FORWARD_READY`

V2 must never emit `LIVE_READY`.

`PAPER_FORWARD_READY` means local simulation evidence is promising enough for the next protected local review step. It is not broker paper trading, broker readiness, or live readiness.

## Demo Command

```powershell
python -m automation.forex_engine.run_paper_forward_evidence_v2_demo
```

The command prints fixture count, regime count, simulated ledger entry count, aggregate paper PnL, consistency percentage, classification, protected gate status, and the next safe action.

## Interpretation

This is local simulation only.

This is not broker paper trading.

This does not prove live readiness.

Stronger out-of-sample and forward evidence is required.

Live readiness remains a protected downstream gate.

V2 evidence can support `PAPER_FORWARD_READY` only for local simulation. It cannot authorize broker paper trading or live trading. The next protected step is risk-governor threshold hardening and then a separate approval packet for broker-paper sandbox integration, if earned.

## Boundaries

No broker integration, OANDA/live exchange integration, broker paper orders, live trading, credentials, `.env` reads or writes, real orders, account mutation, webhooks, scheduler activation, daemon activation, network market automation, worker dispatch, queue mutation, approval mutation, report writes, commit, push, or merge is authorized by V2 evidence.
