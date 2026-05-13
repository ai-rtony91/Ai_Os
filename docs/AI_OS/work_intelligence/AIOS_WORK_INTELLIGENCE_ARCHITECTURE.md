# AI_OS Work Intelligence Architecture

## Purpose

AI_OS Work Intelligence is a read-only repo awareness layer. It helps the operator understand current work state, pending tasks, validation readiness, worker queue health, and safe next actions without changing project files.

The first version creates a scanner, validator, configuration file, and example report schemas for a master TODO ledger and daily work snapshot.

## Read-Only Scanner

`Invoke-AiOsWorkIntelligenceScan.ps1` inspects local project evidence and prints a JSON snapshot to the console.

The scanner does not write generated output files. It collects counts and references only:

- current branch
- clean or dirty git state
- latest commit reference
- file and folder counts
- report and checkpoint counts
- validator and automation script counts
- JSON and markdown counts
- TODO and FIXME markers
- worker lane count
- worker report presence
- latest report and checkpoint references

The scanner is intentionally read-only so it can be run frequently without changing the repo or interfering with APPLY approval gates.

## Configuration

`AIOS_WORK_INTELLIGENCE_CONFIG.json` defines:

- scanner mode
- read-only guarantees
- scan roots
- report roots
- checkpoint roots
- worker registry path
- worker report directory
- protected files
- validation commands

The config must keep `mode` set to `READ_ONLY`.

## Master TODO Ledger

`MASTER_TODO_LEDGER.example.json` defines the future canonical task model:

- `task_id`
- `phase`
- `stage`
- `title`
- `status`
- `priority`
- `blocked_reason`
- `depends_on`
- `worker_lane`
- `validation_required`
- `safe_next_action`

Future versions can generate a real ledger from worker reports, unresolved TODO markers, checkpoint notes, daily reports, and validator status.

## Daily Snapshot

`DAILY_WORK_INTELLIGENCE_SNAPSHOT.example.json` defines a compact daily operating summary:

- repo status
- branch
- repo counts
- worker queue health
- validation health
- next safe action
- current focus area

This is meant to become the operator's first read at session start.

## Worker Queue Connection

Work Intelligence connects to the parallel worker system by reading the worker registry and worker report directory. Worker reports can later feed the master TODO ledger after validation confirms:

- no overlapping file ownership
- no protected files
- no delete plans
- validation commands are present

The scanner does not approve APPLY work. It only reports evidence.

## Future Telemetry And BI Integration

Future versions may export read-only snapshots to spreadsheet or BI-friendly formats. Those integrations should remain downstream of the scanner:

1. run read-only scan
2. validate output schema
3. export approved snapshot
4. review in Excel or Power BI

No external integration should bypass local validation or operator approval.

## Safety Boundary

The Work Intelligence layer must not:

- edit protected root files
- perform APPLY work
- stage changes
- commit
- push
- run destructive commands
- activate external execution workflows
- touch secrets or credentials

Its job is to improve visibility, not to automate changes.

## Validation

Run from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
git diff --check
git status --short --branch
```
