> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS APPLY Routing Chain

## Purpose

The APPLY Routing Chain defines how a DRY_RUN item becomes an APPLY candidate without removing operator control.

## Chain

```text
DRY_RUN
-> validation
-> approval request
-> APPLY candidate
-> exact-file evidence
-> merge-ready package
```

## State Definitions

`DRY_RUN` means the task has a plan and no files are changed.

`validation` means required validators are identified or run by explicit operator instruction.

`approval request` means the operator is asked to approve exact files and scope.

`APPLY candidate` means the task is ready for approved file edits only.

`exact-file evidence` means changed files and validation output are available for review.

`merge-ready package` means evidence is complete enough for operator merge review. It does not execute merge.

## Required Evidence

Each APPLY route should include:

- route_id
- source_task
- current_state
- requested_files
- approved_files
- blocked_files
- validator_requirements
- validation_result
- approval_required
- next_safe_action

## Blocked Conditions

Routing is blocked by:

- missing next safe action
- invalid state transition
- unresolved conflict
- stale worker promotion
- missing approval
- protected file violation attempt
- broker/OANDA/API/live trading scope

## What This Does Not Automate

This chain does not approve APPLY, edit files, merge, commit, push, stage files, run broker logic, or run live trading logic.
