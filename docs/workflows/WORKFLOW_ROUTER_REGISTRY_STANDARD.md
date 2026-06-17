# AI_OS Workflow Router Registry Standard

Status: canonical workflow

## Purpose

This document defines the AI_OS standard for workflow routers and workflow registries.

A workflow router maps a registered workflow name to approved DRY_RUN helper checks. A workflow registry defines which workflow names exist, what they may do, which helpers they may preview, what risks they carry, and what approval gates apply.

This standard must be in place before dashboard buttons, launchers, helpers, or automation routes are connected to workflow execution.

## Authority Boundary

Router and registry output is evidence. It is not approval.

A router, registry, launcher, dashboard button, helper list, terminal output, log, or status panel must not approve APPLY, edit files, stage files, commit, push, merge, deploy, launch apps, open browsers, change settings, create scheduled tasks, handle credentials, touch secrets, connect brokers, place trades, or enable live trading.

Only the user can approve APPLY or any protected action.

## Single Live Micro-Trade Exception Router Boundary

For any future Single Live Micro-Trade Exception, router, registry, queue, launcher, dashboard, helper, terminal, report, and telemetry output remains evidence or projection only.

Routers and registries cannot route around Human Owner approval, transform evidence into execution authority, approve or arm the exception, release credential handles, extend approval, retry after a terminal result, re-enter autonomously, or start hidden scheduler, daemon, or background execution paths.

Approval must be explicit, Human Owner-bound, one-shot, non-transferable, expiring, packet-bound, and compliant with `RISK_POLICY.md`. Generic fields such as `approval_status`, `approved_by_human`, `APPROVED`, or `approval_granted` do not satisfy the live micro-trade exception by themselves.

Workflow artifacts must not contain credentials, broker order IDs, account identifiers, live payloads, private account data, or secret values.

## Router Scope

A workflow router may:

- accept a workflow name.
- confirm the active repo root.
- check that the workflow name is registered.
- print the selected workflow.
- print allowed actions and blocked actions.
- list helper scripts mapped to the workflow.
- check whether mapped helpers are present or missing.
- call approved helper scripts only when the helper path contains `.DRY_RUN.`.
- produce a PASS, WARN, or FAIL result.
- recommend one next safe action.

A workflow router must remain DRY_RUN-first and evidence-only.

## Registry Scope

A workflow registry documents approved workflow names, operator-facing labels, helper mappings, risk levels, execution mode, write behavior, approval requirements, and blocked actions.

The registry does not approve work. It defines the controlled menu of workflows that a router, dashboard, launcher, or helper chain may reference.

Any workflow not listed in the active registry is unregistered and must fail safely.

## Required Workflow Registry Fields

Each registered workflow should define:

- workflow name.
- operator phrase or display label.
- purpose.
- risk level.
- execution mode.
- whether it writes files.
- whether it requires human review.
- whether it requires separate git checkpoint approval.
- allowed actions.
- blocked actions.
- helper mapping.
- expected router output.
- validation or review expectation.
- next safe action.

Unknown values must be marked `UNKNOWN`. Do not invent approval, helper paths, write behavior, or risk status.

## Workflow Risk Levels

Workflow risk levels should use these values:

- `LOW`: read-only DRY_RUN inspection, preview, or console output.
- `MEDIUM`: approved file creation or approved report writing without git staging, commit, push, merge, deployment, broker execution, live trading, secret handling, app launch, browser open, startup changes, or settings changes.
- `HIGH`: any workflow that proposes protected edits, launcher behavior, settings changes, scheduled tasks, credential handling, broker/trading contact, deployment, destructive operations, or other protected actions.

New router-connected workflows should default to `LOW` until a separate approved AI_OS standard explicitly allows a higher risk level.

## Approved Helper Mapping Rules

Helper mappings must be explicit. A workflow may not expand from a vague label into arbitrary scripts.

Each helper mapping should identify:

- helper path.
- helper purpose.
- expected mode.
- whether the helper is required or optional.
- expected output.
- blocked actions.

Mapped helpers must be reviewed as part of workflow registration. A router must not discover and run unrelated scripts by folder scan, wildcard expansion, naming guess, or dashboard label.

## DRY_RUN Helper Requirement

Router-called helpers must be DRY_RUN helpers unless a future approved canonical AI_OS document explicitly changes the boundary.

The helper path must contain `.DRY_RUN.` or the router must block the helper with a FAIL result.

A non-DRY_RUN helper path must not be run from the router by default. It requires separate human approval and a future approved routing standard before it can become router-connected behavior.

## Dashboard And Launcher Mapping Rules

Dashboard buttons, launcher actions, command palettes, terminal shortcuts, and other operator-facing controls must map to registered workflow names, not directly to raw scripts.

A dashboard or launcher should show:

- workflow name.
- purpose or display label.
- risk level.
- execution mode.
- approval requirement.
- allowed actions.
- blocked actions.
- expected result.

Dashboard and launcher output is a projection of registered workflow evidence. It must not become independent authority or approval.

## Router Output Requirements

Router output should include:

- task name or router command.
- router mode.
- repo root.
- selected workflow.
- workflow risk level.
- allowed actions.
- blocked actions.
- approval requirement.
- helper scripts that would be used.
- helper scripts found.
- helper scripts missing.
- PASS, WARN, or FAIL result.
- next safe action.

If a value cannot be verified, mark it `UNKNOWN` and use WARN or FAIL as appropriate.

## PASS/WARN/FAIL Result Semantics

Router results must use these meanings:

- `PASS`: the workflow name is registered, expected DRY_RUN helpers are present, and no unsafe action was attempted.
- `WARN`: the workflow is recognized, but review is needed before any follow-up action. Examples include a missing optional helper, dirty working tree, incomplete evidence, or other non-blocking issue.
- `FAIL`: the workflow name is unknown, the repo root cannot be verified, a required helper is missing, a non-DRY_RUN helper is mapped, a protected action appears, or another blocking condition is detected.

A PASS result does not approve APPLY, report writing, git staging, commit, push, merge, deployment, launcher action, browser open, broker action, trading action, credential handling, or security setting changes.

## Unknown Workflow Fail-Safe Behavior

Unknown workflow names must fail safely.

When a workflow name is unknown, the router should:

1. Stop.
2. Report FAIL.
3. Print or reference the valid workflow list when available.
4. Avoid running helpers.
5. Recommend one next safe action.

The operator or worker must not work around an unknown workflow by running guessed scripts.

## Missing Helper Behavior

Missing helper behavior depends on whether the helper is required or optional.

- A missing required helper produces FAIL.
- A missing optional helper produces WARN.
- A missing helper must never cause the router to substitute an unrelated script.
- A missing helper must not cause APPLY, report writing, git actions, or protected actions.

The router should report the missing path, workflow name, and next safe action.

## Blocked Workflow Types

The following workflow types are blocked from router connection unless a future approved canonical AI_OS document explicitly changes the boundary:

- broker order placement.
- live trading.
- OANDA execution.
- real orders.
- real webhooks.
- credential, secret, token, private key, or recovery key handling.
- app launch.
- browser opening.
- startup setting changes.
- scheduled task creation.
- registry, firewall, VPN, BIOS/UEFI, BitLocker, or browser policy changes.
- file deletion, movement, rename, overwrite, reset, or cleanup.
- git add, git commit, git push, merge, release, or deployment.
- uncontrolled background automation.

Blocked workflow types must not be registered as ordinary LOW-risk router workflows.

## Approval Gate Requirements

Human approval is required before:

- APPLY.
- file creation or report writing.
- protected file edits.
- git add, commit, push, merge, release, or deployment.
- app launch or browser opening.
- startup, scheduled task, or settings changes.
- credential, secret, token, private key, or recovery key handling.
- broker, trading, OANDA, webhook, real order, or live execution work.
- changing the workflow registry or router behavior.

Approval must identify the exact mode, files or paths, intended action, expected validation, and stop condition.

## Relationship To Worker Lifecycle Standard

This standard supports `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`.

Router output can help determine whether a task is ready for runner preview, review, or a later approval request. Router output does not move work into APPLY by itself.

If router output conflicts with lifecycle state, the conflict must be marked `MISMATCH` and resolved before continuing.

## Relationship To Worker Output Interface Standard

This standard supports `docs/workflows/WORKER_OUTPUT_INTERFACE_STANDARD.md`.

Router, dashboard, launcher, terminal, and log output must present authority, mode, approval state, findings, and next safe action clearly. Output must not create independent authority or hidden approval.

## Relationship To Validator Execution Standard

This standard supports `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`.

Validators may inspect router output, workflow registry fields, helper mappings, missing helpers, blocked actions, and result semantics. Validator output is evidence and does not approve router execution, APPLY, commit, push, merge, deployment, broker work, live trading, or secret handling.

## Relationship To Approval Model

This standard supports `docs/security/approval-model.md`.

All router-connected activity defaults to DRY_RUN. APPLY and protected actions require explicit human approval. The approval model overrides any router, registry, dashboard, launcher, terminal, or helper output that implies permission.

## Future Workflow Registration Rules

Future workflow registration must start with a DRY_RUN proposal.

A proposed workflow must define:

- workflow name.
- purpose.
- risk level.
- execution mode.
- helper mapping.
- allowed actions.
- blocked actions.
- write behavior.
- approval gates.
- expected output.
- validation or review requirement.
- next safe action.

A future workflow must not be connected to a dashboard, launcher, helper chain, or automation route until its registry entry is reviewed against this standard.

## Stop Conditions

Stop and report when:

- repo root cannot be verified.
- branch cannot be verified when branch context matters.
- workflow name is unknown.
- registry entry is missing required fields.
- helper mapping is missing, unclear, or unverifiable.
- required helper is missing.
- mapped helper path does not contain `.DRY_RUN.`.
- helper substitution is attempted.
- router output implies approval.
- dashboard or launcher maps directly to a raw script instead of a workflow name.
- a blocked workflow type appears.
- protected action lacks approval.
- output conflicts with active authority.
- next safe action is missing.

## Next Safe Action Requirement

Every router result, registry review, dashboard route preview, launcher route preview, and workflow registration proposal must end with one next safe action.

The next safe action should be one of:

- an exact DRY_RUN command.
- an exact validation command.
- an exact review instruction.
- an exact APPLY prompt after approval.
- an exact registry update prompt after approval.
- a checkpoint instruction.
- a stop point.

The next safe action must not bypass approval, validation, protected boundaries, or active authority.
