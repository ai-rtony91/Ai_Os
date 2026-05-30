# AI_OS Supervised Auto-Loop Bridge

This folder contains a local-first DRY_RUN bridge for the supervised AI_OS auto-loop.

It is not uncontrolled autonomy. It does not dispatch workers, mutate active queues, mutate approval inboxes, commit, push, merge, deploy, or touch Trading Lab broker execution. It prepares structured recommendations so the operator can review the next safe action.

The bridge demonstrates this supervised chain:

1. Intake a plain-language goal.
2. Convert it into a packet candidate.
3. Check branch, path, and active-system readiness.
4. Recommend validator routing.
5. Produce an approval inbox candidate.
6. Produce a commit package recommendation.
7. Write a finish-line DRY_RUN report.

## Canonical Systems Referenced

This scaffold points at existing AI_OS systems instead of replacing them:

- Work packets: `automation/orchestration/work_packets/`
- Worker registry and inbox: `automation/orchestration/workers/`
- Approval inbox: `automation/orchestration/approval_inbox/`
- Validators: `automation/orchestration/validators/`
- Commit packages: `automation/orchestration/commit_packages/`
- Clean-state gate: `automation/orchestration/clean_state_gate.ps1`
- Telemetry evidence: `telemetry/`

## Safety Boundary

All scripts in this folder are DRY_RUN only. They may print JSON and, when an explicit output path under `telemetry/auto_loop/reports/` is provided, write generated evidence reports there.

Blocked actions:

- commit
- push
- merge
- live trading
- broker execution
- OANDA execution
- Webull execution
- secret access
- credential access
- active queue mutation
- active approval inbox mutation
- active worker registry mutation
- runtime process mutation

Trading Lab remains paper-only.

## Repo-Loop Spine DRY_RUN

Run the connected local spine preview:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopSpine.DRY_RUN.ps1 -GoalText "Create a paper-only Trading Lab latency report scaffold without touching broker or live execution paths"
```

The command writes a generated report under `telemetry/auto_loop/reports/` with:

- packet movement preview
- worker assignment recommendation
- ownership lock preview
- validator execution plan
- approval execution plan
- commit package candidate
- runtime state preview
- resume pointer

## Gated Write Sandbox

Run the local sandbox record builder:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/auto_loop/scripts/Invoke-AiOsRepoLoopGatedWrite.DRY_RUN.ps1 -GoalText "Create a paper-only Trading Lab latency report scaffold without touching broker or live execution paths" -ChangedPaths "apps/trading_lab/trading_lab/results/example.json","automation/trading_lab/example.ps1" -RiskTier HIGH
```

Check latest sandbox state:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/auto_loop/scripts/Get-AiOsAutoLoopStatus.DRY_RUN.ps1 -Latest
```

Read the latest resume pointer:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/auto_loop/scripts/Get-AiOsAutoLoopResume.DRY_RUN.ps1 -Latest
```

The gated-write sandbox creates local packet, lock, approval, validator-run, runtime-snapshot, and resume records under `automation/orchestration/auto_loop/state/`. These records are not active production queues, approval inboxes, worker registries, runtime state, or telemetry runtime authority.

Human approval remains required before APPLY, active state promotion, worker dispatch, commit, push, merge, deployment, trading action, or protected action. The resume record is the continuity bridge for the next supervised packet.
