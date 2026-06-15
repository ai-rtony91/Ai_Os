# AIOS Forex Builder Stress and Out-of-Sample Validation

This layer makes paper-forward evidence harder to fool. It does not try to make the number larger. It tests whether local simulated performance survives deterministic stress and heldout fixture checks.

## Scope

- Local simulation only.
- Deterministic local Python fixtures only.
- No broker integration.
- No broker paper trading.
- No live trading.
- No credentials, secrets, environment reads, webhooks, scheduler, daemon, network market data, API ingestion, or real orders.

## Stress Tests

The stress runner applies deterministic scenarios to the paper-forward evidence:

- base
- double_spread
- double_slippage
- double_spread_double_slippage
- half_capture_rate
- minus_best_regime
- plus_drawdown_penalty
- conservative_extreme
- disaster_case

Each scenario reports stressed paper PnL, stressed return percent, drawdown penalty, classification, blockers, and protected-gate status. The disaster case is allowed to fail; it exists to show the edge boundary instead of hiding it.

## Out-of-Sample Checks

The OOS validator splits local fixtures into train-like and heldout groups, then runs:

- heldout fixture validation
- leave-one-regime-out validation
- leave-one-symbol-out validation
- leave-one-timeframe-out validation

The result reports heldout PnL, heldout return percent, heldout consistency, weakest holdout, strongest holdout, degradation percent, blockers, and classification.

## Interpretation

PAPER_FORWARD_READY means the local simulation evidence survived the current deterministic stress and OOS gates. It is not LIVE_READY. It is not broker-paper approval. Good local PnL is not real money, and simulated spreads, slippage, exits, fills, and data coverage are still approximations.

If stress or OOS fails, AIOS must improve the blocker named in the result before advancing. If both pass, the next safe step is a broker-paper sandbox readiness contract, not broker integration.

## Demo

```powershell
python -m automation.forex_engine.run_stress_and_oos_demo
```

Expected fields include fixtures, stress scenarios, stress survival percent, heldout consistency, worst stress PnL, degradation percent, combined classification, live ready false, protected gate required true, and the next safe action.
