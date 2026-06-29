# AIOS Forex Dashboard End User UX Contract V1

The dashboard must help the owner understand state without exposing heavy proof internals by default.

## Required User Sections
- Command Center
- Safety Gate
- Candidate
- Evidence
- Profit Proof
- Broker Boundary
- Reports
- SOS / Owner Wake
- Settings Placeholder
- Secrets Later

## Critical-Only Display Rules
- Show closure status, proof-chain state, protected boundary state, and next safe action first.
- Display owner-review requirement near any demo, live, broker, order, money, or credential reference.
- Display locked false flags as summaries, not as operational controls.
- Never display a profit guarantee or autonomous real-money trading claim.

## Hidden Heavy Data Rules
- Keep raw evidence, long logs, metadata, proof internals, and broker-heavy state behind report links.
- Keep account identifiers, credentials, `.env`, broker API details, and secret paths out of the dashboard.
- Open detailed proof reports only after an intentional user click.
- Use repo-safe report links instead of embedding heavy state in first-view dashboard panels.

## Overwhelm Prevention Rules
- Use one concise state label per window.
- Prefer review-ready, locked, blocked, and next-action labels over dense proof text.
- Collapse non-critical evidence by default.
- Keep SOS / Owner Wake reserved for real owner action, not routine proof detail.

## Protected Boundary
- Broker/API, credential, account identifier, order execution, demo, live, scheduler, daemon, webhook, and background-loop state must display as locked unless a later owner-approved packet changes authority.
- No Bitwarden or secrets lane starts until Forex 110 closure is landed.
