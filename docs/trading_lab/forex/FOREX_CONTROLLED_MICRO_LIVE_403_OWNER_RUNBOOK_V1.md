# Forex Controlled Micro-Live 403 Owner Runbook V1

## Safe owner flow

1. Confirm the repository is clean (`git status`).
2. Dot-source the session helper:
   `. .\scripts\security\Start-AiosBitwardenSession.ps1`
3. Run the read-only 403 classifier:
   `python scripts/forex_delivery/run_forex_oanda_live_403_readonly_classifier_v1.py --owner-approved-readonly-live-403-classifier`
4. Review only safe status output (booleans + status + next action).
5. Clear session when complete:
   `. .\scripts\security\Clear-AiosBitwardenSession.ps1`
6. Do not rerun orders until the classification is reviewed by owner.

## Forbidden owner actions

- No raw vault JSON output in chat or notes.
- No token pasted to chat, email, or markdown.
- No account ID pasted.
- No `BW_SESSION` pasted.
- No screenshots containing credentials.
- No direct order retry before diagnosis is reviewed.

