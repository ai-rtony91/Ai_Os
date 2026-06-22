# AIOS Broker Threshold Sprint V7–V9

## Objective
Deliver the next protected-demo readiness spine:
- V7 protected demo connection preflight
- V8 protected read-only demo attempt controller
- V9 demo micro-trade approval packet

## Files Added
- `automation/forex_engine/broker_threshold_sprint_v7_v9.py`
- `tests/forex_engine/test_broker_threshold_sprint_v7_v9.py`
- `Reports/forex_delivery/AIOS_BROKER_THRESHOLD_SPRINT_V7_V9.md`

## Functional Summary
- Added offline-default deterministic verdict function for V7 preflight with strict blocking rules for demo-only, read-only, no persistence, and safe endpoint conditions.
- Added offline-default controller builder for a future protected read-only OANDA demo connection attempt with explicit runtime authorization checks.
- Added offline-default micro-trade approval packet builder that blocks on kill-switch/gates and missing approvals without executing any order or network call.

## Safety posture
- No live trading
- No broker credentials persisted
- No `.env` reads
- No default network calls
- No order execution
- No scheduler/daemon/webhook
- No account ID persistence
- No raw broker payload persistence

## Test scope
- V7–V9 focused tests added to `tests/forex_engine/test_broker_threshold_sprint_v7_v9.py`
- Regression set includes V6/V5/V4 and OANDA protected connection attempt tests
- Full `tests/forex_engine` suite requested
