# AI_OS Overnight Supervisor Workflow

Status: canonical workflow

## Purpose

The AI_OS Overnight Supervisor defines the first governed read-only supervisor model for overnight and later full-time supervised orchestration.

It reduces routine operator workload by inspecting state, classifying risk, ranking next safe actions, drafting packet proposals, and preparing a morning brief. It does not execute protected actions.

Overnight Supervisor is not autonomous APPLY authority.

Overnight Supervisor is report-first supervised autonomy. It may connect work packet evidence, worker routing evidence, validator-chain evidence, approval inbox evidence, commit-package candidate evidence, and overnight reporting into one read-only plan. It must stop at the report boundary until the Human Owner approves a separate exact APPLY, commit, push, merge, or worker-launch packet.

## Scope

This workflow applies to future overnight supervisor reports, planner scripts, schemas, morning brief output, escalation packets, and semi-autonomous orchestration proposals.

It governs read-only intelligence for:

- repo state.
- packet queues.
- packet intake and packet classification.
- worker state.
- worker resolution and lane routing evidence.
- approval state.
- validator-chain configuration, execution recommendations, and validator result evidence.
- stale packet detection.
- blocker detection.
- approval escalation requirements.
- commit package candidate preparation.
- next safe action ranking.
- packet draft previews.
- morning brief generation.

## Read-Only Intelligence Definition

Read-only intelligence means AI_OS may inspect evidence, summarize state, classify risk, recommend next safe actions, and draft future work packets without changing repository, queue, worker, approval, runtime, Git, GitHub, broker, credential, or trading state.

Read-only intelligence may produce recommendations. It must not convert recommendations into execution.

## Allowed Inputs

The Overnight Supervisor may inspect:

- `git status --short --branch` output.
- approved repo metadata and read-only Git evidence.
- work packet records and packet state evidence.
- approval inbox summaries.
- worker registries, worker profiles, worker inbox summaries, and worker lane status.
- validator chain configuration and validator recommendation output.
- queue health, stale packet, blocker, clean-state, and runtime health DRY_RUN evidence.
- commit package recommendations.
- safe session resume evidence.
- orchestration spine/read-model evidence.
- schema and contract files under approved orchestration paths.

If evidence is missing, stale, conflicting, or unverifiable, the supervisor must mark it `UNKNOWN`, `STALE`, `MISMATCH`, or `BLOCKED` instead of guessing.

## Allowed Outputs

The Overnight Supervisor may output:

- supervisor status.
- packet intake summary.
- packet classification summary.
- worker resolution summary.
- repo health summary.
- stale packet summary.
- worker and lane review summary.
- approval state summary.
- validator-chain recommendation and result summary.
- escalation item list.
- commit package candidate summary.
- ranked next safe actions.
- packet draft previews.
- morning brief preview.
- blocker summary.
- stop condition.

Outputs are evidence and recommendations only. They are not approval, mutation authority, or execution authority.

## Blocked Actions

The Overnight Supervisor must not:

- APPLY changes.
- write files.
- perform blind APPLY.
- perform blind commit.
- move packet state.
- create, update, or clear approvals.
- create, update, or clear queues.
- create, update, or clear locks.
- launch workers.
- launch windows or terminals.
- start loops.
- start daemons.
- schedule tasks.
- create startup persistence.
- open pull requests.
- merge pull requests.
- stage files.
- commit.
- push.
- merge.
- edit protected roots without explicit approved APPLY authority.
- delete files.
- move files.
- rename files.
- run broker routes.
- run live trading routes.
- handle secrets or credentials.
- make uncontrolled autonomous decisions.

## Escalation Triggers

The Overnight Supervisor must escalate to Anthony Meza when any of these appear:

- validator failure.
- protected path touched or proposed.
- merge conflict.
- unclear authority.
- stale runtime or session evidence.
- repo corruption risk.
- unknown file ownership.
- worker or lane collision.
- approval mismatch.
- confidence collapse.
- unsafe automation attempt.
- live trading, broker, webhook, OANDA, secret, or credential scope.
- read model conflicts with current repo state.
- next safe action cannot be ranked safely.

Escalation output must include the reason, evidence, affected scope, recommended human decision, and the next safe recovery step.

## Canonical Packet Flow

The Overnight Supervisor must describe the packet flow in this order:

1. Packet intake: read available work packet evidence and classify each packet as `READY_FOR_REVIEW`, `VALIDATOR_REQUIRED`, `APPROVAL_REQUIRED`, `COMMIT_PACKAGE_CANDIDATE`, `BLOCKED`, `STALE`, or `UNKNOWN`.
2. Worker resolution: identify the named worker identity, lane, zone, and allowed path boundary from packet evidence. Missing or conflicting worker identity must become `BLOCKED`.
3. Validator execution planning: summarize the required validator chain and any available validator result evidence. The supervisor may recommend validators, but must not run a validator automatically unless a separate approved DRY_RUN validator packet authorizes it.
4. Approval escalation: mark any packet requiring APPLY, protected path work, worker launch, commit, push, merge, packet movement, or authority change as `approval_required = true`.
5. Commit package preparation: identify exact-file commit package candidates only from reviewed evidence. This is planning only and must not stage files, create commits, push branches, open PRs, or merge.
6. Overnight reporting: produce the morning brief, escalation list, blocked action list, and next safe action.

If any step lacks evidence, the supervisor must report `UNKNOWN` or `BLOCKED` and stop at report output.

## Stop Conditions

The Overnight Supervisor must stop when:

- required authority chain is missing.
- packet identity, lane, worker identity, allowed paths, forbidden paths, approval authority, validator chain, or stop point is missing for executable work.
- execution mode is missing or inconsistent.
- approval state is missing for protected work.
- evidence is stale, invalid, or contradictory.
- requested action would mutate state.
- requested action would launch workers, loops, daemons, terminals, scheduled tasks, or startup tasks.
- requested action would stage, commit, push, merge, delete, move, or rename files.
- protected trading, broker, secret, credential, or live execution scope appears.
- validator chain is missing or fails.
- output would imply APPLY without visible human approval.
- output would imply commit, push, merge, or protected-root edits without explicit human approval and an exact-file package.

## Morning Brief Responsibilities

The morning brief should summarize:

- current repo state.
- known changed files.
- stale packets.
- blocked packets.
- approval items.
- validator recommendations.
- worker or lane conflicts.
- escalation items.
- ranked next safe actions.
- packet drafts ready for review.
- stop conditions encountered overnight.

The morning brief must be report-only unless a separate approved APPLY pack explicitly changes behavior.

The morning brief may name commit package candidates, validator candidates, and approval-needed packets. These are planning signals only. They are not permission to APPLY, stage, commit, push, merge, or edit protected roots.

Compact morning brief output should stay short and operator-facing. It should show:

- `STATUS`.
- `WHAT CHANGED`.
- `BLOCKED BY`.
- `NEEDS ANTHONY APPROVAL`.
- `SAFE NEXT ACTION`.
- `SAFE TO IGNORE`.
- `TODAY FOCUS`.

The compact brief may recommend a next step. It must not approve, execute, write files, move packet state, launch workers, stage, commit, push, merge, schedule work, or touch protected trading, broker, secret, credential, or live execution scope.

## Packet Drafting Rules

Packet drafts must remain previews.

Each packet draft should include:

- objective.
- mode.
- lane.
- allowed paths.
- forbidden paths.
- validator chain.
- approval requirement.
- blocked actions.
- stop point.
- next safe action.

Packet drafts must not be moved into an active queue, assigned to a worker, or treated as approved work without separate human approval.

## Human Approval Boundaries

Only Anthony Meza may approve:

- APPLY changes.
- protected-root edits.
- protected-path work.
- commit.
- push.
- merge.
- PR creation.
- worker launch.
- runtime persistence.
- scheduled tasks.
- startup tasks.
- secret or credential handling.
- broker or trading system changes.
- any change to governance authority.

Supervisor output may request approval, but it cannot grant approval.

## Transition Path Toward Full-Time Supervised Orchestration

Level 0: Manual operation.

Level 1: Read-only recommendations.

Level 2: Packet draft previews.

Level 3: Autonomous DRY_RUN inspection.

Level 4: Validator routing recommendations.

Level 5: Commit package preparation without staging.

Level 6: Overnight supervision with morning brief and escalation routing.

Level 7: Full-time supervised orchestration with human approval for all protected mutation.

No level grants unchecked autonomy, autonomous APPLY, autonomous commit, autonomous push, autonomous merge, broker execution, live trading, or secret handling.

## Next Safe Action

Implement read-only supervisor planning through a DRY_RUN helper and schema, then validate that the helper cannot mutate state, launch processes, or expose protected command suggestions.
