# AI_OS Approval Pause Resume Rules

Purpose:
Model approvals as pauses inside a run, not as separate runs.

## Approval States

- `approval_requested`
- `approval_pending`
- `approval_granted`
- `approval_rejected`
- `resumed_from_state`
- `parked_by_human`
- `expired`

## Rules

Human approval pauses a run. It does not start a new run.

When approval is required, the run must store:

- run ID
- packet ID
- requested action
- approval scope
- allowed paths
- forbidden paths
- validator evidence
- dirty-tree state
- stop point
- resume command or packet

## Resume

A resumed run must verify:

- same worktree or approved worktree transfer
- same branch or approved branch transfer
- no forbidden dirty files
- approval is current and in scope
- state strategy has not changed silently
- validator evidence is still valid or rerun

## Rejection

If approval is rejected, the run must stop and mark `approval_rejected`. It must not continue by choosing a lower-friction path.

