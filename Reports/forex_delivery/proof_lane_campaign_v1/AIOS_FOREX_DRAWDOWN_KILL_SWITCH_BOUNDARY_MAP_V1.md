# AIOS Forex Drawdown and Kill-Switch Boundary Map V1

## 1. Status
`PARTIAL`

## 2. Configured limits

| Setting | Value | Role |
|---|---|---|
| `mode` | `PAPER_ONLY` | Global local-only operating mode |
| `starting_balance_usd` | `500.0` | Baseline account size used by the local model |
| `paper_risk_per_trade_pct` | `0.5` | Allowed paper risk per trade |
| `first_live_risk_target_pct` | `0.25` | Future-only live target, not active here |
| `max_daily_drawdown_pct` | `2.0` | Daily paper drawdown limit |
| `max_open_trades_paper` | `2` | Paper open-trade cap |
| `pause_after_consecutive_losses` | `3` | Loss-streak pause threshold |
| `minimum_confidence_to_trade` | `70` | Local confidence gate |
| `WEEKLY_DRAWDOWN_THRESHOLD_PCT` | `5.0` | Weekly risk-management threshold |
| `NEAR_DRAWDOWN_FRACTION` | `0.5` | Half-threshold used for reduce-risk behavior |

At the default balance, the configured paper order risk limit resolves to `2.50 USD`.

## 3. Paper-mode blocker behavior
- `automation/forex_engine/risk.py` blocks when mode is not `PAPER_ONLY`, when the open-trade cap is reached, when the consecutive-loss threshold is reached, when the daily drawdown limit is reached, or when the calculated risk amount is non-positive.
- `automation/forex_engine/risk_management.py` treats non-paper mode, validation failure, daily drawdown, weekly drawdown, loss streak, open-trade cap, exposure overflow, and oversize order risk as explicit breaches.
- `automation/forex_engine/paper_operator.py` raises alerts for the same local safety conditions and blocks the operator when validation is unhealthy or the mode is not paper.
- The exact limit and over-limit cases are intentionally distinct: the cap uses `>=`, while exposure overflow uses `>`.

## 4. Kill-switch escalation behavior
- `NON_PAPER_MODE`, `DAILY_DRAWDOWN`, and `WEEKLY_DRAWDOWN` are kill-switch breaches.
- `VALIDATION_FAILED` does not become a kill-switch breach in the same way, but `build_kill_switch_report` escalates it to `ACTIVE` and requires a reset before continuation.
- `LOSS_STREAK` pauses trading rather than triggering the kill switch.
- `MAX_OPEN_TRADES`, `EXPOSURE_TOO_HIGH`, and `ORDER_RISK_TOO_HIGH` block the order instead of escalating to a kill switch.
- `build_kill_switch_report` returns `TRIGGERED`, `ACTIVE`, or `INACTIVE` depending on the breach class.

## 5. Metrics/backtest drawdown evidence
- `automation/forex_engine/metrics.py` computes gross profit, gross loss, net PnL, profit factor, streaks, and max drawdown in USD and percent.
- The metrics output explicitly marks the result as `paper-only evidence; not a profitability claim`.
- `automation/forex_engine/backtest.py` carries max drawdown into the summary and labels the result as `PAPER_ONLY Supertrend edge candidate research; no live readiness or earnings claim.`
- The backtest loop closes open trades locally and never turns that calculation into broker truth.

## 6. Tests
- `tests/forex_engine/test_risk_management.py` covers daily drawdown, weekly drawdown, loss streak pauses, open-trade blocking, oversize blocking, non-paper mode kill-switch behavior, validation failure escalation, and kill-switch formatting.
- `tests/forex_engine/test_paper_operator.py` covers paper-only boundary alerts, loss streak alerts, daily drawdown alerts, weekly drawdown alerts, validation health alerts, operator posture, and demo import behavior.
- The tests also confirm that no live trading demo module exists and that the demo imports do not require network access.

## 7. Modularity assessment
- The limit math and kill-switch logic are cleanly separated from any broker transport.
- `config.py`, `risk.py`, `risk_management.py`, `metrics.py`, `backtest.py`, and `paper_operator.py` form a reusable local safety chain.
- The modules are suitable for paper/demo read-model work, but they are not a live broker stack.
- The code is deterministic enough to support a future receipt schema and validator without inventing new safety math.

## 8. Live broker enforcement gaps
- No broker SDK call path is present in the inspected safety chain.
- No order placement, order modification, order cancellation, or account mutation path is present.
- No credential read, token use, or account-ID exposure path is present.
- No network-bound live execution path is present in this local model.

## 9. What must stay paper/demo
- The configuration contract.
- The risk math and drawdown math.
- The local kill-switch model.
- The paper operator alerts and posture logic.
- The backtest summary and max-drawdown reporting.
- The paper-only tests that enforce the boundary.

## 10. What may be shared with live
- Pure drawdown formulas.
- Loss-streak counting.
- Risk threshold calculations.
- Read-only report formatting.
- Evidence summarization logic that never touches broker transport or credentials.

## 11. Claim allowed
- Paper-only local limits are explicit and tested.
- Local kill-switch and pause behavior is defined.
- Drawdown math is reusable for read-only evidence.

## 12. Claim blocked
- Live broker enforcement.
- Live-trading readiness.
- Broker-verified risk control.
- Profit claim.
- Execution claim.
