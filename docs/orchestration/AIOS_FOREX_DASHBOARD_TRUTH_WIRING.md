# AIOS FOREX Dashboard Truth Wiring

## Purpose

This packet establishes display-only dashboard wiring for paper-only forex operations.
Dashboard output is now sourced from a read-only projection chain:

`evidence_ledger -> session_replay -> orchestrator read model -> dashboard display`.

No component creates trade truth, order truth, or execution state.

## Safety boundary

- Paper-only mode only.
- No broker/API/live execution.
- No credentials, no account ids, no secrets.
- No scheduler/daemon/webhook/background automation.
- No new network behavior beyond existing local app route usage patterns.

## Source-of-truth chain

1. `automation/forex_engine/evidence_ledger.py` records canonical events.
2. `automation/forex_engine/session_replay.py` composes deterministic session truth.
3. `services/orchestrator/forexDashboardTruthStatus.js` exposes a safe read model.
4. `apps/dashboard/src/MinimalOperatorDashboard.jsx` renders only the read model.

## Orchestrator status wiring

`services/orchestrator/index.js` now exposes:

- `GET /health`
- `GET /api/forex/session-status`
- `GET /api/forex/replay-status`
- `GET /forex/status` (legacy compatibility route mapped to read-only projection)

No POST or mutating order routes are wired here.

## Dashboard fields

The dashboard now renders the following display-only fields:

- mode
- source
- freshness
- session replay status
- evidence ledger status
- candidates / rejected candidates
- previews created/rejected
- risk accepted/rejected
- open trades, closed trades
- P/L, balance change
- drawdown
- risk usage
- missing evidence warnings
- blocked reasons
- next safe action

If no runtime evidence payload is supplied, the dashboard shows a deterministic
`DISPLAY_ONLY / NO_RUNTIME_EVIDENCE` status rather than inventing trade truth.

## Proof closure

`services/orchestrator/forexDemoConnectorProofClosure.js` is a read-model helper only.
It does not perform side effects and only summarizes what is present in session replay payload.

## Why this does not execute trades

- The orchestrator routes are read-only GET routes.
- Dashboard rendering consumes only already-built read-model data.
- All payloads are explicitly labeled `paper_only`.
- Safety payload requires: no broker, no live trading, no credentials, no real orders, no network access.

## Next safe packet

Recommended next packet: `AIOS-FOREX-NEXT-ACTION-ENGINE` or
`FOREX-LONG-RUN-PAPER-SUPERVISOR` depending on roadmap state.
