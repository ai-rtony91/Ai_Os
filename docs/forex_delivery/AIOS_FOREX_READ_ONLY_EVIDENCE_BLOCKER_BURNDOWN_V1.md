# AIOS Forex Read-Only Evidence Blocker Burndown V1

## Purpose

This packet tightens read-only evidence approval so readiness blockers are reduced only by real sanitized evidence. It does not implement auto-exit, live execution, broker writes, or Human Owner execution approval.

## Approved Evidence Criteria

Read-only evidence may reduce future live-review blockers only when the source is sanitized broker read-only evidence, the source is valid, the broker/account is reachable, open-position state is reconciled, and the capability flags confirm that broker writes, order placement, and close trade actions remain blocked.

Fixture or blocked evidence remains unapproved and must keep the fixture/not-live blocker.

## False-Positive Private Marker Fix

The approval scanner evaluates private values rather than safe status field names. Safe fields such as “not recorded” account/order/transaction status values do not trigger `secret_or_private_identifier_marker_present`.

The scanner still blocks bearer-like token values, raw broker payload values, and non-safe account/order/transaction identifier values.

## Account P/L Versus Daily P/L

Account-level P/L evidence is not the same as a verified daily P/L ledger.

- `account_pl_available` means sanitized account-level realized or unrealized P/L is present.
- `daily_pl_available` means a daily P/L ledger or daily P/L evidence is verified.
- If account P/L exists but daily P/L does not, the daily P/L blocker remains with `daily_pl_block_reason: daily P/L ledger not verified`.

## Trading History Writeback Verification

Trading history writeback is verified only when sanitized broker read-only evidence includes a trading-history row or a separate sanitized history writeback evidence path. Fixture-only history does not verify writeback.

If writeback is not verified, `real_trading_history_writeback_not_verified` remains.

## Live Execution Still Blocked

This packet never sets `live_execution_allowed` true, never sets `EXECUTION_REVIEW_READY` true by default, and never places a trade. Live BUY, SELL, close, broker write calls, order placement, secret reads, and account/order/transaction identifier output remain blocked.

## Next Target

```text
AIOS-FOREX-AUTO-EXIT-LIVE-READINESS-V1
```

Auto-exit live readiness and real trading-history writeback verification are the next readiness targets before any future execution packet can be considered.
