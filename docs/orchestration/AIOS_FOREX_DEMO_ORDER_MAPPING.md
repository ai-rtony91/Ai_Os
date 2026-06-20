# AIOS Forex Demo Order Mapping

## Purpose

`automation/forex_engine/demo_order_mapping.py` converts an approved paper order preview or paper fill into a sanitized `DEMO_ORDER_INTENT` payload.

This is mapping only. It does not submit, route, write, connect, authenticate, or call broker/network APIs.

## Inputs

- Approved order preview with `allowed: True` and `approval_state: paper_preview_ready`.
- Or paper fill result with sanitized fill fields.
- Sanitized demo connector read-only state with `allowed: True` and `fresh: True`.

## Output

The mapper returns an envelope with:

- `allowed`
- `decision`
- `blocked_reason`
- `blocked_reasons`
- `warnings`
- `mode: DEMO_MAPPING_ONLY`
- `demo_order_intent`
- `submit_enabled: False`
- `broker_write_enabled: False`
- `live_trading: False`
- `safety`
- `next_safe_action`
- `metadata`

The nested `demo_order_intent` includes:

- `pair`
- `side`
- `units`
- `order_type`
- `entry_price`
- `stop_loss`
- `take_profit`
- `client_order_id`
- `idempotency_key`
- `mode: DEMO_MAPPING_ONLY`
- `submit_enabled: False`
- `broker_write_enabled: False`
- `live_trading: False`
- `safety`

## Blockers

The mapper blocks when:

- The preview is not allowed.
- The preview approval state is not `paper_preview_ready`.
- The connector read-only state is not allowed.
- The connector read-only state is stale.
- Account identifier material is present.
- Credential-loaded flags are present.
- Broker write, order submit, network submit, or live trading flags are enabled.
- Units are invalid.
- Stop-loss or take-profit fields are missing.
- Pair, side, or order type is unsupported.

## Safety

All emitted intents remain `DEMO_MAPPING_ONLY`. The module does not import broker SDKs, perform network access, read runtime secrets, write files, or submit orders.
