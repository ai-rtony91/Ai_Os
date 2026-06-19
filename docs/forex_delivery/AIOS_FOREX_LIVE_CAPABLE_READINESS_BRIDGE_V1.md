# AIOS Forex Live-Capable Readiness Bridge V1

## Status

Status: READINESS_CONTRACT

Packet ID: AIOS-FOREX-LIVE-CAPABLE-READINESS-BRIDGE-V1

Zone: FOREX_LIVE_OPS

Human Owner: Anthony Meza

## Scope

This document defines the governed bridge between dashboard intent and future live-capable forex execution readiness.

It does not authorize live trading, broker writes, order placement, live close-trade actions, secret reads, API-token handling, account identifier handling, transaction identifier handling, package changes, runtime connector changes, commits, pushes, PR creation, or merge activity.

The bridge is a read-model contract. It makes the dashboard useful for profit-seeking operational review by showing which requirements are real, which requirements are missing, and why live execution remains blocked.

## Core Principle

AIOS may pursue profit only through risk-adjusted expectancy backed by current evidence. It must not claim guaranteed profit.

Live execution remains blocked unless every readiness gate is green and the Human Owner explicitly arms execution in a later packet.

## Overall Gate

The bridge must expose:

```text
LIVE_READY: true/false
BLOCKED_REASONS:
NEXT_SAFE_ACTION:
```

`LIVE_READY` defaults to `false`.

`LIVE_READY` may become `true` only when all of these are true:

- real market data source is approved for the intended trading use
- broker/account state is reconciled
- signal logic is available
- expected edge evidence is available
- risk governor approves the exact trade boundary
- exit plan is ready before entry
- trading history writeback is available
- secret-safe runtime status is available without exposing secrets
- Human Owner explicitly arms execution

## 1. Live Data Readiness

Every live data readiness projection must include:

| Field | Requirement |
| --- | --- |
| `DATA_SOURCE_NAME` | Non-secret source label safe for display. |
| `DATA_SOURCE_TYPE` | One of `fixture`, `paper`, `broker-live-read-only`, or `broker-live-execution`. |
| `FRESHNESS_TIMESTAMP_UTC` | Timestamp of the source snapshot or `UNKNOWN`. |
| `STALE_OR_VALID_STATUS` | `VALID`, `STALE`, `BLOCKED`, or `UNKNOWN`. |
| `LIVE_TRADING_ALLOWED_FROM_THIS_SOURCE` | `true` only when source permission, freshness, and trading-use gates pass. |
| `BLOCK_REASON` | Required when live trading from the source is not allowed. |
| `SECRET_VALUES_PRINTED` | Must be `false`. |
| `ACCOUNT_IDS_PRINTED` | Must be `false`. |

Fixture, delayed, stale, demo, unverified, or unlabeled data blocks live execution.

## 2. Broker State Readiness

Broker/account readiness is read-only and sanitized. It must include:

| Field | Requirement |
| --- | --- |
| `ACCOUNT_REACHABLE` | `true/false`; no account identifiers printed. |
| `BROKER_MODE` | `demo`, `paper`, `live`, or `UNKNOWN`. |
| `OPEN_POSITIONS_RECONCILED` | `true/false`. |
| `PENDING_ORDERS_RECONCILED` | `true/false`. |
| `DAILY_PL_AVAILABLE` | `true/false`. |
| `MARGIN_RISK_AVAILABLE` | `true/false`. |
| `BLOCK_REASON` | Required when any broker/account readiness field blocks execution. |

Unknown broker/account state fails closed. The dashboard may display status, not raw broker payloads.

## 3. Signal Readiness

Signal readiness must include:

| Field | Requirement |
| --- | --- |
| `SELECTED_PAIR` | Sanitized pair symbol selected for review. |
| `STRATEGY_NAME` | Strategy identity, not a vague label. |
| `SIGNAL_SIDE` | `BUY`, `SELL`, or `NONE`. |
| `CONFIDENCE` | Numeric or labeled confidence with source context. |
| `EXPECTED_EDGE_EVIDENCE_PATH` | Repo-safe evidence path or `UNAVAILABLE`. |
| `BACKTEST_OR_PAPER_EVIDENCE_REQUIRED` | `true/false`. |
| `SPREAD_SLIPPAGE_STATUS` | `VALID`, `BLOCKED`, `UNVERIFIED`, or equivalent safe status. |
| `BLOCK_REASON` | Required when signal readiness is not complete. |

Fixture ranking, visual chart review, or blind clicking must not become a live signal.

## 4. Risk Readiness

Risk readiness must include:

| Field | Requirement |
| --- | --- |
| `MAX_UNITS` | Exact maximum units or `NOT_APPROVED`. |
| `MAX_TRADE_RISK` | Exact maximum risk or `NOT_APPROVED`. |
| `DAILY_LOSS_CAP` | Exact cap or `NOT_APPROVED`. |
| `ONE_POSITION_RULE` | Required before live execution. |
| `NO_REVENGE_LOOP_RULE` | Required before live execution. |
| `NO_DUPLICATE_ENTRY_RULE` | Required before live execution. |
| `KILL_SWITCH_REQUIRED` | Required before live execution. |
| `RISK_GOVERNOR_APPROVAL` | `true/false`. |
| `BLOCK_REASON` | Required when the risk governor has not approved. |

Risk governor approval is necessary but not sufficient. It does not bypass data, broker, signal, exit, history, secret, or Human Owner arming gates.

## 5. Exit Readiness

Exit readiness is evaluated before entry. It must include:

| Field | Requirement |
| --- | --- |
| `STOP_LOSS_REQUIRED_BEFORE_OR_WITH_ENTRY` | Must be enforced before or with entry. |
| `TAKE_PROFIT_POLICY` | Required, or an explicit approved no-take-profit reason. |
| `TRAILING_STOP_POLICY` | Required when the selected strategy depends on trailing protection. |
| `MAX_TIME_POLICY` | Required before live execution. |
| `AUTO_EXIT_READINESS` | `READY` or blocked status. |
| `MANUAL_CLOSE_FALLBACK` | Required fallback path. |
| `BLOCK_REASON` | Required when exit readiness is not complete. |

No entry may proceed when the exit plan is absent, unknown, stale, or outside the Human Owner-approved risk boundary.

## 6. Trading History Writeback Readiness

Live execution is blocked when trading history writeback is unavailable.

Every opened trade must create a sanitized evidence row. Every close must record realized P/L when safely available.

Each closed-trade evidence row must include:

```text
PAIR:
SIDE:
UNITS:
ENTRY_TIME:
EXIT_TIME:
DURATION:
REALIZED_PL:
EXIT_REASON:
SLIPPAGE_IF_AVAILABLE:
SOURCE:
FRESHNESS:
```

Writeback evidence must not contain secrets, account IDs, raw broker payloads, private order identifiers, transaction identifiers, tokens, or private credential material.

## Dashboard Bridge Behavior

Dashboard buttons may request or display readiness read-models. They must not create broker truth, order truth, approval truth, signal truth, P/L truth, or history truth.

Until every gate is green, the dashboard must show:

```text
LIVE_READY: false
ACTION_MODE: READ_ONLY
LIVE_BUY_SELL_BUTTON: NOT_PRESENT
```

## Default Blocked State

The safe default state is:

```text
LIVE_READY: false
NEXT_SAFE_ACTION: Connect permitted read-only data and broker reconciliation in a later packet, then run paper signal execution before any live arming gate.
```

## Stop Conditions

Stop any future implementation if it would:

- place or close a live trade
- add live BUY/SELL behavior
- call broker write APIs
- read secrets or `.env` files
- display account IDs
- display API tokens
- display raw broker payloads
- display transaction identifiers
- treat fixture, stale, delayed, demo, or unverified data as live-tradable
- skip paper evidence before live arming
- skip Human Owner arming before live execution
