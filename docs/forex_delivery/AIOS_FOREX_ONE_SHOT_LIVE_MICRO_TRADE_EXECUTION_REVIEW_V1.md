# AIOS Forex One-Shot Live Micro-Trade Execution Review V1

## Purpose

This packet adds the final non-executing review layer before any separately approved one-shot live micro-trade execution packet may be considered.

Execution review means AIOS evaluates sanitized evidence from the read-only bridge, paper signal loop, and live micro-trade arming gate. It does not execute, place orders, modify orders, close trades, read secrets, or call a broker.

## What Is Evaluated

- Read-only live data bridge evidence exists and includes source type, source label, freshness, broker/account reachability if available, open-position reconciliation if available, P/L availability if available, and trading-history availability or a block reason.
- Paper signal execution loop evidence exists and includes signal side, risk approval, paper entry, exit plan, paper close/reconcile, realized paper P/L, trading history writeback, and `live_execution_allowed: false`.
- Live micro-trade arming gate evidence exists and includes `LIVE_ARMABLE`, the arming phrase, and false broker write, order placement, close trade, and live execution flags.
- Final live prerequisites are reviewed: micro-sized units, max trade risk, daily loss cap, kill switch, one-position rule, no duplicate entry, no revenge loop, stop-loss, take-profit or waiver, max-time policy, manual broker UI fallback, trading history writeback, and no unreconciled duplicate live position.
- Proposed live micro units are aligned to the live micro-trade arming gate `max_units`. If the arming report omits `max_units`, the execution review defaults the maximum live micro size to `1`. Paper simulation unit size is not reused as proposed live size.

## What Remains Blocked

- Live BUY remains blocked.
- Live SELL remains blocked.
- Live close remains blocked.
- Broker write calls remain blocked.
- Order placement remains blocked.
- Secret reads remain blocked.
- Account, order, and transaction identifier values must not be recorded.

## Required Future Human Phrase

The phrase required in a future execution packet is:

```text
I AUTHORIZE ONE LIVE MICRO TRADE EXECUTION WITH MAXIMUM MICRO RISK
```

This phrase is documented for future review only. It is not consumed by this packet to execute anything.

## Next Packet Candidate

```text
AIOS-FOREX-ONE-SHOT-LIVE-MICRO-TRADE-EXECUTION-V1
```

That packet would require separate approval and must still pass broker, risk, exit, history, and human arming controls.

## Profitability

Profitability is not guaranteed. Any future execution must be risk-governed, proof-based, and limited to the approved one-shot micro-trade scope.

## How To Run The Review

```powershell
python scripts/forex_delivery/run_one_shot_live_micro_trade_execution_review.py
```

The script writes:

```text
Reports/forex_delivery/AIOS_FOREX_ONE_SHOT_LIVE_MICRO_TRADE_EXECUTION_REVIEW_DRY_RUN_V1.md
```

The script is dry-run only and does not require secrets, network access, or broker credentials.
