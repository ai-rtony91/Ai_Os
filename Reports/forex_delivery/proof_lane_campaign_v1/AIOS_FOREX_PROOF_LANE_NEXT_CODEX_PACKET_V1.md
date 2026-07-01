CODEX-ONLY PROMPT
AI_OS EXECUTION TOKEN
AI_OS BOOTSTRAP REQUIRED

Identity marker: EAST_OCC_01
Supervisor identity: Anthony Meza
Packet ID: AIOS_FOREX_PROOF_LANE_RECEIPT_SCHEMA_DRY_RUN_VALIDATOR_V1
Mode: APPLY
Zone: Reports/forex_delivery/proof_lane_campaign_v1
Worker identity: Codex East
Lane: Forex Proof Lane
Worktree: C:\Dev\Ai.Os
Branch: feature/forex-proof-lane-parallel-campaign-v1

Mission:
Create a non-secret Forex proof-lane receipt schema, a sanitized fake receipt fixture, a dry-run validator, and tests. Keep the lane local-only and paper/demo only.

Allowed paths:
- automation/forex_engine/
- tests/forex_engine/
- Reports/forex_delivery/proof_lane_campaign_v1/

Forbidden paths:
- .env
- credentials/
- secrets/
- broker/
- live trading paths
- runtime service paths
- scheduler paths
- notification paths
- dashboard mutation paths outside the proof-lane output root
- docs/governance/

Approval authority:
Current-session Human Owner approval is required for APPLY changes and exact-file staging. No broker approval is implied or granted.

Validator chain:
- `python -m compileall -q -j 0 automation tests scripts`
- `python -m pytest tests/forex_engine/ -q`
- `python -m pytest tests/security/test_aios_bitwarden_local_credential_broker_v1.py -q`
- `git diff --check`

Stop point:
Stop after the schema, fixture, validator, and tests are complete. Do not call brokers, read credentials, touch `.env`, send notifications, place orders, or claim profit.

Preflight:
- Confirm `C:\Dev\Ai.Os` is the active worktree.
- Confirm the branch is `feature/forex-proof-lane-parallel-campaign-v1`.
- Confirm the worktree is clean before writing.
- Read the current receipt, risk, and dashboard evidence before editing.

Final report format:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS: COMPLETE, NO COMMIT, NO PUSH
