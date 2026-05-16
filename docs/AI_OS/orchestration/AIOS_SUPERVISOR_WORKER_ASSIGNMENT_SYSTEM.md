# AI_OS Supervisor Worker Assignment System

The supervisor worker assignment system converts one operator work goal into a DRY_RUN-only assignment plan.

It answers:

- what workers are needed
- what each worker does
- what lane each worker uses
- what files are in scope
- what validator runs
- what approval is required
- what the next safe action is

## Operating Boundary

The system is a planner, not a launcher. It does not auto-launch Codex, open worker windows, create scheduled tasks, create startup tasks, connect brokers, call APIs, use secrets, place orders, enable live trading, stage files, commit, push, or create PRs.

All APPLY, exact-file staging, commit, push, PR creation, and worker launch actions require separate explicit human approval.

## Planner

Run from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Invoke-AiOsSupervisorPlanner.DRY_RUN.ps1
```

Optional goal override:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Invoke-AiOsSupervisorPlanner.DRY_RUN.ps1 -WorkGoal "Review dashboard orchestration cleanup readiness."
```

The planner reads the lane registry and validator-chain config if present, then prints a JSON preview.

## Worker Roles

`SUPERVISOR-PLANNER` uses the `main_control` lane. It breaks the goal into packets, workers, approvals, validators, and next actions.

`PACKET-AUTHOR` uses the `dispatch_queue` lane. It drafts work-packet previews and keeps active queue mutation blocked until approved.

`LANE-ROUTER` uses the `state_monitor` lane. It maps file scope to the existing lane registry and flags missing or ambiguous lane needs.

`VALIDATOR-ROUTER` uses the `validation_audit` lane. It routes read-only validators and reports PASS, WARN, or FAIL.

`GATEKEEPER` uses the `main_control` lane. It checks approval requirements and previews commit or PR packaging without staging or publishing.

## Validator Routing

Baseline validators:

- `git diff --check`
- `git status --short`
- JSON parse validation for changed `.json` files
- PowerShell parse validation for changed `.ps1` files
- `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1` when orchestration routing is in scope
- `automation/orchestration/validators/Test-ApplyApprovalGate.DRY_RUN.ps1` when approval routing is in scope
- `automation/orchestration/validators/Test-CommitPackageManifest.DRY_RUN.ps1` when commit packaging is in scope

## Approval Routing

DRY_RUN planning is allowed after the operator requests it.

APPLY requires exact approved files and action.

Commit packaging remains preview-only until exact-file staging and commit are separately approved.

Push and PR creation require separate approval after commit approval.

## Next Safe Action

Run the planner, inspect the JSON output, then approve one exact next action: a packet preview, a validator run, or a scoped APPLY request.
