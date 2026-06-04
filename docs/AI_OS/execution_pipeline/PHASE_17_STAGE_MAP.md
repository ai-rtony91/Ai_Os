# Phase 17 Stage Map

Status: DRY_RUN stage map

| Stage | Purpose | Inputs | Outputs | Allowed paths | Forbidden paths | Validators | Stop point | Next dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17.1 Automatic Packet Generator | Turn a local goal into a Codex packet draft. | Goal input fixture. | Packet draft preview. | `docs/AI_OS/execution_pipeline/`, `automation/orchestration/execution_pipeline/`, `schemas/aios/execution_pipeline/` | telemetry, control, locks, approval inbox, memory, Night Supervisor, broker, OANDA, live trading, secrets, `.env` | JSON parse, required fields, forbidden term scan. | Stop before APPLY. | 17.2 |
| 17.2 Worker Router | Assign generated packets to safe lanes. | Packet draft. | Worker assignment preview. | Same Phase 17 paths. | Same forbidden paths. | Lane, branch, worktree, collision, Night Supervisor checks. | Stop before worker launch. | 17.3 |
| 17.3 Validator Dispatcher | Attach validator checklists to packets. | Packet and worker assignment. | Validator chain preview. | Same Phase 17 paths. | Same forbidden paths. | Precheck, JSON, no-write, dirty-tree, forbidden-path, secret, network, trading validators. | Stop before mutation. | 17.4 |
| 17.4 Approval Engine | Generate approval previews without writing runtime approval state. | Validator evidence. | Approval preview. | Same Phase 17 paths. | `automation/orchestration/approval_inbox/` and all forbidden runtime paths. | Approval scope, risk, expiration, human authority checks. | Stop before real approval write. | 17.5 |
| 17.5 Execution Supervisor | Supervise goal-to-clean-state preview. | Packet, worker, validator, approval, commit, clean-state previews. | Supervisor state and final report. | Same Phase 17 paths. | Runtime, telemetry, Night Supervisor, trading, secrets. | Lifecycle, blocked-state, parked-state, clean-state checks. | Stop after preview report. | Future 17.6+ |
