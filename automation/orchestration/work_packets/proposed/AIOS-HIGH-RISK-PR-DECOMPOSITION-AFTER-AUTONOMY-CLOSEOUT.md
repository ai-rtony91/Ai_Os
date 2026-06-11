# Proposed Review Packet: High-Risk PR Decomposition After Autonomy Closeout

Status: PROPOSED / REVIEW-ONLY  
This file is not an executable Codex packet and does not authorize APPLY, commit, push, merge, PR closure, runtime launch, runtime execution, queue mutation, scheduler registration, SOS send, broker action, live trading, or credential access.

## Purpose

Decompose high-risk open PRs into smaller reviewable lanes instead of merging broad or stale branches blindly.

## Scope

High-risk PRs:

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

## Allowed Paths

- `Reports/pr_reconciliation/`
- `Reports/autonomy_loop_closure/`
- `automation/orchestration/work_packets/proposed/`

## Forbidden Paths

- `.github/`
- `docs/governance/`
- `docs/workflows/`
- `automation/orchestration/work_packets/active/`
- `automation/orchestration/workers/inbox/`
- `automation/orchestration/command_queue/`
- `automation/orchestration/approval_inbox/`
- `telemetry/runtime/`
- `services/runtime/`
- `services/dispatcher/`
- `services/orchestrator/`
- `services/policy/`
- `apps/dashboard/`
- `apps/trading_lab/`
- `aios/modules/trader/`
- `scripts/control/`
- `.git/`
- `secrets`
- `credentials`
- `.env`
- `broker files`
- `live trading paths`

## Blocked Actions

Do not merge blind. Do not close high-risk PRs from a batch lane. Preserve runtime, trading, scheduler, SOS, broker, credential, and live-trading blocks.

## Validator Chain

- `git diff --check`
- `git status --short --branch`

## Stop Point

Stop after producing a decomposition recommendation. Do not mutate PRs or protected repo systems.

## Safe Next Action

For each high-risk PR, create a separate exact-scope review packet or close recommendation with file-level evidence and Anthony approval.
