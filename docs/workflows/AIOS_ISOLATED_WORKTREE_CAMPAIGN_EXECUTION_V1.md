# AIOS Isolated Worktree Campaign Execution V1

## Purpose

Define the safe workflow for running a new AIOS campaign in an isolated Git worktree when the source worktree must remain untouched because it contains unrelated, stale, or owner-controlled dirty work.

## Scope

This workflow applies only when a packet explicitly authorizes isolated worktree setup or when campaign arbitration selects isolated worktree execution and the owner approves the exact worktree path, branch, allowed paths, forbidden paths, validator chain, and stop point.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize PR creation, scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## Exact Workflow

1. Inspect source status.

```powershell
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git remote -v
```

2. Preserve source untouched.

Do not reset, clean, stash, switch branches, delete files, move files, or stage files in the source worktree.

3. Inspect existing worktrees.

```powershell
git worktree list
```

4. Fetch the approved remote baseline.

```powershell
git fetch origin
git log --oneline -n 5 origin/main
```

5. Create the target worktree from `origin/main`.

```powershell
git worktree add -b lane/example-campaign C:\Dev\Ai.Os.worktrees\example-campaign origin/main
```

The branch and path above are illustrative. A real packet must name exact branch and worktree values.

6. Verify target branch.

```powershell
git -C C:\Dev\Ai.Os.worktrees\example-campaign status --short --branch
git -C C:\Dev\Ai.Os.worktrees\example-campaign branch --show-current
```

7. Edit only target allowed paths.

The campaign worker must run all file reads, writes, and validators against the target worktree path, not the source worktree.

8. Validate target.

```powershell
git -C C:\Dev\Ai.Os.worktrees\example-campaign diff --check
git -C C:\Dev\Ai.Os.worktrees\example-campaign status --short --branch
```

9. Produce protected handoff.

The final report must include exact owner PowerShell commands for staging explicit files, committing, pushing the lane branch, creating the PR, watching checks, and later merging only after checks pass.

## Forbidden Moves

- Do not reset the source worktree.
- Do not clean the source worktree.
- Do not stash source worktree changes.
- Do not switch the source branch away from dirty owner work.
- Do not delete an existing target worktree folder.
- Do not overwrite an existing target worktree.
- Do not use `git add .`.
- Do not edit source worktree files after selecting isolated execution.
- Do not run protected publishing actions without separate explicit Human Owner approval.
- Do not touch broker/API paths, credentials, trading execution, money movement, schedulers, webhooks, daemons, production activation, or secrets.

## Recovery From Existing Target Worktree

If the target path already exists:

1. Run `git worktree list`.
2. If the path is listed and belongs to the intended branch, verify status.
3. If the path is listed but branch or ownership differs, stop and hand off.
4. If the path exists but is not listed by Git, stop and hand off.

Do not delete or reuse unknown folders.

## Recovery From Target Branch Already Existing

If the target branch already exists:

1. Check local and remote branch presence.
2. Check whether the existing branch belongs to the same packet.
3. If same-packet and checkpoint matches, resume.
4. If ownership is unknown, stop.

Do not force-create, delete, reset, or rename the branch without explicit owner approval.

## Recovery From 1312 During Worktree Operations

If Codex hits `CreateProcessAsUserW failed: 1312` during read-only inspection, retry at most once and record the failure.

If Codex hits `1312` during worktree creation, branch creation, fetch, protected Git/GitHub actions, or any required write operation:

- do not retry in a loop.
- do not attempt destructive cleanup.
- record the failed command in the checkpoint.
- produce owner PowerShell handoff.
- stop with `WAITING_FOR_OWNER_POWERSHELL` if the blocked command is required to continue.

## Owner PowerShell Handoff Template

```powershell
cd C:\Dev\Ai.Os
git status --short --branch
git branch --show-current
git worktree list
git fetch origin
$TargetBranch = "lane/example-campaign"
$TargetWorktree = "C:\Dev\Ai.Os.worktrees\example-campaign"
git worktree add -b $TargetBranch $TargetWorktree origin/main
git -C $TargetWorktree status --short --branch
git -C $TargetWorktree branch --show-current
```

The owner must replace the example branch and worktree path with exact values from an approved packet. If either value is unclear, stop before running the command.

## Relationship To Campaign Arbitration Doctrine

`docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md` decides whether isolated worktree execution is appropriate. This workflow defines how to execute that decision while preserving the source worktree and avoiding hidden cleanup.

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/AI_OS_PR_LANE_RUNNER.md`
