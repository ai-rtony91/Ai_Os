# AI_OS Macro Awareness Engine 001

Stage 15.12 creates the first macro-awareness and market-context intelligence layer for AI_OS.

This layer is risk-awareness only. It is not autonomous news trading, headline chasing, internet-fed order routing, broker execution, or live trading.

## Purpose

Macro awareness helps AI_OS recognize market conditions that can make otherwise valid paper signals unsafe or low quality. The layer modifies confidence, ranking, simulated size, and watch states. It does not execute.

## Market Conditions Tracked

- Economic-event risk.
- Abnormal volatility conditions.
- Session transitions.
- Central-bank event pressure.
- Spread instability.
- Liquidity instability.
- Cross-market stress behavior.
- Macro uncertainty environments.

## Event Awareness

The first model uses placeholders only:

- CPI placeholder.
- FOMC placeholder.
- NFP placeholder.
- ECB placeholder.
- BOJ placeholder.
- Session overlap awareness.
- Pre-event caution window.
- Post-event stabilization window.

## Macro States

- NORMAL
- ELEVATED_RISK
- HIGH_IMPACT_EVENT
- VOLATILITY_EXPANSION
- LIQUIDITY_WARNING
- RISK_OFF
- UNSTABLE
- LOCKDOWN

## Risk Reactions

- Reduce confidence.
- Freeze confidence increases.
- Reduce simulated size.
- Reduce portfolio exposure.
- Suppress unstable pair ranking.
- Activate WATCH state.
- Activate LOCKDOWN during severe instability.

## Architecture Principles

- Macro awareness informs risk.
- Macro awareness does not directly execute trades.
- No LLM in direct live order path.
- No autonomous headline trading.
- Market context modifies confidence only.
- Execution isolation remains permanent.

## Safety Boundary

- paper_only_status: PAPER_ONLY
- live_execution_status: BLOCKED
- broker_api_status: BLOCKED
- autonomous_execution_status: BLOCKED
- network_order_routing_status: BLOCKED

