# Runtime Status Output Model

Runtime status outputs help the operator understand current state.

They should be simple, local, and safe for future dashboard use.

## Recommended Outputs

`dispatcher_runtime_status.json`

Overall runtime summary.

`active_worker_table.json`

Source of truth for active worker state.

`packet_runtime_table.json`

Source of truth for packet state.

`lock_runtime_table.json`

Source of truth for lock state.

`approval_runtime_status.json`

Current approval summary.

`validator_runtime_status.json`

Current validator summary.

`recovery_runtime_status.json`

Current recovery summary.

`queue_health_summary.json`

Queue health summary.

`commit_readiness_status.json`

Commit package readiness summary.

`runtime_status_index.json`

Index of runtime status files for humans and later dashboard use.

## Dashboard Rule

Dashboard-facing status files are read-only summaries.

They should not collect secrets.

They should not trigger trading.

They should not trigger APPLY, commit, push, or recovery override.

## Dirty Repo Display

Status output should show dirty repo state clearly.

It should separate approved package changes from unrelated modified or untracked files.

Unrelated dirty files should make commit readiness `REVIEW_REQUIRED`.

