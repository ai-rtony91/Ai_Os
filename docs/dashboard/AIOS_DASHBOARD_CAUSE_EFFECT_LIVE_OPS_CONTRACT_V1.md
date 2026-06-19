# AIOS Dashboard Cause/Effect Live Ops Contract V1

## Scope

This packet upgrades the Minimal Operator Dashboard from visual navigation only to a read-only cause/effect operating contract. It prepares the UI to display AIOS forex operations truth without creating that truth.

This packet does not add broker writes, live BUY/SELL, live close-trade behavior, secret reads, account identifiers, tokens, transaction identifiers, package changes, or live-trading wiring.

## Core Rule

The dashboard displays truth. The dashboard does not create truth.

Navigation buttons may open pages and describe the read-model they expect. They must not directly create broker truth, account truth, order truth, approval truth, or trading-history truth.

## Button Cause/Effect Model

| Button | Cause | Effect |
| --- | --- | --- |
| Watchlist | Request latest available watchlist/opportunity snapshot from the AIOS read-model source. | Display ranked pairs, score, confidence, trend, data source, freshness, and live-trading permission. |
| Position | Request broker/account position reconciliation read-model. | Display open position, units, entry price if available, realized P/L, unrealized P/L, freshness, and source label. |
| Risk / P&L | Request risk governor and P/L truth read-model. | Display daily loss cap, max position size, realized P/L, unrealized P/L, current risk status, and blocked/allowed state. |
| Exit | Request exit readiness/readiness-plan evaluation for any current open trade. | Display stop-loss present, take-profit policy, trailing stop policy, max-time policy, auto-exit readiness, and block reason. |
| Trading History | Request sanitized closed-trade and execution-evidence read-model. | Display closed trades, realized P/L, exit reason, protection controls used, slippage, evidence status, source, and freshness when available. |

## Trading History Page

Trading History is a new Forex Bot navigation target.

Current behavior:

- It is read-only.
- It does not invent real trade history.
- It displays `NO_REAL_HISTORY_AVAILABLE` when no sanitized real closed-trade evidence exists.
- It labels fixture/demo state clearly as `FIXTURE_NOT_LIVE`.
- It preserves source, freshness, and `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false` labeling.

Future sanitized history rows may include:

- pair
- side
- units
- entry time
- exit time
- duration
- realized P/L
- exit reason
- stop-loss used
- take-profit used
- trailing stop used
- max-time used
- slippage
- evidence status
- source/freshness

## Exit Page Meaning

Exit is not Trading History.

Exit evaluates whether a current or future open trade is protected and exit-ready. It may display readiness controls and block reasons. It must not close trades directly in this packet.

## UI Safety Requirements Preserved

- Top page identity remains emoji-only.
- Lower page content uses text-only labels.
- Home and Forex navigation remain icon-first.
- Routing remains local UI routing.
- Source truth labels remain visible.
- Freshness is displayed when available from the read-model source.
- `READ_ONLY`, `BLOCKED`, `FIXTURE_NOT_LIVE`, and `NO_REAL_HISTORY_AVAILABLE` meanings remain visible.
- `LIVE_TRADING_ALLOWED_FROM_THIS_DATA: false` remains visible for fixture data.

## Stop Conditions

Stop future dashboard implementation if any change would:

- call broker write APIs
- place or close a live trade
- read or display secrets
- expose account IDs, tokens, order IDs, transaction IDs, or raw broker payloads
- imply fixture data is live-tradable
- let a button bypass approval, risk, P/L truth, auto-exit, secret, broker, or kill-switch gates
