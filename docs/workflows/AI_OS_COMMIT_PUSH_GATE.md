# AI_OS Commit/Push Gate

## Purpose

The AI_OS Commit/Push Gate defines how Codex classifies requested protected repository actions before staging, committing, pushing, creating a PR, watching checks, merging, or syncing local main.

This is a governance and workflow specification. It does not stage files, commit, push, create PRs, watch checks, merge, reset, clean, delete branches, or sync local main by itself.

The gate reduces repeated operator approval prompts only when the exact action is already proven safe. It does not authorize blind autopilot.

This gate is now part of the broader Protected Action Gate. It may confirm that a requested protected action is safe enough to present for execution, but it does not create Human Owner approval by itself.

The exact-scope DRY_RUN helper is:

```text
automation/orchestration/pr_gates/Invoke-AiOsProtectedActionRunner.DRY_RUN.ps1
```

The runner emits evidence only. It classifies supplied action scope and safety evidence, then stops. It never executes the protected action and never grants approval by itself.

## Approval Markers

Protected action approval must be current-session, exact-scope, and action-specific.

Required markers:

| Marker | Protected action |
|---|---|
| `APPROVE_STAGE_EXACT_FILES` | Stage exact named files only. |
| `APPROVE_COMMIT` | Create one exact commit with the approved message and cached diff. |
| `APPROVE_PUSH` | Push one exact branch to one exact remote target. |
| `APPROVE_PR_CREATE` | Create one exact pull request with the approved base, head, title, and body. |
| `APPROVE_CHECK_WATCH` | Watch checks for one exact pull request. |
| `APPROVE_MERGE` | Merge one exact PR or merge target. |
| `APPROVE_SYNC_MAIN` | Sync local `main` to the approved remote state after merge. |
| `APPROVE_BRANCH_DELETE` | Delete one exact branch. |
| `APPROVE_RESET_OR_CLEAN` | Run one exact reset or clean recovery action. |
| `BLOCK_PROTECTED_ACTION` | Explicitly deny or stop a protected action. |

Approval markers do not transfer between actions. Stage approval does not approve commit. Commit approval does not approve push. Push approval does not approve PR creation. PR creation approval does not approve check watching or merge. Check-watch approval does not approve merge. Merge approval does not approve local main sync, branch deletion, reset, or clean.

CI pass, validator PASS, dashboard state, supervisor output, or PR readiness output does not authorize merge. Merge requires `APPROVE_MERGE` and the exact PR or merge target.

Merge approval does not include branch deletion unless `APPROVE_BRANCH_DELETE` is separately present.

Gate output confirms safety classification only. Human Owner approval remains required for every protected action.

## Gate States

The gate must return exactly one of these states:

1. `SAFE_TO_STAGE`
2. `SAFE_TO_COMMIT`
3. `SAFE_TO_PUSH`
4. `SAFE_TO_PR_CREATE`
5. `SAFE_TO_CHECK_WATCH`
6. `SAFE_TO_MERGE`
7. `SAFE_TO_SYNC_MAIN`
8. `HUMAN_APPROVAL_REQUIRED`
9. `BLOCKED`

## Inputs

A protected-action gate decision must identify:

- lane name
- branch
- allowed write boundary
- requested action: stage, commit, push, pr_create, check_watch, merge, or sync_main
- exact files approved for staging when committing
- changed file list
- reviewed diff summary
- cached diff file list when committing
- validation result
- commit message when committing
- push target when pushing
- PR base/head when creating a PR
- PR number when watching checks or merging
- checks status and mergeability before merging
- clean repo status before local main sync
- commits intended for push when pushing, or explicit authorization to push the current committed lane output
- visible GitHub ruleset or validate warning when pushing

If any required input is missing, the result must not be a `SAFE_TO_*` state.

## `SAFE_TO_STAGE`

Staging may be classified `SAFE_TO_STAGE` only when all of these are true:

1. Stage is explicitly authorized with `APPROVE_STAGE_EXACT_FILES`.
2. The lane, branch, and exact approved file list are supplied.
3. Changed files are known and are inside the exact approved list or approved boundary.
4. No broad staging command such as `git add .`, `git add -A`, or `git add --all` is requested.
5. Blocked paths, secrets, broker, OANDA, live trading, real order, dashboard, backup, generated junk, and unsafe path terms are absent.

When the result is `SAFE_TO_STAGE`, Codex may use the decision as evidence for a separately approved exact-file staging command. The runner itself does not stage.

## `SAFE_TO_COMMIT`

Commit may be classified `SAFE_TO_COMMIT` only when all of these are true:

1. The task explicitly authorizes Codex to commit.
2. The lane is named.
3. The allowed write boundary is named.
4. The exact files to stage are named.
5. The changed file list is known.
6. The diff has been reviewed by Codex and shown or summarized.
7. Every changed file is inside the allowed lane or write boundary.
8. The cached diff contains only the approved files.
9. No untracked backlog is staged.
10. `git add .` is not used.
11. Validation passed.
12. The commit message is provided.
13. Merge conflicts are not present.

When the result is `SAFE_TO_COMMIT`, Codex may stage only the named files, run `git diff --cached`, verify the cached diff contains only those files, and commit with the provided message.

## `SAFE_TO_PUSH`

Push may be classified `SAFE_TO_PUSH` only when all of these are true:

1. Push is separately and explicitly authorized.
2. The branch is `main` or is explicitly named.
3. The push target is `origin/main` or is explicitly named.
4. The commits to push are known, or the lane explicitly authorizes pushing the current committed lane output.
5. No new files are edited during the push lane.
6. No files are staged during the push lane.
7. No commit is created during the push lane.
8. No branch switching, merge, rebase, reset, or clean operation is part of the push lane.
9. Any GitHub ruleset or `validate` warning visible in push output is reported.

When the result is `SAFE_TO_PUSH`, Codex may push only the named branch to the named remote target.

## `SAFE_TO_PR_CREATE`

PR creation may be classified `SAFE_TO_PR_CREATE` only when all of these are true:

1. PR creation is explicitly authorized with `APPROVE_PR_CREATE`.
2. The base branch, head branch, title/body evidence, and lane scope are exact.
3. The head branch differs from the base branch.
4. Validation evidence is passing.
5. No blocked paths or unsafe scope terms are present.

When the result is `SAFE_TO_PR_CREATE`, Codex may use the decision as evidence for a separately approved `gh pr create` command. The runner itself does not create the PR.

## `SAFE_TO_CHECK_WATCH`

Check watching may be classified `SAFE_TO_CHECK_WATCH` only when all of these are true:

1. Check watching is explicitly authorized with `APPROVE_CHECK_WATCH`.
2. The PR number is exact.
3. The lane and branch context are supplied.
4. No mutation command is included.

When the result is `SAFE_TO_CHECK_WATCH`, Codex may use the decision as evidence for separately approved or read-only check watching. The runner itself does not start check watching.

## `SAFE_TO_MERGE`

Merge may be classified `SAFE_TO_MERGE` only when all of these are true:

1. Merge is explicitly authorized with `APPROVE_MERGE`.
2. The PR number or merge target is exact.
3. Required checks are passing.
4. Mergeability is clean.
5. Validation evidence is passing.
6. No force, admin bypass, reset, clean, branch deletion, or unresolved review blocker is included.

When the result is `SAFE_TO_MERGE`, Codex may use the decision as evidence for a separately approved merge command. The runner itself does not merge.

## `SAFE_TO_SYNC_MAIN`

Local main sync may be classified `SAFE_TO_SYNC_MAIN` only when all of these are true:

1. Local main sync is explicitly authorized with `APPROVE_SYNC_MAIN`.
2. The current branch and target branch are both `main`.
3. Repo status evidence is clean or synced.
4. The expected remote/main state is known by the calling packet.
5. No reset, clean, branch deletion, or unrelated dirty state is included unless separately approved by an exact recovery packet.

When the result is `SAFE_TO_SYNC_MAIN`, Codex may use the decision as evidence for a separately approved local sync flow. The runner itself does not switch branches, pull, reset, clean, or delete branches.

## `HUMAN_APPROVAL_REQUIRED`

The gate must return `HUMAN_APPROVAL_REQUIRED` when the action may be valid but still requires an explicit operator decision.

Human approval is required for:

- running `.ps1` scripts
- delete, move, copy, or write operations outside approved file creation or approved file edits
- branch switching
- `git reset`
- `git clean`
- broad recursive operations
- untracked backlog handling
- uncertain scope
- using `git add .`, even if a lane is named
- any change that crosses lane or write-boundary ownership
- incomplete validator, PR, check, mergeability, or local-sync evidence when the action may still be useful after review

Codex must stop and ask for explicit approval before proceeding when this state is returned.

## `BLOCKED`

The gate must return `BLOCKED` when:

- the command is outside the lane
- the command touches unapproved files
- the command stages broad backlog
- the command uses `git add .`
- validation fails
- cached diff does not match approved files
- direct push to `main` is requested for protected work
- required checks are failing, pending, or missing before merge
- repo is dirty before local main sync
- required PR/base/head/target evidence is missing
- merge conflicts exist
- force, reset, clean, branch deletion, or broad staging is requested without exact recovery approval
- the command continues a placeholder task such as `Implement {feature}`
- required evidence is missing
- Codex is uncertain
- the action conflicts with `AGENTS.md`, repo memory, or the operator's current instruction

Codex must stop when this state is returned.

## Required Output

A gate decision should report:

- gate state
- requested action
- lane
- branch
- write boundary
- approved files
- changed files
- cached diff files when committing
- validation evidence
- commit message when committing
- push target and commits when pushing
- PR target evidence when creating, watching, or merging a PR
- local main sync target evidence when syncing
- blockers
- warnings
- reason
- next safe action
- no-mutation confirmation

## Relationship To Existing AI_OS Helpers

Existing helpers may provide evidence for this gate, but they do not replace this gate by themselves.

- `automation/orchestration/show-commit-package.ps1` can preview commit package contents.
- `automation/orchestration/validator_chain_runner/` can provide validation status.
- `automation/orchestration/approval_runner/` can provide approval risk evidence.
- `automation/orchestration/post_push/` can provide post-push verification evidence.
- `automation/orchestration/pr_gates/Invoke-AiOsProtectedActionRunner.DRY_RUN.ps1` can provide exact-scope protected-action gate evidence for stage, commit, push, PR create, check watch, merge, and local main sync.

Executable mutation automation for this gate must not be created until a separate APPLY lane proves the owner path, duplicate search, input schema, output schema, approval model, validator chain, and no-mutation default behavior. The current protected-action runner is DRY_RUN-only evidence.

## Operator Prompt Reduction Rule

Codex may treat `TIER_0_AUTO` and safe `TIER_1_LOW_RISK` commands as `Option 2` by default:

- `Option 2` means: continue the next safe governed DRY_RUN/non-destructive step.
- For protected gates (`merge`, `APPLY`, `commit`, `push`, worker launch, Night Supervisor, SOS/ADB, notifications, broker/OANDA/webhook, live trading, secrets, credentials, `.env`), Codex must keep asking Anthony and never auto-proceed.

Codex may stop asking the operator for repeated 1/2/3 choices for the same protected action only after this gate returns a `SAFE_TO_*` state for the exact protected action and the packet already contains the matching current-session Human Owner approval marker.

Codex must still stop for `HUMAN_APPROVAL_REQUIRED` or `BLOCKED`.
