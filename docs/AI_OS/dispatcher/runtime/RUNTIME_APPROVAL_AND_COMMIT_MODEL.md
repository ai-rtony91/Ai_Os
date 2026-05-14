# Runtime Approval And Commit Model

AI_OS runtime work stays human-controlled.

The runtime may prepare information for review, but it must not approve, stage, commit, or push by itself.

## Approval Gates

Human approval is required for:

- APPLY
- recovery resume when state is unknown
- stale lock override
- stale worker reassignment
- commit package approval
- push authorization

## Approval Source Of Truth

Approval decisions belong in:

`Reports/dispatcher/runtime/approval/approval_runtime_ledger.json`

The current summary belongs in:

`Reports/dispatcher/runtime/approval/approval_runtime_status.json`

## Commit Package Source Of Truth

Commit package decisions belong in:

`Reports/dispatcher/runtime/commit_packages/commit_package_ledger.json`

Commit readiness summary belongs in:

`Reports/dispatcher/runtime/commit_packages/commit_readiness_status.json`

## Commit Rules

Never use `git add .`.

Never use `git add -A`.

Stage exact approved files only.

Dirty repo state blocks commit packaging unless every changed file is reviewed and included in the approved package.

Commit and push require separate human approval.

## Why APPLY Stays Human-Controlled

APPLY changes files.

File changes can affect safety rules, dashboard behavior, validators, reports, or future trading-lab workflows.

Human approval keeps scope clear and prevents accidental edits outside the packet.

