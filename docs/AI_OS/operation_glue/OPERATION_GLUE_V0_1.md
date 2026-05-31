# Operation Glue v0.1

Operation Glue v0.1 is a file-based relay loop for AI_OS.

It reduces copy/paste work by turning one goal file into structured worker packet, result, approval inbox, and supervisor summary files.

## What It Does

- Reads a goal intake JSON file.
- Creates a worker packet preview.
- Imports a worker result file.
- Builds an approval inbox state.
- Prints a short supervisor summary with the next safe action.

## What It Does Not Do

- It does not provide full autonomy.
- It does not approve work.
- It does not stage, commit, push, merge, reset, clean, or delete branches.
- It does not touch broker, OANDA, wallet, secrets, deployments, or live trading.

## File Locations

- Goal intake: `control/operation_glue/GOAL_INTAKE.example.json`
- Worker packets: `control/operation_glue/worker_packets/`
- Worker results: `telemetry/operation_glue/worker_results/`
- Approval inbox: `control/operation_glue/APPROVAL_INBOX.json`
- Supervisor summary: `automation/orchestration/glue/Get-AiOsOperationGlueSummary.DRY_RUN.ps1`
- Dashboard sample: `apps/dashboard/mock-data/operation_glue.sample.json`

## Basic Flow

1. Anthony writes or edits one goal intake file.
2. The packet generator creates a worker packet.
3. A worker saves a result report.
4. The result importer normalizes the report.
5. The approval inbox builder creates review items.
6. The supervisor summary shows the latest state and next safe action.

## What Is Still Manual

- Anthony still approves APPLY, protected actions, commits, pushes, PR creation, merges, resets, cleans, and branch deletion.
- Workers still need to run assigned packets.
- Result files still need to be provided by workers or imported from their reports.

## What Is Safer Now

- Goals, packets, results, and approval decisions are separated.
- Protected Action Gate flags are carried forward in the packet.
- Supervisor output stays readable and does not become approval.

## Next APPLY Packet

Connect Operation Glue output to the existing Night Supervisor summary and dashboard state after this v0.1 loop is reviewed and committed.
