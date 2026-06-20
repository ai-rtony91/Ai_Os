# AIOS FOREX Dashboard Truth Wiring V1 Report

## Packet

- Packet ID: FOREX-DASHBOARD-TRUTH-WIRING-V1
- Branch: feature/forex-dashboard-truth-wiring-v1
- Mode: LOCAL_APPLY_PATCH_ONLY

## Files inspected (as required by packet)

- services/orchestrator/index.js (current stash state reviewed before edits)
- services/orchestrator/forexDashboardTruthStatus.js
- services/orchestrator/forexDemoConnectorProofClosure.js
- apps/dashboard/src/MinimalOperatorDashboard.jsx
- automation/forex_engine/session_replay.py
- automation/forex_engine/evidence_ledger.py
- docs/orchestration/AIOS_FOREX_SESSION_REPLAY.md
- docs/orchestration/AIOS_FOREX_EVIDENCE_LEDGER.md

## Files changed

- services/orchestrator/index.js
- services/orchestrator/forexDashboardTruthStatus.js
- services/orchestrator/forexDemoConnectorProofClosure.js
- apps/dashboard/src/MinimalOperatorDashboard.jsx
- tests/orchestrator/test_forex_dashboard_truth_status.py
- docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md

## Stash files reviewed

- apps/dashboard/src/MinimalOperatorDashboard.jsx
- services/orchestrator/index.js
- services/orchestrator/forexDemoConnectorProofClosure.js

## Dashboard fields wired

- mode
- source
- freshness
- session replay status
- evidence ledger status
- candidates
- rejected candidates
- previews
- risk accepted / rejected
- open trades / closed trades
- realized P/L projection
- balance change
- drawdown
- risk usage
- missing evidence warnings
- blocked reasons
- next safe action

## Orchestrator status wiring

- Read-only GET routes added/kept:
  - `GET /health`
  - `GET /api/forex/session-status`
  - `GET /api/forex/replay-status`
  - `GET /forex/status`
- No POST routes for order submit/close and no execution path.
- All routes return `paper_only` and safety flags in payload.

## Tests added

- `tests/orchestrator/test_forex_dashboard_truth_status.py`
  - display-only labels
  - GET-only routing expectations
  - no broker/live/order/credential strings in source
  - required dashboard truth fields presence assertions
  - source-safety token scan

## Safety boundary

- No broker/API/live execution.
- No credentials or account ids.
- No real orders.
- No network calls beyond local route reads.

## Validators

- Not run by Codex (per user instruction).

## Next human commands

- Wire remaining backend/read-model endpoints to real in-memory evidence/session store when available.
- Verify dashboard still loads after route-level integration in running app.

## Next safe action

- Implement or refine `AIOS-FOREX-NEXT-ACTION-ENGINE` or `FOREX-LONG-RUN-PAPER-SUPERVISOR` packet.
