# AI_OS Commit/Push Gate

## Purpose

The AI_OS Commit/Push Gate defines how Codex classifies a requested commit or push workflow step before staging, committing, or pushing.

This is a governance and workflow specification. It does not create an executable helper, does not stage files, does not commit, and does not push.

The gate reduces repeated operator approval prompts only when the exact action is already proven safe. It does not authorize blind autopilot.

## Gate States

The gate must return exactly one of these states:

1. `SAFE_TO_COMMIT`
2. `SAFE_TO_PUSH`
3. `HUMAN_APPROVAL_REQUIRED`
4. `BLOCKED`

## Inputs

A commit or push gate decision must identify:

- lane name
- branch
- allowed write boundary
- requested action: commit or push
- exact files approved for staging when committing
- changed file list
- reviewed diff summary
- cached diff file list when committing
- validation result
- commit message when committing
- push target when pushing
- commits intended for push when pushing, or explicit authorization to push the current committed lane output
- visible GitHub ruleset or validate warning when pushing

If any required input is missing, the result must not be `SAFE_TO_COMMIT` or `SAFE_TO_PUSH`.

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

Codex must stop and ask for explicit approval before proceeding when this state is returned.

## `BLOCKED`

The gate must return `BLOCKED` when:

- the command is outside the lane
- the command touches unapproved files
- the command stages broad backlog
- the command uses `git add .`
- validation fails
- merge conflicts exist
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
- cached diff files when committing
- validation evidence
- commit message when committing
- push target and commits when pushing
- reason
- next safe action

## Relationship To Existing AI_OS Helpers

Existing helpers may provide evidence for this gate, but they do not replace this gate by themselves.

- `automation/orchestration/show-commit-package.ps1` can preview commit package contents.
- `automation/orchestration/validator_chain_runner/` can provide validation status.
- `automation/orchestration/approval_runner/` can provide approval risk evidence.
- `automation/orchestration/post_push/` can provide post-push verification evidence.

Executable automation for this gate should not be created until a separate APPLY lane proves the owner path, duplicate search, input schema, output schema, and no-mutation default behavior.

## Operator Prompt Reduction Rule

Codex may stop asking the operator for repeated 1/2/3 choices only after this gate returns `SAFE_TO_COMMIT` or `SAFE_TO_PUSH` for the exact action.

Codex must still stop for `HUMAN_APPROVAL_REQUIRED` or `BLOCKED`.
