# AI_OS Operator Workflow

Status: canonical workflow
Sources: `docs/AI_OS/operator`, `docs/AI_OS/operator_workflows`, `docs/workflows/aios-operator-workflows.md`

## Purpose

This workflow defines the human-controlled AI_OS operating loop. It does not approve commits, pushes, merges, deployments, worker launches, broker execution, or live trading.

## Role Naming Standard

Use these role names when clarity matters:

- OPERATOR = human in control of the repo, session, or workflow.
- END USER = future customer or user of AI_OS applications, dashboards, or tools.
- AI WORKER = Codex, Claude, ChatGPT, or automation agent performing scoped tasks.
- TERMINAL WORKER = shell or window assigned to one lane or work category.
- LANE = job category or work area assigned to a terminal worker or AI worker.

Use OPERATOR for repo/session authority and approvals. Use END USER for future product or customer context. Avoid using "user" alone when ambiguity matters.

A lane is not a person and is not approval authority. A terminal worker is a shell or window role, not autonomous authority. AI workers may inspect, recommend, validate, and edit when approved, but may not approve protected actions for themselves.

MAIN CONTROL is an operator-control lane/window concept, not a separate person, autonomous agent, or runtime authority. Runtime behavior alone must not create authority. Approval authority remains with the OPERATOR.

## Morning Startup Workflow

The current canonical AI_OS V2 startup workflow is manual and operator-controlled.

Startup authority currently lives in `AGENTS.md`, `README.md`, and this operator workflow. Startup scripts are helpers, not authority.

Canonical first actions:

1. Open the active V2 repo.
2. Run `git status --short --branch`.
3. Read current authority and workflow docs before mutation.
4. Inspect repo state before automation or worker launch.

No startup helper may silently mutate runtime state, auto-launch workers or Codex, or auto-register scheduled tasks or startup behavior.

DRY_RUN startup helpers must not write files. Any DRY_RUN helper that writes files is invalid until repaired.

Report generation, telemetry generation, work-intelligence scans, worker launch, or app launch require explicit approval.

Future startup automation must remain preview-first, fail-closed, and operator-approved.

## Standard Loop

1. Inspect current state.
2. Confirm branch and working tree.
3. Classify the task as DRY_RUN or APPLY.
4. Identify allowed paths, blocked paths, validation, and stop point.
5. Produce a DRY_RUN plan when scope is unclear or risky.
6. Wait for explicit human approval before APPLY.
7. Make exact scoped edits only.
8. Run required validation.
9. Report files changed, validation, commit status, push status, and next safe action.

## Git Status Checkpoint Discipline

AI_OS guidance should avoid repetitive status checks after every minor step.

Status checks should be used at major checkpoints only:

- start of a work batch
- pre-commit
- post-push or post-merge
- error recovery
- lane switch
- session shutdown

This protects operator focus, reduces unnecessary interruptions, and keeps guided work grouped into practical mission blocks.

## Operator Command Presentation

Operator-facing instructions should make the next action easy to execute without relying on memory of lane names, terminal titles, or prior context.

Before giving commands, state:

- WHERE the command should run.
- The visible tab, window, lane, or terminal role the operator should use.
- The exact path or repo root expected for the command.

When a command or output block is intended to be copied, wrap it with `COPY START` and `COPY END` markers when that helps the operator distinguish the copyable text from surrounding explanation.

Do not assume the operator remembers lane names. Use the current V2 lane title or role from active topology and avoid stale legacy lane names.

If the same manual workaround must be explained repeatedly, prefer fixing or documenting the responsible script or workflow so the operator does not carry that burden manually.

Persistent window and tab identity should be owned by repo scripts, registry files, checkpoint/session evidence, or other approved workflow artifacts. Manual window or tab renaming is temporary and should not be treated as durable authority.

## Operator Intent Protection Doctrine

AI_OS workflow guidance must protect the operator's intent before solving the technical task.

The operator-visible success condition must be defined before implementation. A change is not complete just because code was edited, validation passed, or a command succeeded. A change is complete only when the operator's real workflow behaves as intended.

Before a work batch begins, identify:

- What the operator is trying to do.
- What the operator should visibly see when it works.
- What should remain unchanged.
- What system component is responsible.
- What assumptions are being made.
- What should be inspected before action.

Workflow rules:

1. Do not solve from the first symptom alone.
   Inspect the responsible boundary before changing files or behavior.

2. Use precise operational language.
   "Exit," "disable," "pause," "close," "hide," "launch," and "remove" are not interchangeable.

3. Define visible success.
   Examples:
   - The tray icon disappears.
   - The terminal opens in the expected repo.
   - The PR shows the expected files.
   - The game launches while the helper is no longer running.
   - Only one helper icon exists.

4. Change one behavior at a time.
   Avoid stacking multiple fixes before testing the operator-visible outcome.

5. Protect do-not-touch boundaries.
   Each task should state what must not be edited, deleted, committed, pushed, recreated, or automated.

6. Separate task classes.
   Repo features, local machine tools, launcher behavior, documentation, temporary workarounds, and operator preferences must not be mixed unless explicitly approved.

7. Stop on drift.
   If the operator says the direction is wrong, stop and realign. Do not defend the current design or add more workarounds.

8. Prefer the smallest safe change.
   Avoid new scripts, watchdogs, dependencies, repo features, or automation layers unless they are required by the operator-visible success condition.

This doctrine applies globally to AI_OS work, Codex prompts, assistant guidance, local tooling, repo edits, automation planning, and troubleshooting.

## Human Approval Gates

Explicit approval is required before:

- APPLY.
- Protected root edits.
- Move, delete, rename, overwrite, reset, or clean.
- Commit.
- Push.
- Merge.
- Deployment.
- Credential, secret, broker, webhook, OANDA, or live trading work.

## Clean Stop Conditions

Stop and report when:

- Current branch is wrong.
- Working tree has unexplained changes.
- Requested scope touches blocked paths.
- Required facts are `UNKNOWN`.
- Evidence conflicts and must be marked `MISMATCH` or `INVALID DATA`.
- Validation fails.
- A protected action lacks approval.

## Final Report Contract

Every substantial workflow report should include:

- Task.
- Files inspected.
- Files changed.
- Validation result.
- Errors.
- Unknowns.
- Commit status.
- Push status.
- Next safe action.
