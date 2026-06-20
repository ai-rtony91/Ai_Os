# AIOS Forex Paper Trade Model (V1)

## Purpose

This model defines a canonical, paper-only lifecycle representation for trading opportunities and paper trade execution state inside AI_OS Trading Lab. It is intentionally model-only logic for planning, validation, and deterministic state transitions.

## Paper-only boundary

Every returned trade payload includes a strict safety map:

```python
{
    "paper_only": True,
    "broker": False,
    "live_trading": False,
    "credentials": False,
    "real_orders": False,
    "network_access": False,
}
```

No code in this model submits broker calls, writes files, opens network connections, or accesses credentials.

## Canonical lifecycle fields

`automation/forex_engine/paper_trade_lifecycle.py` models the following fields:

- `trade_id`
- `pair`
- `direction` (`buy`, `sell`)
- `entry_type` (`market`, `limit`, `stop`)
- `entry_price`
- `stop_loss`
- `take_profit`
- `units`
- `dollar_risk`
- `percent_risk`
- `status`
- `created_timestamp`
- `opened_timestamp`
- `closed_timestamp`
- `close_reason`
- `realized_pnl`
- `evidence_path`
- `paper_only`
- `safety`
- `blocked_reason`
- `lifecycle_history`
- `metadata`

## Canonical statuses

- `candidate`
- `previewed`
- `rejected`
- `queued`
- `opened`
- `active`
- `closed`
- `killed`
- `expired`
- `error`

## Allowed transitions

- `candidate -> previewed`
- `candidate -> rejected`
- `previewed -> queued`
- `previewed -> rejected`
- `queued -> opened`
- `queued -> expired`
- `queued -> killed`
- `opened -> active`
- `opened -> closed`
- `opened -> killed`
- `opened -> error`
- `active -> closed`
- `active -> killed`
- `active -> expired`
- `active -> error`

Terminal statuses are:

- `rejected`
- `closed`
- `killed`
- `expired`
- `error`

Any terminal-to-non-terminal transition is rejected.

## Rejection behavior

- Invalid statuses.
- Invalid trade content (missing IDs, invalid direction/entry type, non-positive price/units/risk constraints).
- Blocked lifecycle transitions.
- Unsafe payloads that mutate the paper-only boundary.

Invalid transitions raise `ValueError` from `transition_paper_trade`.

## API surface

`PAPER_TRADE_STATUSES`
`TERMINAL_PAPER_TRADE_STATUSES`
`PAPER_TRADE_ALLOWED_TRANSITIONS`
`build_paper_trade(...)`
`validate_paper_trade(trade)`
`transition_paper_trade(...)`
`paper_trade_to_dict(trade)`
`paper_trade_from_dict(payload)`

`validate_paper_trade` returns:

```json
{
  "valid": bool,
  "blocked_reason": "none" | "string",
  "errors": ["..."],
  "warnings": ["..."],
  "paper_only": True,
  "next_safe_action": "..."
}
```

## Relationship to `automation/forex_engine/models.py`

This packet does not replace or rename the existing `automation.forex_engine.models.PaperTrade`.
`PaperTrade`, `TradeStatus`, and `TradeOutcome` remain unchanged to avoid breaking legacy imports in:

- `automation/forex_engine/paper_execution.py`
- existing tests and existing paper signal execution scaffolding

The new model intentionally focuses on lifecycle and paper-trade-state transitions and uses only standard library types.

## Why this does not enable broker/fill/live behavior

This file never writes fills, orders, secrets, credentials, network calls, or broker payloads.
It returns structured trade state only.
Paper fills and broker submits are handled elsewhere and intentionally not introduced here.

Dashboard ownership in Trading Lab still treats trade truth as display/projection of paper state and
must not use this module to create mutable trading truth in live-orchestrated components.

## Next safe packet

After this model lands, proceed with:

- `FOREX-RISK-GOVERNOR` for deterministic risk gate policy
- or `FOREX-POSITION-SIZING` if repo state requires position budgeting next.

