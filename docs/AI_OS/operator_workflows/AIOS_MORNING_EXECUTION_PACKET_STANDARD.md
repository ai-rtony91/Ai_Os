> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Morning Execution Packet Standard

## Purpose

The Morning Execution Packet gives the operator a compact daily starting point.

It collects context, active phases, worker assignments, blocked actions, validator sequence, next safe action, and checkpoint reminders before any APPLY work is considered.

## Required Packet Fields

The packet should include:

- session_date
- repo_path
- current_phase
- active_objective
- approved_scope
- blocked_actions
- pending_approvals
- validator_sequence
- next_safe_action
- checkpoint_reminder
- commit_push_reminder

## Startup Context

Startup context should show:

- current repo
- current branch
- current workflow state
- known blocked conditions
- stale session warnings
- unresolved approvals

Missing evidence must be labeled `UNKNOWN`.

## Active Phases

Active phases should show:

- phase_id
- title
- status
- lane
- owner
- next_safe_action

## Blocked Actions

The packet must keep blocked actions visible:

- autonomous execution
- merge execution
- auto-commit
- auto-push
- startup tasks
- background daemons
- installs
- internet calls
- broker execution
- OANDA
- API keys
- live trading

## Validator Sequence

The morning packet should list validator order without running it automatically:

1. ownership
2. conflict
3. stale worker
4. merge package
5. dashboard integrity
6. protected file boundary

## Checkpoint Reminders

Checkpoint reminders should group:

- current uncommitted changes
- pending exact-file package
- unresolved errors
- unknown evidence
- next safe action

## What This Does Not Automate

This standard does not execute commands, launch workers, apply changes, merge branches, commit, push, or place orders.
