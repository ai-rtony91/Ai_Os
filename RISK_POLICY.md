# AI_OS Risk Policy

## Purpose

This file is the canonical root safety and execution authority for AI_OS V2.

It defines the default safety posture, blocked execution boundaries, emergency-stop conditions, approval-gate doctrine, validation expectations, and fail-closed behavior for AI_OS development and operation.

This file does not replace `AGENTS.md` as agent-behavior authority and does not redefine workflow topology, launcher topology, or worker-lane structure.

## Canonical Authority Status

`RISK_POLICY.md` is root authority for AI_OS safety and execution boundaries.

Supporting security, audit, placement, and ownership documents may add detail, but they must not weaken this policy. If a supporting document conflicts with this file, the stricter safety rule applies until the conflict is resolved by explicit human approval.

## Default Risk Posture

AI_OS defaults to inspection before execution.

- DRY_RUN is the default mode.
- APPLY requires explicit human approval.
- Unknown risk is blocked until clarified.
- Authority mismatch is blocked until resolved.
- Branch, path, or repo identity mismatch is blocked until verified.
- Inspection must not automatically escalate into execution.
- Automation must not silently fall back to a less safe behavior.

## Absolute Execution Blocks

The following are blocked unless a future explicit, reviewed policy changes the project boundary:

- live trading.
- broker execution.
- OANDA or live order execution.
- real webhook execution.
- real orders.
- broker credentials, account identifiers, API keys, tokens, passwords, private keys, recovery keys, or other secrets.
- destructive actions without explicit approval, including delete, move, rename, overwrite, reset, clean, and force push.
- runtime mutation without validation.
- hidden automation, startup tasks, scheduled tasks, or background execution paths.
- validation bypass.
- automatic escalation from a report, dashboard, terminal, queue, packet, or launcher into execution authority.

## Trading Lab Boundary

Trading Lab is paper-only.

Allowed when explicitly scoped:

- paper simulation.
- backtesting.
- latency tracking.
- signal validation.
- paper route previews.
- local-only telemetry that does not collect secrets or live execution data.

Blocked:

- live broker connections.
- live order routing.
- real order placement.
- OANDA API clients or live broker adapters.
- broker credentials or live account data.
- LLMs directly in live order execution paths.

## Secrets / Credentials / Private Data

Secrets, credentials, and private data must not be committed, persisted, exposed in generated reports, or embedded in scripts.

Sensitive data includes:

- API keys, tokens, passwords, private keys, SSH keys, OAuth secrets, recovery keys, and `.env` contents.
- broker account identifiers, live account data, live market execution data, order details, or live order path data.
- browser profile paths, credential stores, private user data, and screenshots containing private data.

Any suspected sensitive data must fail closed as `BLOCKED` until human review and verified evidence clarify the path forward.

## Approval Gate Doctrine

Explicit human approval is required before:

- APPLY.
- protected root file edits.
- execution-behavior changes.
- runtime, dashboard, telemetry, trading, broker, webhook, deployment, or CI/security workflow changes.
- modifying secret-handling behavior.
- destructive actions.
- staging, committing, pushing, merging, releasing, or deploying.

Approval must identify the intended files, intended change, validation expectation, and stop point. Broad or ambiguous approval does not authorize unrelated execution.

## Emergency Stop Conditions

Stop immediately and report when any of the following are detected:

- suspected secret, credential, private data, broker data, or live execution data.
- live trading, broker execution, OANDA, real webhook, or real order path.
- unapproved runtime mutation.
- unapproved destructive action.
- protected file edit without explicit approval.
- branch, path, repo identity, or authority mismatch.
- MISMATCH evidence, INVALID DATA, or unknown critical facts.
- failed validation.
- silent fallback, hidden automation, scheduled task, startup task, or unexpected background execution path.

Emergency stop means no further execution, no launcher continuation, no worker continuation, no commit, and no push until the operator approves the next safe step.

## Validation Before Mutation

Validation is mandatory before mutation.

- Inspect current authority and target files before editing.
- Run the scoped validators requested by the task.
- Run `git diff --check` when files change.
- Validate JSON parses when JSON files change.
- Validate PowerShell parses when PowerShell files change.
- Do not mutate runtime state, trading state, dashboard state, telemetry state, or worker state without explicit scope and validation.

Passing validation does not approve commit, push, merge, deployment, or execution.

## Fail-Closed Rules

AI_OS must fail closed when safety, authority, or execution state is uncertain.

Fail closed on:

- unknown risk.
- authority mismatch.
- branch, path, repo, or lane mismatch.
- missing approval.
- missing validation.
- suspected sensitive data.
- hidden execution behavior.
- stale or conflicting instructions.
- unsafe fallback behavior.

The safe result is `BLOCKED`, `REVIEW`, or `INVALID DATA` until the operator provides a clear next action.

## Audit And Evidence Expectations

Security-relevant actions should leave enough evidence to reconstruct what happened.

Evidence should distinguish:

- DRY_RUN from APPLY.
- requested action from approved action.
- validation command from validation result.
- rejected or blocked action from completed action.
- trading/broker blocked action from normal workflow output.

Audit evidence must not contain secrets, broker credentials, private data, or live execution data.

## Supporting Authority References

These documents support this root policy with implementation detail:

- `AGENTS.md` - agent operating behavior and protected-action rules.
- `README.md` - V2 front-door context, project boundary, and paper-only Trading Lab statement.
- `docs/security/approval-model.md` - approval workflow details.
- `docs/security/threat-model.md` - threat categories and required security controls.
- `docs/security/secret-prevention.md` - secret-handling procedures.
- `docs/security/audit-logging.md` - audit event and evidence expectations.
- `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md` - canonical privacy and credential exclusion checklist.
- `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` - placement and blocked implementation boundaries.
- `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` - folder ownership and risk boundaries.

## Non-Authority / Draft References

Draft, legacy, generated, archived, or planning documents are evidence only unless explicitly promoted by a future approved V2 workflow.

Draft risk-control and governance matrices may inform future updates, but they do not authorize execution, weaken this policy, activate live trading, approve broker connectivity, approve secrets handling, approve runtime mutation, or replace root authority.

## Last Verified

Updated on 2026-05-21 for AI_OS V2 on branch `v2/aios`.
