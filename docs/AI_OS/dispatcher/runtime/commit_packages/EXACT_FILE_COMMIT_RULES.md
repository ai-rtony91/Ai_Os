# Exact File Commit Rules

AI_OS commits must be built from exact approved files.

## Forbidden Staging

These commands are not allowed for AI_OS runtime commit packages:

- `git add .`
- `git add -A`
- wildcard staging without prior expansion and human review

## Required Staging Behavior

The operator must stage only files listed in the approved commit package.

Before commit, staged files must be verified by comparing:

1. Approval record file list.
2. Commit package file list.
3. Actual staged file list.

If the lists do not match, the package becomes `BLOCKED` or `REVIEW_REQUIRED`.

## Dirty Repo Behavior

Dirty repo state does not block DRY_RUN.

Dirty repo state blocks commit readiness when:

- unrelated modified files exist
- untracked files exist without review
- staged files include anything outside the package
- protected files appear without explicit approval

## Commit And Push

Commit approval and push approval are separate decisions.

No commit package may auto-commit or auto-push.

