# AI_OS Screener Dashboard Contract Draft

## Purpose

This draft defines the first safe contract for showing future screener output in an AI_OS dashboard.

The contract is visibility-only. It allows a future dashboard to display validated screener fields without enabling trading execution, broker routing, webhook firing, credential access, auto-routing, or strategy activation.

## Scope

Allowed future use:

- Read a pre-approved screener output record.
- Validate required fields before display.
- Show signal status in a dashboard panel.
- Mark execution state as blocked unless a separate future approval changes the boundary.

Not allowed:

- No live execution.
- No broker routing.
- No webhook firing.
- No credential access.
- No auto-routing.
- No strategy activation.
- No broker order placement.
- No live trading.

## Required Screener Output Fields

Future screener output shown in the dashboard must include these fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `symbol` | YES | Market symbol or instrument label. |
| `signal_type` | YES | Signal category such as observe, alert, risk_only, or blocked. |
| `signal_strength` | YES | Human-readable signal strength. |
| `confidence_score` | YES | Bounded confidence score for display only. |
| `risk_state` | YES | Current risk state for the signal. |
| `execution_allowed` | YES | Must remain `false` until separate approval. |
| `approval_required` | YES | Must remain `true` for any action beyond display. |

## Contract Rules

1. `execution_allowed` must remain `false` until a separate approval explicitly authorizes a later stage.
2. `approval_required` must remain `true` for any workflow that could affect trading, broker routing, credentials, webhooks, strategy activation, or order placement.
3. Dashboard display must treat screener output as informational only.
4. A screener signal is not a trade instruction.
5. A screener signal is not broker authorization.
6. A screener signal is not strategy activation.
7. A screener signal must not trigger webhooks, daemons, services, scheduled tasks, startup tasks, or auto-routing.

## Safe Example

```json
{
  "symbol": "UNKNOWN",
  "signal_type": "observe",
  "signal_strength": "low",
  "confidence_score": 0.0,
  "risk_state": "blocked",
  "execution_allowed": false,
  "approval_required": true
}
```

## Dashboard Boundary

The dashboard may display contract-compliant screener records in a future approved stage. The dashboard must not create, submit, queue, route, simulate, or place orders from this contract.

Any future extension that changes `execution_allowed` from `false` is outside this draft and requires a separate approval gate, updated risk policy review, paper-trading validation, and explicit human approval.
