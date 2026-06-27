# AIOS Campaign Checkpoint And Resume V1

## Purpose

Define the checkpoint and resume protocol for long-running AIOS campaigns so work can continue after pauses, context compaction, shell failures, validation failures, or owner handoff without losing branch, scope, validation, or safety state.

## Scope

This workflow applies to campaign packets that explicitly authorize checkpoint and report writes inside a named report or documentation path.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize PR creation, scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## Checkpoint Frequency

Campaign checkpoints must be updated:

- after branch setup.
- after every two completed documents or equivalent artifact group.
- after every recovery.
- after validation.
- after final report generation.
- immediately before any protected-action handoff.
- before stopping for a true governance gate.

## Required Checkpoint Fields

Every campaign checkpoint must include:

- `campaign_id`
- `packet_id`
- `mission_id`
- `program_id`
- `epic_id`
- `bucket_id`
- `branch`
- `worktree`
- `base_commit`
- `current_commit`
- `current_objective`
- `completed_work`
- `pending_work`
- `touched_files`
- `validators_passed`
- `validators_blocked`
- `failures_encountered`
- `recovery_attempts`
- `next_safe_action`
- `stop_reason`
- `resume_prompt`

If a value is unknown, record `UNKNOWN`. Do not invent state.

## Resume Protocol

Resume uses evidence, not memory:

1. Read `AGENTS.md`.
2. Read `docs/governance/AI_OS_REPO_MEMORY.md`.
3. Read the active campaign checkpoint.
4. Run `git status --short --branch`.
5. Confirm branch, worktree, and dirty files match the checkpoint.
6. Confirm dirty files are inside the approved packet scope.
7. Read any touched file that will be edited again.
8. Continue from `pending_work` only if no stop gate is active.
9. Update the checkpoint after the next completed work item or recovery.

Resume does not approve APPLY, commit, push, PR creation, merge, reset, clean, broker/API access, credential access, trading execution, or production activation.

## Crash Recovery Rule

After a crash, context compaction, shell reset, or disconnected session, the next worker must treat the checkpoint as a recovery aid, not as command authority.

If checkpoint evidence conflicts with current repo state, mark the state `INVALID DATA`, stop, and report:

- checkpoint branch.
- observed branch.
- checkpoint dirty files.
- observed dirty files.
- touched files.
- last completed work.
- next safe owner action.

## Owner Handoff Rule

When a protected action, blocked shell command, or external dependency is required, the checkpoint must include an owner handoff with exact commands or exact missing evidence.

The owner handoff must not combine check-watch and merge in a way that could merge failed checks. Fix/check blocks and merge/sync blocks must remain separate.

## Example Checkpoint

```text
campaign_id: AIOS-AEE-LONG-CAMPAIGN-FOUNDATION-V1
packet_id: AIOS-AEE-LONG-CAMPAIGN-DOCTRINE-AND-OPERATING-LAW-V1
mission_id: MISSION-AIOS-CORE
program_id: PRG-AIOS-CORE-001
epic_id: EPC-AIOS-AUTONOMOUS-EXECUTION-ENGINE
bucket_id: BKT-AEE-LONG-CAMPAIGN-FOUNDATION
branch: lane/aios-aee-long-campaign-foundation-v1
worktree: C:\Dev\Ai.Os
base_commit: 5e370798
current_commit: 5e370798
current_objective: Create doctrine and workflow artifacts for long campaign execution.
completed_work: Core doctrine; engine workflow.
pending_work: Failure playbooks; failure memory; checkpoint/resume; arbitration; final report.
touched_files: docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md; docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md; Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_CHECKPOINT.md
validators_passed: preflight; structural checks pending.
validators_blocked: read-only directory listing hit 1312 twice.
failures_encountered: CreateProcessAsUserW failed 1312.
recovery_attempts: retry read-only once; continue with targeted evidence.
next_safe_action: Continue authoring approved artifacts.
stop_reason: NONE
resume_prompt: Resume this campaign from the current checkpoint and do not perform protected actions.
```

## Example Resume Prompt

This is an operator-facing outline, not an executable packet. A real Codex packet must use the required routing marker, execution token, bootstrap block, complete identity header, allowed paths, forbidden paths, validator chain, stop point, and final report format.

```text
Resume packet AIOS-AEE-LONG-CAMPAIGN-DOCTRINE-AND-OPERATING-LAW-V1 from:
Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_CHECKPOINT.md

Before continuing:
- Read AGENTS.md.
- Read docs/governance/AI_OS_REPO_MEMORY.md.
- Run git status --short --branch.
- Verify branch lane/aios-aee-long-campaign-foundation-v1.
- Verify dirty files match the checkpoint and are inside approved paths.
- Continue only with pending approved artifacts.
- Do not commit, push, create a PR, merge, reset, clean, stash, access broker/API, access credentials, execute trading logic, move money, activate schedulers, activate webhooks, activate daemons, or activate production paths.
```

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md`
- `docs/governance/AIOS_FAILURE_MEMORY_V1.md`
- `docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md`
- `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md`
- `docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/SAFE_SESSION_RESUME.md`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
