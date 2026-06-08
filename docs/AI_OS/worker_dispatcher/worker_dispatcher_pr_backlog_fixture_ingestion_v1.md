# Worker Dispatcher PR Backlog Fixture Ingestion V1

## Purpose

The Dispatcher Assignment Executor can read a local PR backlog fixture so PR
dependency state is available without live GitHub access. Fixture ingestion is
DRY_RUN-only and does not approve merge, APPLY, or worker launch.

## Supported Fields

- `pr_number`
- `title`
- `state`
- `draft`
- `merged`
- `merge_state`
- `base_branch`
- `head_branch`
- `head_sha`
- `changed_paths`
- `labels`
- `updated_at`
- `dependency_notes`

The executor also accepts GitHub CLI-style aliases such as `number`, `isDraft`,
`mergeStateStatus`, `baseRefName`, and `headRefName` when live metadata is
provided explicitly.

## Classifications

- `PR_READY_FOR_REVIEW`
- `PR_MERGED_BASELINE`
- `PR_OPEN_DEPENDENCY`
- `PR_DRAFT_OR_SUPERSEDED`
- `PR_BLOCKED_BY_CONFLICT`
- `PR_REVIEW_REQUIRED`
- `PR_UNKNOWN`

Merged PRs are baseline only when `merged: true` is explicit. Draft, superseded,
or closed-unmerged records are not baseline. Unknown or conflicting merge state
requires review.

## Dependency Rules

PR changed paths are compared with dispatcher candidate paths. Overlap with an
open PR creates a PR dependency finding. Overlap with an explicitly merged PR is
treated as baseline evidence. PR dependency findings do not approve merge, APPLY,
or worker launch.

Missing fixture input is `PR_UNKNOWN`, not a validator failure.

## Walkie Alignment

PR dependency findings emit preview-only internal walkie events:

- `PR_DEPENDENCY_CHANGED` for path overlap or dependency changes.
- `REVIEW_REQUIRED` when PR backlog state is unknown.

Dispatcher never wakes Anthony directly. Watchdog/Pi5 remains the external wake
gate.
