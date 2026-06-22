# AIOS Broker Demo Effectiveness V2

## Objective
- Implement a protected, offline-default broker-demo connector readiness probe.
- Prove deterministic readiness to attempt future protected demo connector work without live trading, credentials, network calls, or order execution.

## What was added
- New probe module:
  - `automation/forex_engine/broker_demo_effectiveness_v2.py`
- New focused test coverage:
  - `tests/forex_engine/test_broker_demo_effectiveness_v2.py`
- New report artifact:
  - this document

## Added capabilities
- **Connector readiness contract**
  - Validates `connector_mode`, approvals, simulation/broker-demo markers, safety flags, and endpoint classification.
  - Requires explicit connector injection; missing connector fails closed.
- **Fail-closed verdict mapping**
  - `BROKER_DEMO_PROBE_READY`
  - `BROKER_DEMO_PROBE_BLOCKED`
  - `BROKER_DEMO_PROBE_CONNECTOR_REJECTED`
  - `BROKER_DEMO_PROBE_CONTRACT_INVALID` (contract constant retained for compatibility)
- **Connector readiness hardening**
  - Rejects live-mode flags (`network_allowed`, order route, account/market data requests, execution).
  - Rejects connector objects containing credential-like or account-id values.
- **Quote/account/instrument envelope validation**
  - Account placeholder shape and non-negative values.
  - Instrument symbol validation with live-symbol rejection.
  - Quote bid/ask/spread positivity, ask > bid, and stale quote rejection.
- **Sanitized readiness output**
  - Removes sensitive fields and does not persist raw network/credential/account artifacts.
  - Includes separate readiness evidence fields for offline/probe assertions.
- **Latency bucket contract**
  - Added V2 latency bucket report with explicit network-disabled placeholder and explicit offline separation.

## Safety constraints
- No live trading.
- No order execution.
- No broker credentials are read.
- No `.env` reads.
- No live network calls by default (`network_call_performed = False`).
- No scheduler, daemon, webhook, or background execution.
- No account IDs or broker payloads are persisted in probe output.

## Dry-run-only proof
- Evaluation is strictly deterministic and offline.
- Connector object must be explicitly provided and marked for demo safety.
- Contract and connector checks are in-memory and block on any unsafe capability.
- Connector/quote/account/instrument validations are non-mutating and side-effect free.

## Broker-demo readiness status
- Ready when all:
  - connector contract gates clear,
  - explicit approved demo connector is injected,
  - account/instrument/quote envelopes pass validation,
  - no forbidden fields/values are present.
- Otherwise, blocked/rejected according to the failed gate.

## Validation commands to run
- Focused:
  - `python -m pytest tests/forex_engine/test_broker_demo_effectiveness_v2.py -q`
- Broker integration regression:
  - `python -m pytest tests/forex_engine/test_broker_integration_effectiveness_v1.py tests/forex_engine/test_oanda_demo_protected_connection_attempt.py tests/forex_engine/test_broker_specific_paper_demo.py tests/forex_engine/test_paper_demo_broker_adapter.py -q`
- Full forex suite:
  - `python -m pytest tests/forex_engine -q --tb=short --durations=50`
