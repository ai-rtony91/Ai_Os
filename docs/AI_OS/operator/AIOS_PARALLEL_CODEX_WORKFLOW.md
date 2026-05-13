# AI_OS Parallel Codex Crew Workflow

## Purpose

This workflow defines a supervised operator pattern for running 8 parallel DRY_RUN Codex worker lanes and 1 controlled serial APPLY lane.

The goal is speed with control:

- DRY_RUN workers may run at the same time.
- APPLY work must run one worker at a time.
- Validation must run after each APPLY.
- Commit happens only after the whole batch is clean.
- Push happens once only, after explicit operator approval.

## Worker Lanes

| Worker | Lane | Scope |
| --- | --- | --- |
| 1 | Dashboard UI | `apps/dashboard` |
| 2 | TradingView | `docs/AI_OS/trading_laboratory/tradingview` |
| 3 | TradersPost | `docs/AI_OS/trading_laboratory/traderspost` |
| 4 | Latency | `docs/AI_OS/trading_laboratory/latency` |
| 5 | Validators | `automation/trading_lab` |
| 6 | Reports | `Reports/checkpoints` and `Reports/daily` |
| 7 | Mock Data | `apps/dashboard/mock-data` |
| 8 | Git QC | review/report only |

## Start DRY_RUN Crew

Run from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsParallelDryRunCrew.ps1
```

The launcher opens 8 labeled PowerShell windows. Each window prints:

- worker number
- worker label
- lane
- report target
- DRY_RUN-only stop condition

The Codex launch command is intentionally `UNKNOWN`. Add the approved local Codex command later only after operator confirmation.

## Worker Report Contract

Each worker should produce a JSON report under `Reports/operator/worker-reports/` using the path assigned in `AIOS_PARALLEL_WORKER_REGISTRY.json`.

Required fields:

```json
{
  "worker_id": 1,
  "label": "Dashboard UI",
  "mode": "DRY_RUN_ONLY",
  "files_planned": [],
  "files_deleted": [],
  "validation_commands": [],
  "summary": ""
}
```

## Validate Worker Reports

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
```

The validator checks:

- registry exists
- queue example exists
- exactly 8 workers exist
- Codex command remains `UNKNOWN`
- no overlapping planned files between worker reports
- no protected root files
- no deletes
- validation commands are present

The validator prints clear `PASS` or `FAIL`.

## Controlled APPLY Lane

Run from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsControlledApplyLane.ps1
```

The controlled lane:

- reads `automation/operator/AIOS_CONTROLLED_APPLY_QUEUE.example.json`
- shows approved workers
- asks before each APPLY
- validates after each APPLY
- stops on failure
- asks before explicit git add paths
- asks before git commit
- asks before git push
- writes a final report to `Reports/operator/`

## Git Rules

- Do not use `git add .`.
- Use explicit file paths only.
- Do not commit until the whole batch validates cleanly.
- Do not push until the operator approves one final push.

## Safety Rules

- No protected root files.
- No secrets.
- No external execution connection.
- No live execution.
- No real transactions.
- No commit from the scripts.
- No push from the scripts.

## Standard Batch Validation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```
