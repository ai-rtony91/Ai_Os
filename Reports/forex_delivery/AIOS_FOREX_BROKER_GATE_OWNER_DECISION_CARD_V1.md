# AIOS Forex Broker Gate Owner Decision Card V1

## Purpose
Capture explicit owner approvals required to progress the promotion pipeline after broker/account readiness evidence collection.

## Exact owner decisions required
- Approve/deny recorded that the broker readiness evidence is complete for repo-safe review.
- Approve/deny demo-only operation continuation.
- Approve/deny readiness to proceed to `LIVE_ARMING_REVIEW` checklist.
- Approve/deny whether the account policy and risk controls match owner’s live governance standards.

## Demo-only confirmation
- Demo-only run approved: `__YES__` / `__NO__`
- If NO, provide reason: __________________________________________
- If YES, confirm demo account is the active environment for this promotion phase: `__YES__` / `__NO__`

## Live-arming review confirmation
- Live arming review approved: `__YES__` / `__NO__`
- If NO, provide blocker (endpoint mismatch, permission gap, control policy gap, or operational concern): __________________________________________

## Credential handling warning
- Never paste credentials in chat, logs, or issue/PR text.
- Credentials may be referenced only through secure owner-only operational tooling.
- This packet produced **no** credentials, API keys, or account secrets.

## Broker login / manual verification steps (owner only)
1. Log into broker demo portal and confirm account identity and permissions.
2. Verify instrument access, leverage, margin mode, and risk controls.
3. Confirm account mode and endpoint mapping for demo/live separation.
4. Confirm kill switch and rollback path are visible and immediate.
5. Upload/record confirmation back to this decision card or approved tracker.

## Risk and governance confirmations
- Max loss policy confirmed in platform policy and broker controls: `__YES__` / `__NO__`
- Daily stop policy confirmed: `__YES__` / `__NO__`
- Position sizing policy confirmed: `__YES__` / `__NO__`

## Final yes/no fields
- Proceed to `OWNER_APPROVAL_GATE` now: `__YES__` / `__NO__`
- Proceed to `LIVE_ARMING_REVIEW` now: `__YES__` / `__NO__`
- Permit broker-related readiness evidence to be used for promotion: `__YES__` / `__NO__`

## Final instruction
- Default assumption if any NO field remains unchecked is to stop and block live progression until owner re-validates readiness.
