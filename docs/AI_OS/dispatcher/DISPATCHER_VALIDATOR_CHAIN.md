# Dispatcher Validator Chain

The validator chain protects multi-worker work from path collisions, blind commits, and unsafe edits.

Before launch:

1. Run `git status --short --branch`.
2. Check recovery state.
3. Check active packets.
4. Check active locks.
5. Flag untracked `??` files as `REVIEW_REQUIRED`.

Before APPLY:

1. Validate packet fields.
2. Validate allowed paths.
3. Validate blocked paths.
4. Validate protected root file rules.
5. Validate lock ownership.
6. Validate lock overlap.
7. Confirm human approval.
8. Parse JSON files if JSON files are involved.

After APPLY:

1. Run `git status --short --branch`.
2. Run `git diff --check`.
3. Parse JSON files if JSON files changed.
4. Parse PowerShell files if PowerShell files changed.
5. Confirm changed files match the approved list.

Before commit packaging:

1. Confirm the repo has no unrelated dirty files in the package.
2. Confirm untracked `??` files are reviewed.
3. Confirm exact files allowed for staging.
4. Confirm no `git add .`.
5. Confirm human review before commit.
6. Confirm human review before push.

