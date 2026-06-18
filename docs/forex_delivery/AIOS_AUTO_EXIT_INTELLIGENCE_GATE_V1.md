# AIOS Auto Exit Intelligence Gate V1

## Status

Status: REQUIRED_BEFORE_FUTURE_LIVE_TRADING

Zone: FOREX_DELIVERY

Human Owner: Anthony Meza

Related backlog: `docs/forex_delivery/AIOS_MASTER_OPERATOR_DASHBOARD_FOREX_AUTONOMY_BACKLOG_V1.md`

## Purpose

This document defines the canonical auto-exit intelligence gate for future governed AIOS forex trading. It is a planning and readiness contract only. It does not authorize live trading, broker API use, secret access, dashboard mutation, validator changes, or runtime implementation.

Future governed live forex trades must have a complete exit plan before entry. Entry is blocked if exit controls are missing.

## Operating Principle

The Human Owner sets the risk boundary.

AIOS manages the trade inside that approved boundary.

The Human Owner should not babysit open trades.

AIOS must fail closed when exit controls, reconciliation, or risk-boundary enforcement are missing.

## Gate Rule

Before any future governed live forex entry, AIOS must prove that the exit plan exists, is bounded by the approved risk cap, and can be reconciled after action. The gate is evaluated before entry, not after a position is already open.

If any required exit control is missing, AIOS blocks entry.

No larger live forex workflow may treat first-entry readiness as complete unless this auto-exit gate and the P/L truth layer are both satisfied.

## Required Exit Controls

- stop-loss
- take-profit or explicit no-take-profit reason
- break-even stop
- trailing stop
- close-on-profit
- max-time-in-trade
- close-if-spread-widens
- close-if-signal-invalidates
- close-if-loss-cap-threatened
- fail-closed reconciliation
- one-position lock
- no retry
- no loop
- no autonomous repeat unless separately approved

## Gate Result Model

Future implementation packets should produce a structured result with these fields:

```text
AUTO_EXIT_READY: true/false
BLOCK_REASON:
EXIT_PLAN_PRESENT:
STOP_LOSS_PRESENT:
TAKE_PROFIT_POLICY_PRESENT:
BREAK_EVEN_POLICY_PRESENT:
TRAILING_STOP_POLICY_PRESENT:
MAX_TIME_POLICY_PRESENT:
SPREAD_WIDEN_EXIT_PRESENT:
SIGNAL_INVALIDATION_EXIT_PRESENT:
LOSS_CAP_EXIT_PRESENT:
RECONCILIATION_PRESENT:
```

`AUTO_EXIT_READY` may be `true` only when every required control is present, coherent, and inside the Human Owner-approved risk boundary.

`BLOCK_REASON` must be populated whenever `AUTO_EXIT_READY` is `false`.

## Block Conditions

AIOS must block entry when any of these are true:

- the exit plan is absent
- stop-loss is absent
- take-profit policy is absent and no explicit no-take-profit reason exists
- break-even policy is absent
- trailing-stop policy is absent
- max-time-in-trade policy is absent
- spread-widen exit is absent
- signal-invalidation exit is absent
- loss-cap exit is absent
- reconciliation is absent
- one-position lock is absent
- retry, loop, or autonomous-repeat behavior is present without separate approval
- required P/L truth-layer evidence cannot be captured
- secret-safe runtime handling is not available
- broker/API or live-trading approval is absent

## Risk Boundary

Human approval defines the maximum risk envelope. AIOS may manage only inside that boundary. The exit plan must never expand risk beyond the approved cap, increase position exposure without approval, retry failed live actions, loop order attempts, or repeat autonomously unless a separate packet explicitly approves that behavior.

## Reconciliation Requirement

Exit readiness requires fail-closed reconciliation. AIOS must be able to determine whether the trade is open, closed, partially closed, blocked, or unknown. Unknown state is a stop condition.

Reconciliation evidence must remain sanitized. It must not record secrets, account IDs, raw broker payloads, endpoint secrets, private order identifiers, or credential material unless a future explicit approval defines a safe exception.

## Relationship To Dashboard And Operator Flow

The dashboard may display the auto-exit result, block reason, current position state, and next safe action. The dashboard does not create this truth. It must read from approved evidence produced by future runtime or validation packets.

The PowerShell terminal remains the engineering/control-plane workspace. The broker website remains fallback, verification, and emergency manual intervention only.

## Future Execution Dependencies

Future implementation packets should be separate and scoped:

1. Auto-exit result schema packet.
2. Exit-plan validator packet.
3. P/L truth-layer schema packet.
4. One-position lock and no-retry policy packet.
5. Fail-closed reconciliation packet.
6. Dashboard display-only projection packet.
7. Broker fallback verification workflow packet.

Each future packet must preserve the no-secret, no-broker-call, no-live-trade default boundary unless separately approved by the Human Owner.

## Stop Conditions

Stop if:

- exit controls are incomplete
- P/L truth evidence is unavailable
- risk boundary is unclear
- reconciliation cannot fail closed
- secret-safe runtime handling is missing
- live-trading approval is absent
- broker/API behavior would be introduced without approval
- dashboard behavior would create truth instead of displaying truth
- retry, loop, or autonomous-repeat behavior appears without separate approval

