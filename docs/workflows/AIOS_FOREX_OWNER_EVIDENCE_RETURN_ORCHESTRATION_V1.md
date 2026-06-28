# AIOS Forex Owner Evidence Return Orchestration V1

## Purpose
Build a local-only lane for orchestrating owner evidence return before final Forex handoff.

## Scope
- Build and validate owner-return intake from the evidence catalog.
- Validate owner evidence return payloads without network or broker usage.
- Route remaining owner/local gaps and compose the final owner review packet.
- Maintain a checkpoint ledger for each orchestration run.
- Produce deterministic reports and reusable fixtures.

## local-only boundary
- No broker/API calls.
- No credentials.
- No trading commands.
- No money movement.
- No production activation.

## module map
- `automation/forex_engine/forex_owner_evidence_return_intake_v1.py`
- `automation/forex_engine/forex_owner_evidence_return_validator_v1.py`
- `automation/forex_engine/forex_closure_gap_router_v1.py`
- `automation/forex_engine/forex_final_owner_review_packet_composer_v1.py`
- `automation/forex_engine/forex_readiness_checkpoint_ledger_v1.py`
- `automation/forex_engine/forex_owner_evidence_return_orchestrator_v1.py`

## CLI runner map
- `scripts/forex_delivery/run_forex_owner_evidence_return_intake_v1.py`
- `scripts/forex_delivery/run_forex_owner_evidence_return_validator_v1.py`
- `scripts/forex_delivery/run_forex_closure_gap_router_v1.py`
- `scripts/forex_delivery/run_forex_final_owner_review_packet_composer_v1.py`
- `scripts/forex_delivery/run_forex_owner_evidence_return_orchestrator_v1.py`

## Orchestration stages
1. Build deterministic intake from catalog-derived families.
2. Validate return payloads (required sections, sample depth, sensitive pattern rejection).
3. Route owner evidence/local repair/security states.
4. Compose final review packet with safety boundaries and next actions.
5. Record deterministic checkpoint events in a lane ledger.

## Output artifacts
- Intake report
- Validator report
- Closure gap router report
- Final review packet report
- Checkpoint ledger report
- Orchestration report
- Optional checkpoint snapshot

## Test and validation
- `python -m py_compile` for all new/updated lane modules.
- `python -m pytest tests/forex_engine/test_forex_owner_evidence_return_orchestration_v1.py -q`
- run each CLI script with `--write-report --strict`.

## Safety boundaries
- `local_only = True`
- `broker_api = False`
- `env_reads = False`
- `git/github commands = not part of lane`
