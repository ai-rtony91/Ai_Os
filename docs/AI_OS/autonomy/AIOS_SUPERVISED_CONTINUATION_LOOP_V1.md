# AI_OS Supervised Continuation Loop v1

## Purpose

This loop is a DRY_RUN control helper for supervised progression through the Forex paper chain.
It does not run workers, does not launch daemons, and does not execute any protected
pipeline action.

The loop is intentionally constrained to:

- scan local repo state,
- run the FOREX recommender as the first domain recommender,
- propose the next safe packet,
- report required validator checklist and blocked actions,
- require Human Owner review,
- provide a concise Codex handoff summary.

## What it inspects

- Repo branch and dirty/untracked state.
- Active packet id from `automation/orchestration/work_packets/active` (if available).
- Campaign next task recommendation (if registry support is present).
- FOREX continuation recommendation from `Get-AiOsForexNextBuildPacket.DRY_RUN.ps1`.
- Validator script availability for the continuation checklist.

## DRY_RUN output contract

`Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1` outputs a record with:

- `schema = AIOS_SUPERVISED_CONTINUATION_PLAN.v1`
- `mode = DRY\_RUN_READ_ONLY`
- `execution_allowed = false`
- `human_approval_required = true`
- `can_continue_without_anthony = false`
- `continuation_status` (`READY_FOR_APPROVAL`, `REVIEW_REQUIRED`, `BLOCKED`)
- `exact_next_safe_action`
- `codex_handoff_summary`

## Stop rule

- If the repo is dirty/untracked, continuation status must be `REVIEW_REQUIRED` (or `BLOCKED`)
  and the script must not recommend immediate execution.
- If repo is clean and FOREX recommender output is valid, status is
  `READY_FOR_APPROVAL` (never `READY_TO_EXECUTE`).

## Difference from full autonomy

This loop produces a supervised recommendation only. It does not mutate runtime,
telemetry, approvals, queues, locks, worker inbox, scheduler, or daemon state.
It exists as a safe checkpoint before Codex APPLY packet generation.

## Blocked actions preserved

- live trading
- broker/OANDA
- real orders
- webhooks
- real market data
- API keys/secrets
- scheduler/daemon
- worker launch
- runtime mutation
- telemetry mutation
- dashboard mutation
- Cloudflare
- backup sync
- push/PR/merge automation

## Anthony execution

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/continuation/Get-AiOsSupervisedContinuationPlan.DRY_RUN.ps1 -OutputJson
```

When the output reports `continuation_status = READY_FOR_APPROVAL`, Anthony should run the
listed required validators, review safety gates, and then approve the generated Codex
packet for the next step.
