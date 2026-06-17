# AI_OS APPLY Routing Chain

Status: canonical workflow
Source material: `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md`

`docs/AI_OS/**` is reference/source material only. Current workflow authority lives in `docs/workflows/` unless a specific rule is promoted through governance.

## Purpose

The APPLY routing chain defines how a DRY_RUN item becomes an APPLY candidate without removing operator control.

## Chain

```text
DRY_RUN
-> validation
-> approval request
-> APPLY candidate
-> exact-file evidence
-> review package
```

## State Definitions

`DRY_RUN` means the task has a plan and no files are changed.

`validation` means required validators are identified or run by explicit operator instruction.

`approval request` means the operator is asked to approve exact files and scope.

`APPLY candidate` means the task is ready for approved file edits only.

`exact-file evidence` means changed files and validation output are available for review.

`review package` means evidence is complete enough for operator review. It does not execute merge, commit, push, or APPLY.

## Single Live Micro-Trade Exception Routing Boundary

For any future Single Live Micro-Trade Exception, APPLY routing can prepare review packages only. It cannot approve, arm, extend, retry, re-enter, execute, release credential handles, or satisfy the exception.

The exception remains blocked unless `RISK_POLICY.md` is satisfied by explicit Human Owner approval that is one-shot, non-transferable, expiring, packet-bound, and scoped to the exact exception fields. Generic route fields such as `approval_status`, `approved_by_human`, `APPROVED`, or `approval_granted` are not sufficient by themselves.

Routing evidence, review packages, validator summaries, reports, telemetry, queues, and generated artifacts must not contain credentials, broker order IDs, account identifiers, live payloads, private account data, or secret values.

## Required Evidence

Each route should include:

- route ID.
- source task.
- current state.
- requested files.
- approved files.
- blocked files.
- validator requirements.
- validation result.
- approval required flag.
- next safe action.

## Blocked Conditions

Routing is blocked by:

- missing next safe action.
- invalid state transition.
- unresolved conflict.
- stale worker promotion.
- missing approval.
- protected file violation attempt.
- broker, OANDA, API, webhook, or live trading scope.

## Non-Automation Statement

This chain does not approve APPLY, edit files, stage files, commit, push, merge, run broker logic, or run live trading logic.
