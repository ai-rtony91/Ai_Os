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
