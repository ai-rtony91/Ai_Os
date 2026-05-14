# Validator Stage Matrix

## Purpose

This matrix shows which validators run at each runtime stage.

It is beginner-readable by design. Each stage should produce one clear status and one clear next safe action.

## Stages

| Stage | When it runs | Main question |
| --- | --- | --- |
| `pre_claim` | Before a worker accepts work. | Is the packet safe to assign? |
| `pre_apply` | Before approved APPLY edits begin. | Is the package approved and scoped? |
| `post_apply` | After APPLY edits finish. | Did the package change only approved files? |
| `pre_commit_package` | Before any staging or commit packaging. | Is the repo clean enough for exact-file staging? |
| `recovery_review` | When a worker or lock is stale. | Is human recovery approval needed? |
| `recovery_resume` | Before a stopped packet resumes work. | Is resume safe after stale or interrupted state? |

## Validator Routing Matrix

| Validator | pre_claim | pre_apply | post_apply | pre_commit_package | recovery_review | recovery_resume |
| --- | --- | --- | --- | --- | --- | --- |
| Exact-file staging | REVIEW_REQUIRED | REVIEW_REQUIRED | REVIEW_REQUIRED | BLOCKED if missing | REVIEW_REQUIRED | REVIEW_REQUIRED |
| Dirty repo | REVIEW_REQUIRED | REVIEW_REQUIRED | REVIEW_REQUIRED | BLOCKED if unrelated | REVIEW_REQUIRED | BLOCKED if unclear |
| Allowed path | PASS or FAIL | PASS or FAIL | PASS or FAIL | PASS or FAIL | REVIEW_REQUIRED | PASS or FAIL |
| Blocked path | PASS or BLOCKED | PASS or BLOCKED | PASS or BLOCKED | PASS or BLOCKED | REVIEW_REQUIRED | PASS or BLOCKED |
| Protected root | PASS or BLOCKED | PASS or BLOCKED | PASS or BLOCKED | PASS or BLOCKED | REVIEW_REQUIRED | PASS or BLOCKED |
| Runtime JSON | REVIEW_REQUIRED | REVIEW_REQUIRED | PASS or FAIL | PASS or FAIL | REVIEW_REQUIRED | PASS or FAIL |
| Stale worker | PASS or REVIEW_REQUIRED | PASS or REVIEW_REQUIRED | PASS or REVIEW_REQUIRED | REVIEW_REQUIRED | PASS or BLOCKED | BLOCKED if unresolved |
| Stale lock | PASS or REVIEW_REQUIRED | PASS or REVIEW_REQUIRED | PASS or REVIEW_REQUIRED | REVIEW_REQUIRED | PASS or BLOCKED | BLOCKED if unresolved |
| Recovery resume | SKIPPED | SKIPPED | REVIEW_REQUIRED | REVIEW_REQUIRED | PASS or BLOCKED | PASS or BLOCKED |

## Stage Status Rules

Use the most restrictive status from all checks:

1. If any check is `BLOCKED`, the stage status is `BLOCKED`.
2. If no check is blocked but any check is `FAIL`, the stage status is `FAIL`.
3. If no check is blocked or failed but any check is `REVIEW_REQUIRED`, the stage status is `REVIEW_REQUIRED`.
4. If every check is `PASS`, the stage status is `PASS`.

## Stage Next Safe Actions

| Stage status | Next safe action example |
| --- | --- |
| `PASS` | `Continue to the next validator stage.` |
| `FAIL` | `Fix the failed check, then rerun the validator chain.` |
| `BLOCKED` | `Stop and request a new human decision before continuing.` |
| `REVIEW_REQUIRED` | `Review the listed files and state before continuing.` |

## Recovery Resume Rules

Recovery resume must return `BLOCKED` when interrupted APPLY evidence is missing, an orphan packet has no owner, or a stale lock still claims the files. It may return `PASS` only when the packet, worker, lock, dirty repo state, and approval record all agree on the next safe action.
