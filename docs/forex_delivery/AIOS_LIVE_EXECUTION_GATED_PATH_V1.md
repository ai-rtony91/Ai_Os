# AIOS Live Execution Gated Path V1

## Scope

This document defines the future gated path from read-only dashboard operation toward governed live forex execution.

It is documentation only. It does not authorize broker/API writes, live BUY/SELL, live close-trade behavior, secret reads, credential handling, account identifiers, order identifiers, transaction identifiers, runtime connector changes, or live-trading wiring.

## Principle

Live execution requires gated action plans, not direct blind clicks.

The dashboard may display status, readiness, and next safe action. It must not create execution truth or approval truth.

## Gated Path

### Stage 1: Read-Only Live Data Bridge

Goal: prove AIOS can display permissioned live or demo read-model data without secrets or private payloads leaking into the dashboard.

Required gates:

- approved data source label
- freshness timestamp
- live-trading permission flag
- block reason when not tradable
- sanitized broker/account state when available
- no raw broker payloads
- no account IDs, tokens, order IDs, or transaction IDs

### Stage 2: Paper/Sandbox Execution Button

Goal: introduce a non-live execution action only after the read-only bridge and risk display are reliable.

Required gates:

- paper/sandbox-only execution boundary
- visible risk cap
- P/L truth readback
- auto-exit readiness
- kill switch visible and tested
- reconciliation writeback to sanitized history

### Stage 3: Live Micro-Trade Arm Button

Goal: prepare a live micro-trade request without placing the trade.

Required gates:

- Human Owner-approved risk boundary
- one-position lock
- max position size
- daily loss cap
- stop-loss policy
- take-profit or exit policy
- trailing and max-time policy where required
- P/L truth layer
- secret bridge ready status without exposing secrets
- broker bridge ready status without exposing private identifiers

### Stage 4: Human Approval Confirmation

Goal: require explicit Human Owner confirmation before live execution.

Required gates:

- exact pair
- exact side
- exact units
- exact risk cap
- exact stop/exit plan
- current source label and freshness
- blocked/allowed gate result
- no stale, fixture, demo, or unverified data used for live execution

### Stage 5: Broker Execution

Goal: execute only the approved live micro-trade through a future approved broker adapter.

Required gates:

- broker/API write behavior separately approved
- no blind retries
- no autonomous loops
- fail-closed on API, risk, source, or reconciliation error
- no raw broker payloads in dashboard output
- no secrets or private identifiers in repo docs or UI

### Stage 6: Reconciliation And Trading-History Writeback

Goal: reconcile execution outcome and write sanitized evidence to the Trading History read-model.

Required gates:

- execution status
- position status
- realized P/L when closed
- unrealized P/L when open
- exit reason
- protection controls used
- slippage when safely available
- evidence completeness status
- source/freshness
- sanitized output only

## Default Block

Until every required gate is implemented and separately approved, AIOS dashboard execution remains read-only and blocked for live trading.

The current dashboard may show `READ_ONLY`, `BLOCKED`, `FIXTURE_NOT_LIVE`, or `NO_REAL_HISTORY_AVAILABLE`. Those labels are safety truth, not blockers to remove casually.
