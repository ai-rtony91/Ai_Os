> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Operator Fatigue Reduction Plan

## Purpose

This plan reduces operator fatigue without creating autonomous execution.

The focus is organization, clarity, and fewer manual relay steps.

## Reduction Targets

Reduce fatigue from:

- repeated copy and paste
- scattered validator commands
- unclear approval handoffs
- noisy blocked states
- missing next safe actions
- unbatched checkpoint reminders

## Systems

### Guided Next Action

Show one recommended next safe action at a time.

### Compact Task Routing

Group each task by:

- lane
- state
- approval requirement
- blocked reason
- next safe action

### Grouped Validator Execution

Display validator order as one chain:

1. ownership
2. conflict
3. stale worker
4. merge package
5. dashboard integrity
6. protected file boundary

The chain is display guidance unless the operator explicitly runs it.

### Checkpoint Batching

Batch checkpoint reminders by:

- before APPLY
- after APPLY
- before commit package
- after commit
- before push

### Approval Handoff

Approval handoff should include:

- exact files
- blocked files
- validation state
- unresolved conflicts
- stale evidence
- next safe action

## Safety

Fatigue reduction must not hide blocked states, auto-approve work, stage files, merge, commit, push, run background workers, call the internet, or touch broker/OANDA/API/live trading logic.
