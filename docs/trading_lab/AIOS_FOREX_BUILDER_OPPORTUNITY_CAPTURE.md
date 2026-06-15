# AIOS Forex Builder Opportunity Capture

Opportunity capture measures whether the local paper-forward bot is capturing risk-adjusted simulated expectancy.

Risk-adjusted opportunity capture means capturing more valid edge after risk, cost, regime, and drawdown checks. It does not mean reckless overtrading, bypassing risk, deleting losing regimes, lowering costs to improve a score, or tuning numbers to inflate PnL.

## Metrics

- `capture_rate_pct`: simulated ledger entries divided by intents plus estimated missed signals
- `missed_signal_count`: conservative estimate from intent and simulated-entry gaps
- `missed_pnl_estimate`: conservative local estimate of uncaptured simulated PnL
- `cost_drag_pct`: estimated local round-turn cost drag against paper PnL
- `risk_adjusted_return`: return adjusted by drawdown and cost drag
- `exit_efficiency_pct`: estimated capture of positive versus adverse fixture PnL
- `position_efficiency_pct`: conservative sizing efficiency estimate
- `opportunity_quality_score`: blended local score for capture, exit, size, costs, drawdown, missed edge, and risk-adjusted return

## Balance Visibility

The default starting balance is `500.00`. Every risk-governor summary must show starting balance, ending balance, aggregate paper PnL, and return percent. A large local paper return is not live-realistic evidence by itself and must be stress tested.

## Boundary

This is local simulation only. It is not broker paper trading and does not prove live readiness. It does not read network data, secrets, broker state, environment credentials, or external feeds. Live trading remains blocked until a separate protected approval packet exists.

## Safe Next Step

Use opportunity capture to decide which local threshold must improve next. After this packet, the safer escalation is `PKT-AIOS-PAPER-FORWARD-STRESS-AND-OUT-OF-SAMPLE-V1`.
