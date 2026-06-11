# Final Open PR Cleanup Matrix After #533

Status: REPORT_ONLY

Live PR state capture: FAILED
Confidence: LOW
Fallback evidence: `Reports/pr_backlog_reconciliation/open_pr_backlog_after_570_reconciliation.json`

The packet attempted to capture live open PR state with `gh pr list`, but the Windows sandbox returned `CreateProcessAsUserW failed: 1312`. No close action was performed because the optional safe-close phase requires working `gh` CLI and live confirmation that each PR is still open.

## Safe Close Batch Status

| PR | Fallback classification | Action in this packet |
| --- | --- | --- |
| #554 | SUPERSEDED | NOT CLOSED - live state unavailable |
| #521 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #511 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #504 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #502 | SUPERSEDED | NOT CLOSED - live state unavailable |
| #469 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #468 | SUPERSEDED | NOT CLOSED - live state unavailable |
| #466 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #294 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #274 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #243 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |
| #236 | STALE_NEEDS_CLOSE_REVIEW | NOT CLOSED - live state unavailable |

## Autonomy Keepers

| PR | Current status | Action |
| --- | --- | --- |
| #533 | MERGED ON MAIN | No close action. Functionality is now represented on main. |
| #528 | MERGED ON MAIN | No close action. Functionality is now represented on main. |

## Dependency Batch

Handle these in a separate dependency lane with CI/dashboard validation and no auto-merge:

- #445
- #444
- #359
- #358
- #357
- #251
- #249

## High-Risk Review Group

Do not close or merge these from this packet:

- #550
- #462
- #451
- #449
- #437
- #436
- #300
- #301
- #295
- #267

Reasons include runtime/queue surfaces, GitHub Actions, scheduler/SOS adjacency, broad automation, supervisor branches, dashboard deployment, or forex/trading scope.

## Non-Main-Base Group

- #301 targets `phase-night-supervisor-layer2-memory`, not `main`. Handle it separately from main PR backlog cleanup.

## Close Actions Performed

None.

## No Blind Merge Warning

No PR in this backlog should be blindly merged. Any merge target needs current live PR state, file-level diff review, validation, required checks, and separate Human Owner approval.
