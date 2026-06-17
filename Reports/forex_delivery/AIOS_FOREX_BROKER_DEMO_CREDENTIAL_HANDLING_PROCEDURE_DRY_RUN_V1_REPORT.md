# AIOS Forex Broker-Demo Credential Handling Procedure DRY_RUN V1 Report

Status: DRY_RUN-only credential-handling procedure. This report does not request credentials, collect credentials, store credentials, load credentials, connect to a broker, activate demo or live endpoints, place orders, place trades, start schedulers, start daemons, deploy, stage, commit, push, open a PR, or merge.

## Packet Context

- Packet ID: `AIOS-FOREX-BROKER-DEMO-CREDENTIAL-HANDLING-PROCEDURE-DRY-RUN-V1`
- Mode executed: `APPLY` for one documentation report only
- Lane: `FOREX_DELIVERY`
- Worktree: `C:\Dev\Ai.Os`
- Current baseline: `e8571a4e docs(forex-delivery): add month-end blocker burndown (#793)`
- Prior readiness checkpoint: PR #791 `feat(forex-delivery): checkpoint governed OANDA demo readiness`
- Live-arming evidence gap checkpoint: PR #792 `feat(forex-delivery): add live arming evidence gap dry run`
- Month-end blocker burn-down checkpoint: PR #793 `docs(forex-delivery): add month-end blocker burndown`

## Source Files Inspected

- `Reports/forex_delivery/AIOS_FOREX_LIVE_ARMING_EVIDENCE_GAP_DRY_RUN_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_FOREX_MONTH_END_BLOCKER_BURNDOWN_V1_REPORT.md`
- `docs/forex/LIVE_ARMING_EVIDENCE_BUNDLE_TEMPLATE.md`
- `docs/forex/SINGLE_LIVE_MICRO_TRADE_EXCEPTION_CHECKLIST_TEMPLATE.md`
- `docs/forex/AIOS_FOREX_DELIVERY_GOVERNED_PACKET.md`
- `docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_AUTH_HANDOFF.md`
- `docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_CONNECTION_GATE.md`
- `docs/trading_lab/AIOS_FOREX_BUILDER_OANDA_DEMO_CONNECTION_PROBE.md`

## Purpose

Define a DRY_RUN-only procedure for future broker-demo credential handling before any OANDA practice/demo broker connection packet or future Single Live Micro-Trade Exception review can be considered.

This procedure authorizes no credential collection, no credential storage, no credential loading, no broker connection, no endpoint activation, no account access, no order route, and no trade route. It only defines the evidence a future Human Owner-approved packet would need to prove that broker-demo auth material and account identifiers remain outside the repository.

## Scope

Scope is limited to OANDA demo or practice credentials and account identifiers as external operator-held materials.

Allowed in repo artifacts:

- Sanitized statements that an external auth reference exists.
- Sanitized statements that auth material is operator-controlled.
- Sanitized statements that account identifiers are not stored, logged, or emitted.
- Abstract labels such as `PRACTICE_DEMO`, `PAPER_DEMO`, `OANDA_PRACTICE_DEMO`, and `PRACTICE_REFERENCE_ONLY`.
- Evidence that scans and checklists passed, without exposing values.

Not allowed in repo artifacts:

- Credential values.
- Account identifiers.
- Live endpoint values.
- Broker payloads.
- Raw request or response bodies.
- Screenshots or exported files containing private broker data.

## Non-Repo Credential Boundary

The repository must not contain:

- API keys.
- Account IDs.
- Access tokens or refresh tokens.
- Passwords.
- Private keys.
- Screenshots of credentials.
- Config files containing secret values.
- Fixture values that resemble real secrets.
- Broker order identifiers.
- Raw broker payloads.
- Live account data.

Any future packet that detects these materials in repo files, generated reports, logs, fixtures, screenshots, chat transcripts, or test data must fail closed and stop.

## Approved Future Storage Concept

Acceptable future storage patterns may be documented, but not implemented by this report:

| Pattern | Allowed evidence | Prohibited evidence |
|---|---|---|
| OS or user secret manager | Name of the secret manager class and a confirmation that the value is external. | Secret value, export, screenshot, command output, or retrieval code. |
| Password manager reference | A human-readable reference label controlled by the operator. | Password manager item contents, copied values, shared links, or screenshots exposing private data. |
| Environment variable reference names only | Reference names such as `OANDA_DEMO_AUTH_REFERENCE_PRESENT` or `OANDA_DEMO_ACCOUNT_REFERENCE_PRESENT`. | Environment variable values, `.env` files, shell history with values, or code that loads values in this repo. |
| External runbook reference | Path or title of an operator-held runbook outside repo artifacts. | Runbook copy containing credential values or account identifiers. |
| Manual operator-held credential entry | Confirmation that the operator enters values at runtime outside repo storage. | Saved credential text, command history with values, logs, or transcripts. |

This report does not create secret-manager integration, environment loading, config files, connector code, broker SDK code, or runtime credential access.

## Credential Intake Checklist

A future Human Owner-approved broker-demo credential intake gate must complete all of these steps before any broker-demo connection packet can be reviewed:

1. Confirm the target account is demo or practice only.
2. Confirm no live funds are reachable by the intended credential path.
3. Confirm no live endpoint label is selected.
4. Confirm credential values are not copied into the repository.
5. Confirm credential values are not copied into chat, reports, logs, tests, fixtures, or screenshots.
6. Confirm account identifiers are not copied into the repository.
7. Confirm account identifiers are not copied into chat, reports, logs, tests, fixtures, or screenshots.
8. Confirm a revocation path exists before any future connection attempt.
9. Confirm a rotation path exists if any exposure is suspected.
10. Confirm the dry-run connection gate still blocks by default.
11. Confirm no order route is enabled.
12. Confirm no account-state request is enabled.
13. Confirm no market-data request is enabled unless a later protected packet explicitly authorizes it.
14. Confirm one-shot stop controls are defined for any future protected connection attempt.
15. Confirm Human Owner approval is recorded for the intake gate only.

## Account ID Handling Proof

Account IDs must be referenced without being stored in repo artifacts.

Required proof format:

- `account_identifier_present: false`
- `account_identifier_repo_storage_confirmed_absent: true`
- `account_identifier_logging_confirmed_absent: true`
- `account_identifier_reference_location: EXTERNAL_OPERATOR_CONTROLLED_RUNTIME_ONLY`
- `account_identifier_value_seen_by_repo: false`

Allowed repo evidence:

- A sanitized boolean that an external account reference exists.
- A sanitized boolean that the repo did not receive or persist the account identifier.
- A no-account-ID scan result that lists files scanned and status only.

Forbidden repo evidence:

- Any account identifier value.
- Partial account identifier values.
- Masked account identifier screenshots.
- Raw broker profile screenshots.
- Raw connector output containing account metadata.

## Endpoint Boundary

Demo and practice endpoint policy:

- Future packets may use abstract labels only, such as `OANDA_PRACTICE_DEMO` or `PRACTICE_REFERENCE_ONLY`.
- A future protected packet must prove the endpoint classification is demo/practice before any connection attempt.
- Endpoint evidence must be sanitized and must not include credential values, account identifiers, or raw request data.

Live endpoint denial policy:

- Live endpoint labels fail closed.
- Live account labels fail closed.
- Ambiguous endpoint labels fail closed.
- Missing endpoint classification fails closed.
- Any attempt to activate a live endpoint is outside this procedure and remains blocked.

This report intentionally does not include real endpoint URLs.

## Revocation And Rotation

If any future credential or account identifier is exposed, the safe procedure is:

1. Stop the packet immediately.
2. Do not retry the broker workflow.
3. Do not copy the exposed value into a report.
4. Record only a sanitized exposure classification.
5. Revoke the exposed credential through the external broker or password-manager control plane.
6. Rotate the credential outside the repo.
7. Run a no-secret and no-account-ID repo scan.
8. Document sanitized evidence that revocation and rotation occurred without including values.
9. Require new Human Owner approval before any later broker-demo connection review.

## Evidence Required Before Any Future Broker-Demo Connection

Before any future broker-demo connection packet can be reviewed, the repo must have sanitized evidence for:

- Completed credential handling checklist.
- No-secret repo scan.
- No-account-ID repo scan.
- External credential storage proof without values.
- External account ID handling proof without values.
- Operator approval record for the credential intake gate.
- Demo/practice account confirmation.
- Live endpoint denial and practice/demo allowlist confirmation.
- Revocation and rotation path confirmation.
- Dry-run connection gate confirmation.
- One-shot stop-control confirmation.
- No-order-route confirmation.
- No-account-state-request confirmation unless separately approved later.
- No-market-data-request confirmation unless separately approved later.

## Credential-Handling Gates Defined

| Gate | Required pass condition | Failure result |
|---|---|---|
| Demo-only account gate | Account classification is demo/practice only. | Fail closed. |
| External credential boundary gate | Auth material remains external operator-controlled runtime-only. | Fail closed. |
| No-repo-secret gate | Repo scan finds no secret values or secret-shaped fixture values. | Fail closed. |
| No-account-ID gate | Repo scan finds no account identifiers or partial account identifiers. | Fail closed. |
| Endpoint classification gate | Endpoint label is demo/practice abstract label only. | Fail closed. |
| Live endpoint denial gate | Live endpoint and live account labels are absent. | Fail closed. |
| Revocation path gate | Revocation and rotation procedures are known before connection review. | Fail closed. |
| Dry-run connection gate | Existing connection gate remains readiness-only and blocked by default. | Fail closed. |
| Human approval gate | Human Owner approval is recorded for the exact intake scope. | Fail closed. |
| No-order/no-trade gate | No order route, trade route, scheduler, daemon, or deployment is enabled. | Fail closed. |

## Hard Blockers After This Procedure Exists

This report defines the procedure, but these P0 blockers still prevent broker-demo connection:

- No completed credential intake checklist evidence exists.
- No no-secret repo scan evidence exists for the future connection packet scope.
- No no-account-ID repo scan evidence exists for the future connection packet scope.
- No external credential storage proof without values exists.
- No external account ID handling proof without values exists.
- No Human Owner approval record exists for an actual broker-demo credential intake gate.
- No protected external runtime connector evidence exists.
- No future packet has been approved to perform a broker-demo connection.

## Safety Confirmation

- Broker connection occurred: `False`
- Credential values requested: `False`
- Credential values read: `False`
- Credential values stored: `False`
- Account IDs requested: `False`
- Account IDs read: `False`
- Account IDs stored: `False`
- Live endpoint activated: `False`
- Demo endpoint activated: `False`
- Order route enabled: `False`
- Order submitted: `False`
- Trade submitted: `False`
- Scheduler started: `False`
- Daemon started: `False`
- Deployment performed: `False`

## Next Packet Recommendation

The next single highest-value packet is:

- Packet ID: `AIOS-FOREX-SINGLE-MICRO-TRADE-EXCEPTION-CHECKLIST-HARDENING-DRY-RUN-V1`
- Mode: `DRY_RUN`
- Lane: `FOREX_DELIVERY`
- Scope: Convert the Single Live Micro-Trade Exception template into a stricter review checklist with evidence references, approval-window rules, one-order-only controls, field-completeness gates, and fail-closed labels.
- Stop point: Stop after checklist-hardening report and no-live-action confirmation.

Reason: the credential boundary is now defined procedurally. The next bottleneck is the approval and evidence checklist that decides whether a future exception package is even reviewable.

## Final Status

- Credential-handling gates defined: `10`
- Remaining P0 blockers: `8`
- Ready for broker-demo connection review: `False`
- Ready for single live micro-trade exception review: `False`
- Live trading enabled: `False`
