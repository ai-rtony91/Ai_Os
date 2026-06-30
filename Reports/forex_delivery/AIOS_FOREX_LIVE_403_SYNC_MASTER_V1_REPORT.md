# Forex Live 403 Sync Master Report V1

- packet_id: PKT-FOREX-LIVE-403-SYNC-MASTER-V1
- mission: synchronize Bitwarden helper repair and OANDA live 403 read-only classifier

## Packet scope synchronized
- Repaired `scripts/security/Start-AiosBitwardenSession.ps1` session bootstrap.
- Added `scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py`.
- Added tests for helper and classifier safety behavior.
- Added owner runbook and classifier docs.
- Added state/report artifacts for classifier and this sync packet.

## Bitwarden helper repair summary
- Existing `Env:BW_SESSION` is now reused and short-circuits `bw unlock`.
- Missing session runs direct `bw unlock --raw` assignment.
- Removed non-necessary capture patterns (`2>&1 | Out-String`, `ConvertFrom-Json`).
- Output remains only:
  - `AIOS_BITWARDEN_SESSION_READY=true/false`
  - `BW_SESSION_PRESENT=true/false`

## Read-only classifier summary
- Added dry-run-first, owner-flag gated classifier.
- Enforces OANDA live-only allowlist endpoint.
- Enforces GET-only behavior and blocks `/orders`.
- Classifies into statuses required for owner diagnostics without retrying orders.
- Produces redacted state and report artifacts.

## Forbidden actions (enforced)
- Any order retry during this packet.
- Any POST/PUT/PATCH/DELETE broker calls.
- Any call to `/orders`.
- scheduler / daemon / webhook startup.
- broker credential or account data persistence to repo artifacts.

## Validation evidence
- `python -m py_compile scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py`
- `python -m pytest tests/forex_engine/test_forex_oanda_live_403_readonly_classifier_v1.py -q`
- `python scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py`
- `powershell -NoProfile -ExecutionPolicy Bypass -Command "Test-Path scripts/security/Start-AiosBitwardenSession.ps1; Test-Path docs/trading_lab/forex/FOREX_OANDA_LIVE_403_READONLY_CLASSIFIER_V1.md; Test-Path docs/trading_lab/forex/FOREX_CONTROLLED_MICRO_LIVE_403_OWNER_RUNBOOK_V1.md"`
- `git diff --check`
- `git status --short --branch`

## Safe next owner commands
- Run the sync report validator set and confirm no live order or money movement occurred.
- Confirm no raw token/account/session values are present in stdout or artifacts.

