# Proposed Review Packet: Dependabot Batch Review After Autonomy Closeout

Status: PROPOSED / REVIEW-ONLY
This file is not an executable Codex packet and does not authorize APPLY, auto-merge, commit, push, merge, dependency installation, runtime mutation, dashboard deployment, broker action, live trading, or credential access.

## Purpose

Review dependency-only PRs separately from autonomy closeout work.

## Scope

Dependency PRs only:

- #445
- #444
- #359
- #358
- #357
- #251
- #249

## Allowed Paths

- `Reports/pr_reconciliation/`
- `Reports/autonomy_loop_closure/`

## Forbidden Paths

- `.github/`
- `apps/dashboard/`
- `node_modules`
- `automation/orchestration/work_packets/active/`
- `automation/orchestration/workers/inbox/`
- `automation/orchestration/command_queue/`
- `automation/orchestration/approval_inbox/`
- `telemetry/runtime/`
- `services/`
- `apps/trading_lab/`
- `aios/modules/trader/`
- `.git/`
- `secrets`
- `credentials`
- `.env`

## Blocked Actions

No auto-merge. No dashboard deployment. No dependency install unless separately approved. GitHub Actions dependency changes require CI review.

## Validator Chain

- `git diff --check`
- `git status --short --branch`

## Stop Point

Stop after classifying dependency PRs and recommending exact next actions. Do not merge or close PRs.

## Safe Next Action

Create a separate dependency-review APPLY packet only after Anthony approves exact PR numbers and validation scope.
