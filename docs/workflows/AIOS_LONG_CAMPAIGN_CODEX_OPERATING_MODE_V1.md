# AIOS Long Campaign Codex Operating Mode V1

## Purpose

Define how Codex should behave during 45-minute to 6-hour AIOS campaigns so it keeps working through approved queue items, recovers bounded failures, preserves owner workflow, and stops only at true governance gates.

## Scope

This operating mode applies when a tokenized AIOS packet explicitly assigns Codex a long-running campaign with allowed paths, forbidden paths, approval authority, validators, checkpoint requirements, and a stop point.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize PR creation, scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## How Codex Should Behave During 45-Minute To 6-Hour Campaigns

Codex should operate as a campaign executor:

- load authority first.
- preflight branch and worktree state.
- create or resume the approved lane.
- build a work queue from the packet.
- complete every approved artifact it can safely complete.
- checkpoint frequently.
- validate deterministically.
- recover bounded failures without looping.
- produce a protected publishing handoff.

Codex should not stop after the first file, first report, first validator pass, or first recoverable problem.

## Work Queue Rule

The campaign work queue is the source of execution order after preflight. Every item must map to the packet objective and allowed paths.

Each item should have:

- target artifact or validator.
- required sections or checks.
- related docs to inspect.
- expected cross-links.
- checkpoint trigger.
- stop condition.

New work can be added only when it is a recovery work item or cross-link required by an approved artifact.

## Continue-After-Success Rule

After a successful edit, report update, or validator pass, Codex must ask:

```text
Can I safely contribute more inside approved scope?
```

If yes, continue to the next queue item. If no, checkpoint and hand off.

## Continue-After-Recoverable-Failure Rule

Recoverable failures are not endpoints. Codex should classify the failure, record it, perform the bounded recovery if approved, validate the recovery, update checkpoint, then continue.

Examples:

- missing report path inside allowed boundary.
- markdown structure issue.
- cross-link miss.
- parser false positive that can be resolved by clearer wording.
- read-only shell `1312` failure that can be bypassed with existing evidence after one retry.

## Self-Critique Rule

Codex must use this exact self-critique after each artifact, recovery, or validator:

```text
Can I safely contribute more inside approved scope?
```

The answer is yes only when the next work item stays inside approved paths, does not need protected actions, does not need broker/API or credential access, does not execute trading logic, does not move money, and does not activate production, scheduler, webhook, or daemon paths.

## When To Pause

Pause when:

- the owner sends a conflicting newer instruction.
- checkpoint says pending work requires owner evidence.
- context compaction requires a resume readback.
- validation is still running and output is required before editing.
- related authority needs inspection before mutation.

Pause is not completion. The next safe action must be explicit.

## When To Hand Off

Hand off when:

- protected publishing is ready.
- a required command is blocked by `1312` or another shell failure.
- Git or GitHub requires owner PowerShell.
- external evidence is required.
- branch/worktree state is unsafe.
- dirty files belong to another lane.
- validator failure cannot be repaired inside approved scope.
- safety boundary appears.

## How To Avoid Baby-Work Stopping

Baby-work stopping happens when Codex finishes one small artifact and reports completion even though the packet still lists pending approved work.

Avoid it by:

- tracking the full artifact list.
- checkpointing progress after groups.
- continuing after successful subtasks.
- treating reports as evidence, not endpoints.
- ending only when all required artifacts and validation are complete or a stop gate is reached.

## How To Avoid Repeated 1312 Loops

If `CreateProcessAsUserW failed: 1312` appears:

- retry read-only inspection at most once.
- do not retry write commands.
- do not retry protected Git/GitHub commands.
- record the command and result in the checkpoint.
- switch to alternate deterministic validation only when safe.
- hand off to owner PowerShell when a blocked command is required.

## How To Avoid Re-Prompt Churn

Codex should not ask the owner for routine continuation when:

- the packet already approves the next local docs/report edit.
- no protected action is required.
- dirty state is same-campaign.
- validators are available.
- recovery is bounded and approved by playbook.

Codex should ask or hand off only when authority, safety, state, or protected-action approval is missing.

## How To Preserve Familiar Owner Workflow

Codex should preserve the owner's normal flow:

- local docs/report work happens in the approved branch.
- protected publishing is handed off as exact PowerShell.
- check/watch and merge remain separated.
- no direct push to protected main.
- no hidden branch switching or cleanup.
- no new workflow model introduced mid-lane.

## How To Preserve Repo Safety

Repo safety is preserved by:

- honoring `AGENTS.md` as top local authority.
- honoring `RISK_POLICY.md` safety blocks.
- using exact allowed paths and forbidden paths.
- avoiding duplicate authority.
- preserving dirty owner work.
- updating checkpoints.
- validating before completion claims.
- stopping at protected actions.

## How To Avoid Changing Workflow Mid-Lane

Do not introduce new automation, scripts, schemas, services, runtime behavior, dashboard behavior, broker/API paths, or trading logic in a docs campaign. If a better workflow or tool is discovered, record it as a recommendation in the final report and keep the current lane focused.

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md`
- `docs/governance/AIOS_FAILURE_MEMORY_V1.md`
- `docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md`
- `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md`
- `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
