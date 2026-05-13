# AI_OS Autonomous Snapshot Workflow

## Purpose

The autonomous snapshot workflow extends Work Intelligence with optional local report generation. It can create daily snapshots, append telemetry-friendly metrics, and generate an operator briefing after the scanner builds an in-memory snapshot.

## Default Safety

All write modes are disabled by default:

- `save_to_reports_enabled`: false
- `telemetry_append_enabled`: false
- `operator_briefing_enabled`: false

The scanner remains local-only and must not commit, push, stage files, touch protected root files, or run destructive commands.

## Snapshot Generation

The scanner always builds an in-memory snapshot object. When report saving is explicitly enabled in config, it writes timestamped JSON snapshots under:

```text
Reports/work_intelligence/daily/
```

To write one real daily snapshot without changing the safe default config, run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1 -SaveSnapshot
```

`-SaveSnapshot` writes only the daily JSON snapshot. It does not append telemetry metrics and does not generate the operator briefing.

## Telemetry Metrics

When telemetry append is explicitly enabled, the scanner appends one CSV row to:

```text
Reports/work_intelligence/telemetry/WORK_INTELLIGENCE_METRICS.csv
```

The metrics are intended for future spreadsheet or BI use.

## Operator Briefing

When briefing generation is explicitly enabled, the scanner writes a local markdown briefing under:

```text
Reports/work_intelligence/MASTER_OPERATOR_BRIEFING.md
```

The briefing summarizes repo health, focus area, active phases, worker lanes, blocked items, validation status, next safe action, and recommended next workload.

## Operator Voice Briefing

To write a beginner-readable operator voice briefing without changing default config, run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1 -GenerateBriefing
```

The voice briefing is written under:

```text
Reports/work_intelligence/briefings/
```

`-GenerateBriefing` writes only the plain-language briefing. It does not append telemetry metrics and does not write a daily snapshot unless `-SaveSnapshot` is also used.

## Focus And Security Awareness

The scanner uses local repo evidence to infer a conservative focus area. It checks recent files, latest checkpoints, latest reports, and known subsystem paths.

Allowed focus outputs are:

- `Work Intelligence`
- `Operator Orchestration`
- `Trading Lab`
- `Dashboard UI`
- `UNKNOWN`

When evidence is weak or tied, the scanner returns `UNKNOWN`.

The scanner also emits a `security_warnings` array. Warnings report only the warning type, severity, category, and relative path. The scanner must not print actual secret values and must not include matched secret text.

Security warning evidence is limited to local repo evidence such as `.env` files, API key wording, secret/token/password wording, broker/OANDA/live execution wording, `git add .`, destructive command wording, and protected root file changes from `git status --short`.

Phase 16.7 separates warning noise into explicit classes:

- `secret_material`
- `secret_wording_review`
- `execution_boundary_review`
- `git_safety`
- `destructive_command`
- `protected_file_status`
- `policy_mention`

Severity levels are:

- `HIGH`
- `MEDIUM`
- `LOW`
- `INFO`

Broker, OANDA, and live execution wording belongs to `execution_boundary_review`, not `secret_material`. Protected root file changes belong to `protected_file_status`, not secret scanning. Normal policy-only documentation references are downgraded to `policy_mention` or suppressed after the detail cap so safety docs do not overwhelm actionable warning output.

The snapshot summary includes:

- `security_warning_count`
- `high_risk_count`
- `medium_risk_count`
- `low_risk_count`
- `info_count`
- `suppressed_policy_mentions`

## Autonomous Priority Engine

Phase 16.8 adds lightweight workload ranking using local repo evidence only. The scanner does not invent phases or tasks. When evidence is weak, it keeps the conservative `UNKNOWN` fallback.

The priority engine uses:

- latest report references
- latest checkpoint references
- TODO and FIXME counts
- git clean or dirty state
- validator presence
- report freshness
- worker lane and worker report state
- security warning counts

The snapshot includes:

- `priority_score`
- `urgency_score`
- `dependency_blocked`
- `safe_to_apply`
- `recommended_operator_action`
- `stale_work_detected`
- `stale_work_items`
- `unfinished_phase_count`
- `unfinished_stage_count`
- `blocked_work_count`
- `active_priority_lane`

`safe_to_apply` is `false` when evidence shows a dirty git state, missing validators, protected root modifications, high-risk security warnings, or dependency blocking. It is `true` only when the local evidence supports safe progression.

Stale work detection uses file timestamps only. The scanner can flag stale daily snapshots, operator briefings, reports, and checkpoints when their last-write time is older than the local freshness rule. It does not create stale claims without timestamp evidence.

Recommended operator actions are conservative examples such as:

- `Review latest briefing.`
- `Run next DRY_RUN workload.`
- `Resolve validator failure.`
- `Commit approved work.`
- `Review security warnings.`
- `UNKNOWN`

## Work Queue Draft

Phase 16.9 adds a local `work_queue` array to the scanner output. The queue is a draft for operator review only. It does not APPLY, commit, push, or change repo files.

Queue items are built only from evidence already collected by the scanner:

- TODO count
- FIXME count
- stale work items
- security warnings
- recommended operator action
- dirty git status
- missing worker reports

Each queue item includes:

- `task_id`
- `title`
- `source`
- `priority`
- `status`
- `recommended_action`

Allowed queue statuses are:

- `REVIEW`
- `BLOCKED`
- `READY_FOR_DRY_RUN`
- `UNKNOWN`

When there is no evidence for a queue item, the scanner emits an `UNKNOWN` queue placeholder instead of inventing work.

## Validation

Run from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
git diff --check
git status --short --branch
```
