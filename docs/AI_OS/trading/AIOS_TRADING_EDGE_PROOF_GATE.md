# AIOS Trading Edge Proof Gate

## Purpose

The edge proof gate defines how AI_OS classifies paper-only trading research evidence. It prevents a backtest or demo from being treated as live approval.

## Classifications

- `FAIL`: evidence is too weak, unsafe, too small, or inconsistent.
- `WATCHLIST`: evidence has limited promise but needs more local data or stronger walk-forward consistency.
- `PAPER_FORWARD_READY`: strict paper evidence passed and can continue into paper-forward observation only.

No gate result authorizes live trading.

## Required Evidence

- Minimum sample size.
- Positive expectancy after costs.
- Profit factor threshold.
- Maximum drawdown cap.
- Losing streak cap.
- Walk-forward consistency.
- Explicit cost assumptions.
- No-trade reason accounting.
- No broker/API/live path.

## Blockers

- Too few trades.
- Costless-only winner.
- High drawdown.
- Long losing streak.
- Poor walk-forward consistency.
- Missing cost model.
- Any broker, credential, live order, webhook, scheduler, daemon, or network market ingestion path.

## Future Promotion Boundary

Any future promotion discussion requires a separate protected packet. It must include exact allowed paths, forbidden paths, validation, operator approval, no-secret handling proof, and an explicit stop condition.

This gate is for PAPER_ONLY evidence. It is not an execution policy and not a broker integration plan.
