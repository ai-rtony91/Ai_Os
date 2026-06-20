# AIOS FOREX Next Action Engine V1 Report

## Packet

- Packet ID: AIOS-FOREX-NEXT-ACTION-ENGINE-V1
- Branch: feature/forex-next-action-engine-v1

## Files inspected

- automation/forex_engine/session_replay.py
- automation/forex_engine/evidence_ledger.py
- automation/forex_engine/multi_trade_queue.py
- automation/forex_engine/strategy_candidates.py
- automation/forex_engine/market_data_normalizer.py
- automation/forex_engine/order_preview.py
- automation/forex_engine/risk_governor.py
- automation/forex_engine/position_sizing.py
- automation/forex_engine/paper_fill_simulator.py
- automation/forex_engine/trade_lifecycle_manager.py
- automation/forex_engine/balance_compounding.py
- docs/orchestration/AIOS_FOREX_SESSION_REPLAY.md (if present)
- docs/orchestration/AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md (if present)

## Files changed

- automation/forex_engine/next_action_engine.py
- tests/forex_engine/test_next_action_engine.py
- docs/orchestration/AIOS_FOREX_NEXT_ACTION_ENGINE.md

## Recommendation rules added

- Protected-action detection and `requires_approval` decision for live/broker/credential/secret/API/webhook terms.
- Missing spine prerequisite gating to evidence ledger / session replay / dashboard truth wiring.
- Long-run paper supervisor recommendation when long-run paper packet is missing or evidence is immature.
- Demo connector readonly → order mapping → reconciliation ladder when eligible.
- Demo promotion packet when reconciliation complete but readiness proof missing.
- Self-improvement recommendation after long-run + demo prerequisites are complete.

## Protected-action rules

- Returns `protected_action_detected=True`, `approval_required=True`, `no_live_action_stop=True` for blocked terms.
- Default next-safe action uses explicit approval-focused wording.

## Tests added

- `tests/forex_engine/test_next_action_engine.py`
- Covers import, default recommendation, protected action behavior, missing spine, mature/immature paper evidence branching, demo ladder branching, deterministic blocker order, result shape and safety dict, source scan.

## Safety boundary

- No execution, no live trading, no broker/API calls, no credentials.
- Only returns decision guidance.

## Validators

- Not run by Codex.

## Next human commands

- Run focused tests for `tests/forex_engine/test_next_action_engine.py` in local environment.

## Next safe action

- Continue with subsequent paper-to-demo hardening packet sequencing after validating this engine output in review.
