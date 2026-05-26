# AI_OS Overnight Supervisor Workflow

Status: canonical workflow

## Purpose

The AI_OS Overnight Supervisor defines the first governed read-only supervisor model for overnight and later full-time supervised orchestration.

It reduces routine operator workload by inspecting state, classifying risk, ranking next safe actions, drafting packet proposals, and preparing a morning brief. It does not execute protected actions.

Overnight Supervisor is not autonomous APPLY authority.

## Scope

This workflow applies to future overnight supervisor reports, planner scripts, schemas, morning brief output, escalation packets, and semi-autonomous orchestration proposals.

It governs read-only intelligence for:

- repo state.
- packet queues.
- worker state.
- approval state.
- validator recommendations.
- stale packet detection.
- blocker detection.
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
- repo health summary.
- stale packet summary.
- worker and lane review summary.
- approval state summary.
- validator recommendation summary.
- escalation item list.
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

## Stop Conditions

The Overnight Supervisor must stop when:

- required authority chain is missing.
- execution mode is missing or inconsistent.
- approval state is missing for protected work.
- evidence is stale, invalid, or contradictory.
- requested action would mutate state.
- requested action would launch workers, loops, daemons, terminals, scheduled tasks, or startup tasks.
- requested action would stage, commit, push, merge, delete, move, or rename files.
- protected trading, broker, secret, credential, or live execution scope appears.
- validator chain is missing or fails.
- output would imply APPLY without visible human approval.

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
