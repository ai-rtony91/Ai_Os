# Mock Alert Payload V0.1

## Purpose

This document describes the AIOS trader mock alert payload builder. The payload is a local data structure for previewing paper-only route decisions.

## Files Created

- `aios/modules/trader/payloads/__init__.py`
- `aios/modules/trader/payloads/alert_payload.py`
- `tests/trader/test_mock_alert_payload_v01.py`
- `docs/AI_OS/trader/payloads/MOCK_ALERT_PAYLOAD_V0_1.md`

## Payload Fields

- `schema_version`
- `source`
- `symbol`
- `timeframe`
- `permission`
- `signal`
- `confidence`
- `paper_only`
- `live_execution_status`
- `execution_allowed`
- `route_status`
- `timestamp`
- `metadata`

## Safety Rules

- Mock only.
- Paper-only by default.
- Live execution remains `BLOCKED`.
- `execution_allowed` remains `false`.
- No credentials or external route details are accepted.
- No order placement is provided.

## Validation Command

```powershell
python -m pytest tests/trader/test_mock_alert_payload_v01.py tests/trader/test_paper_route_preview_v01.py
```

This payload is mock only. It does not send webhooks, connect brokers, or place orders.
