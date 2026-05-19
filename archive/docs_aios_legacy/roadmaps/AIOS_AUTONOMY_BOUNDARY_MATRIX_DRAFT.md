# AI_OS Autonomy Boundary Matrix Draft

Status: DRAFT
Mode: DRY_RUN-derived planning artifact

## Purpose

This matrix defines what AI_OS may eventually automate, what always requires human approval, and what must never be automated. It reflects the current governance-first, DRY_RUN/APPLY operating model.

## Boundary Classes

- NEVER AUTOMATE: permanently blocked or not allowed without a future governance replacement approved by the operator.
- ALWAYS HUMAN APPROVAL: allowed only after explicit human approval and reporting.
- SEMI-AUTONOMOUS CANDIDATE: may eventually run as assisted automation after validators, rollback, audit, and stop conditions exist.
- READ-ONLY SAFE: can be automated in DRY_RUN/read-only form if it does not collect sensitive data or mutate state.

## Matrix

| Area | Classification | Reason | Required Controls |
| --- | --- | --- | --- |
| Broker order placement | NEVER AUTOMATE | Financial execution risk | Human trading approval, broker sandbox, risk controls; still blocked now |
| Live trading enablement | NEVER AUTOMATE | Explicit project safety boundary | Separate governance phase required |
| Credential handling | NEVER AUTOMATE | Secrets exposure risk | Use approved secret manager later; no repo storage |
| API key/token storage | NEVER AUTOMATE | Credential compromise risk | Key Vault or equivalent only after approval |
| Windows registry edits | NEVER AUTOMATE | System-level risk | Human operator only |
| BitLocker/BIOS/UEFI/firewall/VPN/browser policy changes | NEVER AUTOMATE | Device/security risk | Human operator only |
| Delete/move/rename files | ALWAYS HUMAN APPROVAL | Repo integrity risk and current rules block it | DRY_RUN, explicit list, backup, approval |
| Protected root file edits | ALWAYS HUMAN APPROVAL | Governance source-of-truth risk | Backup, scoped edit, final report |
| Git commit | ALWAYS HUMAN APPROVAL | Checkpoint integrity | Clean status, diff review, explicit message |
| Git push/merge/reset/clean | ALWAYS HUMAN APPROVAL | Remote/destructive risk | Explicit approval, recovery plan |
| Deployment | ALWAYS HUMAN APPROVAL | Public/runtime risk | CI/CD, rollback, observability, auth |
| Azure resource creation | ALWAYS HUMAN APPROVAL | Cost/security/runtime risk | Deployment plan and rollback |
| Auth or account connection | ALWAYS HUMAN APPROVAL | Account/security risk | Manual operator flow only |
| Report writer APPLY | ALWAYS HUMAN APPROVAL | File mutation risk | Allowlist, dry-run, backup rules |
| Telemetry persistence | ALWAYS HUMAN APPROVAL | Privacy and retention risk | Schema, retention, exclusion rules |
| Dashboard fixture display | SEMI-AUTONOMOUS CANDIDATE | Low risk if local fixture-only | Fixture validation and no live calls |
| Repo file inventory | READ-ONLY SAFE | Non-mutating evidence collection | Avoid secrets/private paths |
| Git status check | READ-ONLY SAFE | Non-mutating repo state | Report branch and cleanliness |
| Schema validation | READ-ONLY SAFE | Non-mutating validation | Fixture-only data |
| Missing-file proposal | SEMI-AUTONOMOUS CANDIDATE | Proposal-only if no APPLY | Human approval before creation |
| Checkpoint draft generation | SEMI-AUTONOMOUS CANDIDATE | Helpful but can misstate state | Evidence links and unknown labels |
| Daily report draft generation | SEMI-AUTONOMOUS CANDIDATE | Helpful but must avoid false claims | Evidence, mismatch rules |
| Source-of-truth index refresh | SEMI-AUTONOMOUS CANDIDATE | Useful if append-only or reviewed | DRY_RUN, no overwrite |
| Dashboard stale-data detection | READ-ONLY SAFE | Display safety improvement | No external calls |
| Tool install detection | READ-ONLY SAFE | Status only | No install, no account connection |
| Agent delegation planning | SEMI-AUTONOMOUS CANDIDATE | Useful with bounded tasks | Task ID, file ownership, approval flag |
| Multi-agent APPLY | ALWAYS HUMAN APPROVAL | Conflict and mutation risk | Disjoint write scopes, approval |
| Backtest ingestion | ALWAYS HUMAN APPROVAL | Data quality and trading implication | Fixture/source validation |
| Paper-trade ledger writing | ALWAYS HUMAN APPROVAL | Trading record integrity | Approved paper environment |
| AI signal review | SEMI-AUTONOMOUS CANDIDATE | Review-only, no execution | Deterministic validator first |
| AI trade blocking | SEMI-AUTONOMOUS CANDIDATE | Safety-positive if deterministic | Human-approved rules |
| AI trade approval | NEVER AUTOMATE | AI must not authorize trades | Human operator only |

## Required Autonomy Stop Conditions

Any automated or semi-autonomous workflow must stop if it detects:

- Secrets, credentials, keys, tokens, recovery keys, or broker account material.
- Broker order placement, live trading, webhook firing, or strategy activation.
- Protected file edits not explicitly approved.
- Delete, move, rename, overwrite, reset, clean, push, merge, or deployment.
- MISMATCH between repo evidence and prior notes.
- INVALID DATA that cannot be verified.
- Unknown current branch or dirty worktree when mutation is requested.
- File Explorer, screenshot, terminal, or repo evidence conflict.

## Approval Packet Requirements

Every future APPLY packet must include:

- Task.
- Phase, stage, workload pack, task ID.
- Files inspected.
- Files proposed for creation.
- Files proposed for modification.
- Protected action flag.
- Risk check.
- DRY_RUN result.
- Unknowns.
- Stop conditions.
- Validation rules.
- Future commit recommendation.

## Semi-Autonomous Promotion Requirements

A function can move from DRY_RUN-only to semi-autonomous only when:

- It is non-destructive.
- It has deterministic validators.
- It has bounded file paths.
- It has no secret, broker, deployment, or account path.
- It logs evidence.
- It labels UNKNOWN and MISMATCH correctly.
- It can be reverted or ignored safely.
- Human approval remains required before mutation.

## Current Recommendation

Keep AI_OS in read-only and human-approved APPLY mode. Promote only fixture validation, schema checks, repo health scans, dashboard stale-data checks, and report draft generation toward semi-autonomous behavior after additional validation.
