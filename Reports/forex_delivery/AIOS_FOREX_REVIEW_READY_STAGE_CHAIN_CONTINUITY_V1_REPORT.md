# AIOS FOREX REVIEW READY STAGE CHAIN CONTINUITY V1

## objective
Restore legacy journey compatibility while preserving proof-bundle continuity for `c1-eur-buy`.

## compatibility surface restored
- `JOURNEY_INCOMPLETE`, `JOURNEY_REVIEW_READY`, `JOURNEY_REJECTED`, `JOURNEY_FAILED`,
  `JOURNEY_ERROR`, `JOURNEY_READY`, `JOURNEY_PENDING`, `JOURNEY_BLOCKED`, `JOURNEY_REVIEW_BLOCKED`.
- Exported module symbols: `candidate_intake_demo_review_bridge`, `review_chain_orchestrator`,
  `build_review_chain_state`, `run_proof_bundle_to_candidate_bridge` at module level.

## recursion control
- Added module-level `run_proof_bundle_to_candidate_bridge` wrapper in the journey module.
- Added recursion-safe fallback path in proof bundle bridge when nested invocation is detected.

## canonical verdict compatibility
- Reintroduced legacy metric-first verdict behavior in `canonical_demo_review_evidence_bridge.build_review_bundle`
  so existing fixtures retain expected outcomes (`DEMO_REVIEW_READY`, `PAPER_CONTINUE`, `REJECTED`).

## evidence depth expansion
- `run_evidence_depth_expansion` now accepts `write_reports` and preserves default behavior.

## continuity verification
- Added/updated continuity test coverage in
  `tests/forex_engine/test_review_chain_stage_chain_continuity_v1.py`.
- Journey now explicitly generates:
  - `demo_validation_contract`
  - `one_shot_exception_package`
  - `live_review_readiness_certificate`
  - and propagates through orchestrator payload.

## status
- Safety preserved; no live trading, broker, network, or credentials code added.
