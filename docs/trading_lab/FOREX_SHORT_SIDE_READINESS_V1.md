# FOREX_SHORT_SIDE_READINESS_V1

## Purpose

Add a separate, paper/simulation-only readiness lane for short-side Forex execution.

The short lane must remain isolated from existing long logic and can only emit review-ready output.

## Scope

- Confirm short signal validity (including sell/short intent).
- Confirm short-side broker permission and evidence availability.
- Verify spread/slippage guard behavior for short entries.
- Verify short TP/SL direction (`SL` above entry, `TP` below entry).
- Validate short risk sizing and unsupported sizing patterns (`martingale`, `revenge`, `averaging`).
- Validate evidence replay presence.
- Confirm no live short execution is allowed until explicit owner short gate exists.

## Non-executing constraints

- No scheduler/daemon/Webhook/automation execution in this lane.
- No broker/live routing.
- No live short order creation.
- No capital increase without an explicit owner short gate.

## Output model

`apps/trading_lab.trading_lab.forex_short_side_readiness_v1.evaluate_short_readiness` and
`evaluate_short_batch` return read-only review bundles only:

- `allowed` for readiness review (not execution).
- `short_readiness` readiness flags.
- `blocked_reason` list when readiness gates fail.
- `safe_next_action` with explicit owner gate path.

## Mirrors and differences from long lane

- Short logic is directional only (`sell`/`short`) and mirrors the long signal structure.
- Stop loss / take profit placement and broker-side reverse rules are validated in the opposite direction.
- Live short execution must be approved by a separate short-readiness gate packet.
- This module is additive and does not change long-only execution behavior.
