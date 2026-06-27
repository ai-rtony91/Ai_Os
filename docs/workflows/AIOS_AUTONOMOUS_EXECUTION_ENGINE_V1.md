# AIOS Autonomous Execution Engine V1

## Purpose

Define the workflow shape for a bounded Autonomous Execution Engine campaign that can plan, execute, validate, checkpoint, resume, and hand off protected publishing without turning reports or validator success into premature endpoints.

## Scope

This workflow applies to governed AIOS campaign packets that name a lane, branch, worktree, allowed paths, forbidden paths, approval authority, validator chain, stop point, and final report format.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## Mission Contract

The Mission Contract is the immutable campaign intake once preflight passes. It captures:

- Mission, Program, Epic, Bucket, Packet, and Lane identity.
- Mode and zone.
- Supervisor and worker identities.
- Worktree and branch target.
- Allowed paths and forbidden paths.
- Required artifacts.
- Validator chain.
- Stop point.
- Human Owner approval boundary.
- Protected action exclusions.

The Mission Contract must be complete before the campaign begins. If it is incomplete, `AGENTS.md` packet validation rules stop execution.

## Campaign Planner

The Campaign Planner converts the Mission Contract into an ordered work queue. It should group artifacts by dependency and validation needs, not by convenience.

Recommended ordering:

1. Core doctrine.
2. Engine workflow.
3. Recovery playbooks.
4. Failure memory.
5. Checkpoint/resume.
6. Campaign arbitration.
7. Isolated worktree workflow.
8. Long-campaign Codex operating mode.
9. Protected publishing handoff.
10. GitHub CI recovery.
11. Checkpoint and final report.

## Campaign State

Campaign State is the current evidence snapshot:

- current phase.
- current branch and worktree.
- base commit and current commit.
- completed artifacts.
- remaining artifacts.
- touched files.
- validators passed.
- validators blocked.
- failures encountered.
- recovery attempts.
- next safe action.
- stop reason when any stop gate is reached.

Campaign State is evidence only. It does not approve APPLY, commit, push, PR creation, merge, broker/API access, credential access, trading execution, or production activation.

## Work Queue

The Work Queue lists every approved artifact or validator action still pending. Each item should include:

- artifact or validator name.
- required sections.
- related authority to inspect.
- allowed path.
- validator expectation.
- checkpoint trigger.
- stop condition.

Recoverable failures are appended as work items. Unrecoverable failures become stop gates.

## Execution Cycle

Each cycle follows this order:

1. Load campaign state.
2. Select the next approved work item.
3. Inspect related existing authority.
4. Apply the bounded edit.
5. Cross-link related artifacts.
6. Update checkpoint evidence.
7. Run or record validators.
8. Classify failures.
9. Recover if the recovery is approved and bounded.
10. Ask: `Can I safely contribute more inside approved scope?`
11. Continue or hand off.

## Failure Classifier

The Failure Classifier maps an issue to one of these outcomes:

- `RECOVERABLE_IN_SCOPE`: convert to work item and continue.
- `RECOVERABLE_OWNER_POWERSHELL`: prepare exact owner handoff and stop when a required command cannot run safely in Codex.
- `VALIDATION_FAIL_REPAIRABLE`: repair only inside approved paths, then revalidate.
- `PROTECTED_ACTION_REQUIRED`: stop and hand off.
- `SCOPE_EXPANSION_REQUIRED`: stop and request a new packet.
- `SAFETY_BOUNDARY`: hard stop.

## Repair Playbook Selector

The Repair Playbook Selector uses `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md` to choose the narrowest approved recovery. It must not improvise destructive repair, reset, clean, stash, branch switching away from dirty owner work, or protected Git/GitHub actions.

## Validator Runner

The Validator Runner executes deterministic checks that are safe for the lane. Required documentation validators include:

- required artifact existence.
- H1 title presence.
- `Purpose` section presence.
- `Scope` section presence.
- safety boundary statements.
- related cross-links.
- `git diff --check`.

Validator output is evidence only. Validator `PASS` does not approve protected actions.

## Evidence Writer

The Evidence Writer updates checkpoint and report artifacts approved by the packet. Evidence must distinguish completed work, blocked validators, recoveries, protected actions not taken, and next safe action.

Evidence files do not become authority unless a separate governance packet promotes them.

## Checkpoint Writer

The Checkpoint Writer updates the campaign checkpoint:

- after branch setup.
- after every two completed documents.
- after every recovery.
- after validation.
- after final report generation.

Related workflow: `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`.

## Resume Loader

The Resume Loader reads the checkpoint, verifies current branch/worktree state, verifies touched files are inside the allowed boundary, and continues from the next pending work item.

Resume restores context only. It does not restart active execution, approve APPLY, approve protected publishing, or bypass state alignment.

## Stop Gate

The Stop Gate halts the cycle when:

- required authority is missing.
- branch/worktree state conflicts with packet assumptions.
- dirty files belong to another lane.
- a validator fails without approved bounded recovery.
- a protected action is required.
- Codex hits a sandbox or process failure on a required command that cannot be bypassed safely.
- broker/API, credentials, trading execution, money movement, production activation, scheduler activation, webhook activation, daemon activation, or secrets enter scope.
- scope expansion is required.

## Final Handoff

The Final Handoff contains:

- packet result.
- start state.
- branch state.
- files read.
- files created and modified.
- validators run and results.
- recoveries performed.
- stop gates preserved.
- protected actions not taken.
- exact owner PowerShell publishing commands.
- exact commit message.
- exact PR title.
- exact PR body source.
- final status.

Related workflow: `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`.

## Text Diagram

```text
Mission Contract
-> Campaign Planner
-> Campaign State
-> Work Queue
-> Execution Cycle
-> Failure Classifier
-> Repair Playbook
-> Validator Runner
-> Evidence Writer
-> Checkpoint Writer
-> Resume Loader
-> Stop Gate
-> Continue or Handoff
```

## Example 45-Minute Campaign Cycle

```text
00:00-05:00  Load authority, run preflight, create or verify lane branch.
05:00-12:00  Inspect related docs and build the work queue.
12:00-25:00  Write the first two artifacts and cross-links.
25:00-30:00  Update checkpoint and classify failures.
30:00-38:00  Write the next artifact or recover a bounded validation miss.
38:00-43:00  Run deterministic validators that are safe in the current shell.
43:00-45:00  Update checkpoint and either continue or prepare handoff.
```

The campaign does not stop merely because one artifact or one validator succeeds.

## Example 6-Hour Campaign Cycle

```text
Hour 0-1  Preflight, branch/worktree setup, authority read, campaign planning.
Hour 1-2  Core doctrine, engine workflow, checkpoint update, local validation.
Hour 2-3  Failure playbooks, failure memory, recovery classification, checkpoint update.
Hour 3-4  Checkpoint/resume, campaign arbitration, isolated worktree workflow, checkpoint update.
Hour 4-5  Long-campaign operating mode, protected publishing handoff, GitHub CI recovery, checkpoint update.
Hour 5-6  Full deterministic validation, final report, protected-action handoff, final checkpoint.
```

Any true stop gate pauses the campaign and produces the exact owner handoff instead of looping.

## No Protected Action Override

This workflow has no protected action override. It cannot authorize staging, commit, push, PR creation, check watching, merge, local main sync, reset, clean, branch deletion, broker/API access, credential access, trading execution, money movement, production activation, scheduler activation, webhook activation, daemon activation, or secrets.

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_FAILURE_MEMORY_V1.md`
- `docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md`
- `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md`
- `docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md`
- `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`
- `docs/workflows/AI_OS_PR_LANE_RUNNER.md`
