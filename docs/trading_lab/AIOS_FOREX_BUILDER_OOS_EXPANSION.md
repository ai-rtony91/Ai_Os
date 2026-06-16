# AIOS Forex Builder OOS Expansion

This packet expands local out-of-sample evidence for paper-forward forex validation.

It is local simulation only. It does not connect to a broker, read credentials, use network data, place broker-paper orders, or authorize live trading.

## What Changed

- Expanded deterministic local fixtures across EURUSD, GBPUSD, USDJPY, 5m, 15m, trend, chop, range, pullback, volatile, reversal, and low-vol regimes.
- Added expanded OOS splits for regime, symbol, timeframe, leave-one-group, weak-regime holdout, stress-repair-focused holdout, and rotating train/test windows.
- Added degradation scoring so heldout performance is compared against train-like performance instead of only checking positive PnL.
- Added compact OOS expansion output for operator review.

## OOS Split Types

- `holdout_by_regime`
- `holdout_by_symbol`
- `holdout_by_timeframe`
- `leave_one_regime_out`
- `leave_one_symbol_out`
- `leave_one_timeframe_out`
- `weak_regime_holdout`
- `stress_repaired_holdout`
- `rotating_train_test_windows`

Each split reports heldout PnL, return percent, heldout consistency percent, degradation percent, blockers, and classification.

Allowed classifications are `FAIL`, `WATCHLIST`, and `PAPER_FORWARD_READY`.

`PAPER_FORWARD_READY` is not live readiness. It only means the local deterministic OOS checks survived the current paper-forward review gate.

## Demo

```powershell
python -m automation.forex_engine.run_oos_expansion_demo
```

The output is compact and reportless by default:

```text
AIOS Forex OOS Expansion Demo
Mode: PAPER_ONLY
Fixtures: <n>
Splits: <n>
Heldout consistency pct: <value>
Max degradation pct: <value>
Weakest split: <id>
Classification: <FAIL/WATCHLIST/PAPER_FORWARD_READY>
Broker-paper contract ready: false
Live ready: false
Protected gate required: true
Safety: no broker/API/network/live execution.
```

## Interpretation

Good local OOS evidence is not real money. It does not prove broker-paper sandbox readiness by itself, and it never authorizes live trading.

`WATCHLIST` is an honest result when heldout coverage, degradation, weak-regime behavior, or stress repair evidence is still not strong enough. A future broker-paper sandbox packet requires separate protected approval for broker choice, credentials handling, network/API use, paper account access, order translation, kill switch, audit logging, daily stop policy, and human owner confirmation.
