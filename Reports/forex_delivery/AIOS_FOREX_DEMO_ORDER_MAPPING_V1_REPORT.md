# AIOS Forex Demo Order Mapping V1 Report

## Packet

- Packet ID: `FOREX-DEMO-ORDER-MAPPING-V1`
- Mode: `LOCAL_APPLY_PATCH_ONLY`
- Scope: demo order mapping only

## Files Added

- `automation/forex_engine/demo_order_mapping.py`
- `tests/forex_engine/test_demo_order_mapping.py`
- `docs/orchestration/AIOS_FOREX_DEMO_ORDER_MAPPING.md`
- `Reports/forex_delivery/AIOS_FOREX_DEMO_ORDER_MAPPING_V1_REPORT.md`

## Mapping Contract

- Converts approved paper preview or sanitized paper fill fields into a nested `demo_order_intent`.
- Emits deterministic `idempotency_key` values from normalized intent fields.
- Keeps `mode` fixed to `DEMO_MAPPING_ONLY`.
- Keeps submission/write/live flags false in the envelope and nested intent.

## Safety Boundary

- No broker SDK imports.
- No network imports.
- No filesystem reads or writes.
- No environment or secret-material access.
- No order submission.
- No live trading.

## Tests Added

- Valid preview mapping.
- Paper fill mapping.
- Submit/write/network blockers.
- Account identifier, credential-loaded, live, and submit blockers.
- Preview readiness blockers.
- Connector allowed/fresh blockers.
- Invalid units, missing SL/TP, unsupported pair/side/order type blockers.
- Deterministic idempotency key.
- Safety dict verification.
- Source scan for broker, network, filesystem, and sensitive access patterns.

## Validators

- Not run by Codex per packet instruction.
