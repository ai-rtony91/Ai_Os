# AI_OS DevOps Chef Window v1

## Purpose

The DevOps Chef Window is a safe queue for operator requests before anything is changed in AI_OS. It is for scripts, tool ideas, install recommendations, stack notes, and next safe actions.

This is a planning and validation scaffold only. It does not edit the dashboard UI, install software, start services, handle credentials, change routes, or touch Trading Lab logic.

## Kitchen-Ticket Workflow

1. Request
   - The operator writes a plain-English request.
   - The ticket captures the requester, request type, target path, expected outcome, and evidence needed.

2. Label
   - The request receives labels such as `script_idea`, `tool_recommendation`, `install_recommendation`, `stack_note`, `next_safe_action`, or `blocked_action`.
   - Labels help sort the queue without approving work.

3. Safety check
   - The request is checked against safety gates and blocked actions.
   - Any missing facts are marked `UNKNOWN`.
   - Any evidence conflict must be marked `MISMATCH` or `INVALID DATA`.

4. Wait for approval
   - The ticket remains in `waiting_for_approval` status until the operator approves or rejects it.
   - No APPLY action starts from this scaffold.

5. Approve or reject
   - Approved tickets can become a future DRY_RUN plan.
   - Rejected tickets stay logged with a reason.

6. Log completion
   - Completion records what happened, what was not done, the evidence used, and the next safe action.

## Required Ticket Fields

- `ticket_id`
- `schema_version`
- `window`
- `status`
- `request`
- `labels`
- `safety_check`
- `approval`
- `completion_log`
- `next_safe_action`

## Blocked Actions

The DevOps Chef Window must block these actions unless a separate approved workflow explicitly allows them:

- Dashboard UI edits
- JavaScript dashboard edits
- Installs
- Startup tasks
- Secrets handling
- Credential handling
- Route changes
- Trading Lab logic changes
- Broker orders
- Live trading
- Commits
- Pushes
- Deletes
- Moves
- Renames
- Windows registry changes
- Firewall, VPN, BitLocker, BIOS, UEFI, or browser policy changes

## Safety Gates

- Default to DRY_RUN before APPLY.
- Require operator approval before file changes.
- Keep work inside approved paths.
- Validate JSON before use.
- Log bad data, failed validation, or evidence conflicts.
- Treat unknown facts as `UNKNOWN`.
- Do not mix AI_OS DevOps planning with trading execution.

## Current Scope

This v1 scaffold provides:

- One plain-English planning document.
- One mock JSON kitchen ticket.
- One validator script.

It does not provide dashboard wiring, live automation, startup execution, installation, credential access, or route changes.
