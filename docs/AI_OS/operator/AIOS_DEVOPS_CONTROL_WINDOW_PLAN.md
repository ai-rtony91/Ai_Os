> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS DevOps Control Window Plan

## 1. Purpose

Phase 25 plans the AI_OS DevOps Control Window. The window reduces manual relay work by making the operator workflow visible in one local dashboard/control panel concept.

This phase is documentation and mock-data only. It does not create real automation.

## 2. What The Control Window Is

The DevOps Control Window is the future operator cockpit for:

- queue review
- workload packet preparation
- DRY_RUN review
- APPLY approval tracking
- validation status
- commit package review
- push readiness
- morning workflow guidance

It turns scattered manual steps into a visible sequence.

## 3. What It Is Not

The first version is not:

- a command runner
- a worker launcher
- an APPLY engine
- a Git client
- a merge tool
- a rollback tool
- a broker/OANDA/API/live execution surface

It must not run hidden shell commands.

## 4. Operator Workflow Steps

The control window must display these workflow states:

1. Next Approved Workload
2. Generate Codex Prompt
3. Run DRY_RUN
4. Review Report
5. Approve APPLY
6. Validate
7. Commit Package
8. Push
9. Morning Workflow

Each state should show current status, required evidence, allowed action, blocked action, and whether operator approval is required.

## 5. Display-Only First Version

Phase 25 is display-only.

Allowed:

- show queue item evidence
- show status
- show required evidence
- show copy-ready guidance text
- show next safe action

Blocked:

- command execution
- hidden shell commands
- worker launch
- APPLY
- merge
- rollback
- commit
- push
- route changes

## 6. Button / Control Justification

Buttons are display/planning only in this phase.

Rules:

- Every visible button must map to a workflow state.
- If a button has no safe workflow state, it should not exist yet.
- Buttons must not execute commands.
- Buttons must not stage, commit, push, merge, or roll back.
- Buttons must not trigger workers.
- Buttons must not imply approval by display alone.

## 7. Required Data Inputs

Future data inputs:

- Work Intelligence queue item
- workload packet plan
- DRY_RUN report summary
- APPLY approval state
- validation command results
- exact-file commit package
- push approval state
- morning workflow status

If evidence is missing, display `UNKNOWN`.

## 8. Required Status Fields

Each step should support:

- `step_id`
- `label`
- `status`
- `required_evidence`
- `allowed_action`
- `blocked_action`
- `operator_approval_required`
- `display_note`

Allowed statuses:

- `LOCKED`
- `READY`
- `REVIEW`
- `BLOCKED`
- `COMPLETE`
- `UNKNOWN`

## 9. Safety Locks

Safety locks:

- no command execution
- no hidden shell commands
- no Git actions
- no worker launch
- no APPLY
- no commit
- no push
- no broker/live trading
- no OANDA
- no API keys
- no secrets

Commit Package and Push remain locked until validation passes and operator approval exists.

## 10. Future Automation Boundaries

Future automation may suggest commands, but execution must remain separately approved.

Automation boundaries:

- Work Intelligence recommends; it does not approve.
- Codex workers report; they do not approve.
- Dashboard displays; it does not execute.
- Operator approves APPLY, commit, and push.

## 11. Dashboard Placement Recommendation

Recommended placement:

- operator/workbench area
- near Work Intelligence queue
- outside Trading Lab execution surfaces
- compact panel, not a full-screen replacement

The dashboard must stay uncluttered and beginner-readable.

## 12. Validation

Use the standard operator validation gate:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```
