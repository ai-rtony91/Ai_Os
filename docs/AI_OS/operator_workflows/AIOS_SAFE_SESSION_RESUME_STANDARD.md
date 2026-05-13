# AI_OS Safe Session Resume Standard

## Purpose

Safe Session Resume restores operator context after a pause, crash, restart, or new chat.

It restores state for review only. It does not resume execution.

## Resume Evidence

The resume packet should show:

- last_completed_phase
- current_in_progress_phase
- active_workers
- unresolved_conflicts
- stale_workers
- uncommitted_files
- last_known_git_status
- resume_warning_state

## Restore Rules

AI_OS may restore:

- where the operator left off
- active worker state
- unresolved conflicts
- pending approvals
- unfinished APPLY packages
- validator chain position
- next safe action

AI_OS must not restore:

- active execution
- autonomous APPLY
- merge execution
- automatic commit
- automatic push
- background worker state
- broker execution
- OANDA
- API key handling
- live trading

## Stale State Handling

If evidence is old, missing, or unverifiable:

- mark it `STALE` or `UNKNOWN`
- block promotion
- require operator review
- do not invent missing facts

## Invalid Resume Handling

If resume evidence conflicts with current repo state, mark it `INVALID DATA` and stop promotion until the operator reviews the mismatch.

## Next Safe Action

Every resume packet must include one clear next safe action.
