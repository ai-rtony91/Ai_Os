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
