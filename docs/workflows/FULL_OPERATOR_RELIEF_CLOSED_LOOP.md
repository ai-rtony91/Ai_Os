# Full Operator Relief Closed Loop

## Purpose

The Full Operator Relief Closed Loop exists to remove Anthony from routine copy/paste routing between repo state, validator output, packet context, approval needs, and next-action reporting.

The v1 loop is local repo-workflow automation only. It collects state, classifies blockers, records evidence, drafts non-executable packet context, writes approval queue items only when needed, and exits.

## How to Run

```powershell
python -m automation.operator_relief.run_operator_relief_loop
```

## What It Automates

- Collects repo root, branch, git status, remote, dirty state, and authority-file presence.
- Classifies dirty worktrees, branch mismatch, packet defects, validator failures, approval needs, and blocked actions.
- Routes only approved v1 validators.
- Writes append-only evidence to `telemetry/operator_relief/evidence.jsonl`.
- Writes approval-needed items to `approval/operator_relief/pending/`.
- Emits local notifications only when human action is needed.
- Builds non-executable packet drafts with resolved branch context.
- Prints the next safe action.

## What Still Requires Anthony

Anthony still approves APPLY packets, protected-path changes, commits, pushes, PRs, merges, branch cleanup, and any higher-risk workflow promotion.

The loop does not approve its own output. Evidence, notifications, and packet drafts are not authority.

## Notification Triggers

The notification gate emits only for:

- approval needed
- validator failed
- packet invalid
- branch mismatch
- dirty worktree
- protected path touched
- forbidden action requested
- loop failure

Clean routine success is recorded as evidence but does not notify.

## Android ADB SOS Notification Rail

Operator Relief can optionally use the existing Android SOS wake rail:

```text
tools/android/Send-AiosAdbSosWake.ps1
```

The existing script posts the message:

```text
#AIOS_SOS WAKE
```

This is not Telegram. It uses the existing Android ADB notification path.

Enable it with:

```powershell
python -m automation.operator_relief.run_operator_relief_loop --send-adb-sos
```

The loop sends SOS only when Anthony is needed: approval needed, validator failed, packet invalid, branch mismatch, dirty worktree, protected path touched, forbidden action requested, or loop failure.

Clean routine success does not send SOS.

This requires the existing ADB setup and Android target availability. If ADB or the Android target is unavailable, the loop records the failure in `telemetry/operator_relief/notifications.jsonl`, prints a local warning, and continues safely.

## Approval Queue

Approval items are written to:

```text
approval/operator_relief/pending/
```

Each item includes an ID, timestamp, reason, risk level, human-required flag, recommended action, `executable=false`, and source evidence.

## Evidence Ledger

Evidence is appended to:

```text
telemetry/operator_relief/evidence.jsonl
```

The ledger is designed to remove manual log transfer. Anthony should not need to copy branch state, dirty status, validator result, or next-action context into another tool just to ask what happened.

Runtime evidence under `approval/operator_relief/pending/*.json` and `telemetry/operator_relief/*.jsonl` is ignored by Git. The `.gitkeep` files remain trackable so the runtime folders exist without committing generated evidence.

## Packet Drafts

Packet drafts include Codex prompt structure, resolved branch, allowed paths, forbidden paths, validator chain, stop point, and final report format.

Drafts are non-executable until Anthony approves them and replaces the placeholder execution token.

## Full-Auto Policy and Handoff

Operator Relief may add Codex Full-Auto as a future execution engine, but AI_OS remains the routing, approval, evidence, notification, and safety-control layer.

Full-Auto eligibility belongs in `automation/operator_relief/full_auto_policy.py`. The policy returns:

- `FULL_AUTO_ALLOWED`
- `FULL_AUTO_REQUIRES_APPROVAL`
- `FULL_AUTO_BLOCKED`

The policy must consider risk tier, allowed paths, forbidden paths, validator availability, dirty state, branch state, protected path status, live-trading flags, credential flags, broker/API flags, commit permission, and push permission.

Non-executing handoff scaffolding belongs in `automation/operator_relief/full_auto_handoff.py`. A handoff draft must include allowed paths, forbidden paths, validator chain, stop condition, evidence output path, notification trigger rules, and an explicit no-push/no-merge boundary unless separately approved.

The handoff scaffold must not call Codex recursively, start a daemon, commit, push, merge, or bypass `AGENTS.md`.

## Full-Auto Runner DRY_RUN v1

The Full-Auto Runner DRY_RUN v1 is the non-mutating bridge between the policy layer and any future execution lane:

```powershell
python -m automation.operator_relief.run_full_auto_dry_run
```

The runner consumes a real `FullAutoTask` JSON payload from stdin, or from `--task-json` when a concrete task file path is provided. It collects current read-only repo state, calls `evaluate_full_auto_policy()`, and prints one machine-readable JSON final report.

Runner behavior:

- Builds a handoff summary only when policy returns `FULL_AUTO_ALLOWED` or `FULL_AUTO_REQUIRES_APPROVAL`.
- Produces no handoff when policy returns `FULL_AUTO_BLOCKED`.
- Reports `approval_needed=true` when human approval is required.
- Writes no repo files, telemetry files, or approval queue files.
- Invokes no Codex worker, recursive worker, OpenAI API, daemon, commit, push, or merge path.

The report includes policy status, repo state, handoff summary when present, approval/block status, and explicit safety booleans proving the run stayed DRY_RUN-only.

## Operator CLI Hook v1

The main AI_OS control surface exposes the same Full-Auto DRY_RUN runner:

```powershell
.\aios.ps1 -Mode operator-relief -TaskJson .\local_full_auto_task.json
```

The CLI hook prints a DRY_RUN mode banner, shows the exact Python module, verifies that `-TaskJson` points to a real file, then runs only `python -m automation.operator_relief.run_full_auto_dry_run --task-json` with the resolved concrete task file path.

If `-TaskJson` is missing or the file does not exist, the hook prints usage and exits blocked. It does not write telemetry, write approval queue files, commit, push, merge, call OpenAI, call Codex recursively, or start a daemon.

## Operator Relief Autonomy Spine v1

Autonomy Spine v1 is the first bounded in-memory autonomy path for Operator Relief. It is local, DRY_RUN-first, non-live, and non-executable by default.

Autonomy ladder:

1. Discover bounded local task JSON.
2. Reject malformed, placeholder, unsupported, forbidden-path, secret, broker/API, live-trading, or unsafe tasks.
3. Generate a complete non-executable AI_OS packet draft.
4. Build an approved v1 validator plan.
5. Classify approval as `AUTO_ALLOWED`, `APPROVAL_REQUIRED`, or `BLOCKED`.
6. Run approved internal validators only when policy and approval state allow it.
7. Evaluate commit/push recommendation without executing Git.
8. Plan next-run metadata without starting a daemon, service, watcher, cron job, or Task Scheduler job.
9. Process up to a bounded `max_steps` count and stop on the first safety or approval condition.

What is automated now:

- `automation.operator_relief.autonomy_task_discovery` reads explicit task files or the local task input folder.
- `automation.operator_relief.autonomy_packet_generator` builds non-executable packet drafts with required AI_OS fields.
- `automation.operator_relief.autonomy_validator_orchestrator` plans and runs only approved v1 validators from the existing validator router.
- `automation.operator_relief.autonomy_approval_processor` classifies autonomous safety state.
- `automation.operator_relief.autonomy_controller` composes discovery-ready tasks, policy, handoff, packet draft, validators, schedule metadata, and commit/push recommendation into one JSON-safe report.
- `automation.operator_relief.autonomy_loop` processes an in-memory task list with a default `max_steps=3`.
- `automation.operator_relief.autonomy_scheduler` returns schedule metadata only.
- `automation.operator_relief.autonomy_commit_push_gate` returns commit/push recommendation status only.

What remains blocked:

- Live trading, broker/API/order execution, and secrets.
- OpenAI API calls and recursive Codex calls.
- Daemons, background watchers, services, cron, and Task Scheduler registration.
- Shell passthrough and arbitrary command execution.
- Merge, rebase, force-push, commit execution, and push execution.
- Telemetry writes and approval queue writes from the autonomy spine.
- Protected-path autonomy without explicit human approval.

Safe commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/autonomy_task_discovery.py automation/operator_relief/autonomy_packet_generator.py automation/operator_relief/autonomy_validator_orchestrator.py automation/operator_relief/autonomy_approval_processor.py automation/operator_relief/autonomy_commit_push_gate.py automation/operator_relief/autonomy_scheduler.py automation/operator_relief/autonomy_controller.py automation/operator_relief/autonomy_loop.py
git diff --check
git status --short --branch
```

## Operator Relief Bounded Executor v1

Bounded Executor v1 is the first executor facade above the Autonomy Spine. It still does not edit repo files. It can only perform these internal actions after policy, approval, and validator gates pass:

- run approved validator plans.
- build a non-executable handoff summary.
- build a non-executable packet draft.
- build a commit/push recommendation.
- return a final JSON-safe report with `executable=false`.

Default mode is `DRY_RUN`. The only alternate v1 mode is `APPLY_SIMULATION`, which simulates eligibility without mutating files.

Blocked executor capabilities:

- file mutation, telemetry writes, approval queue writes, protected-path mutation.
- OpenAI API, recursive Codex, shell passthrough, daemon, watcher, or service start.
- commit, push, merge, rebase, or force-push execution.
- live trading, broker/API/order execution, secrets, or credentials.

Safe validation commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/bounded_executor.py
git diff --check
git status --short --branch
```

## Operator Relief Write-Enabled Safe Executor v1

Write-Enabled Safe Executor v1 adds the first controlled write capability. It runs the bounded executor and may write exactly one JSON DRY_RUN evidence report under `reports/operator_relief/`.

Allowed write behavior:

- output path must resolve inside `reports/operator_relief/`.
- output file must end in `.json`.
- overwrite is blocked unless an explicit overwrite flag is true.
- blocked or approval-required task reports are not written unless report-only failure evidence is explicitly allowed.
- all reports include `executable=false`.

Still blocked:

- source-file edits.
- telemetry `.jsonl` writes.
- approval queue writes.
- protected-path writes.
- commit, push, merge, rebase, or force-push.
- OpenAI API, recursive Codex, shell passthrough, daemon, watcher, or service start.

Safe validation commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/write_enabled_safe_executor.py
git diff --check
git status --short --branch
```

## Operator Relief Inbox/Outbox CLI Bridge v1

Inbox/Outbox CLI Bridge v1 reduces manual copy/paste routing by reading one `FullAutoTask` JSON from `reports/operator_relief/inbox/`, running the write-enabled safe executor, and writing one machine-readable result JSON to `reports/operator_relief/outbox/`.

Allowed bridge behavior:

- inbox task path must resolve inside `reports/operator_relief/inbox/`.
- inbox task must be a valid `.json` `FullAutoTask`.
- outbox result path must resolve inside `reports/operator_relief/outbox/`.
- overwrite is blocked unless an explicit overwrite flag is true.
- blocked or approval-required task results are written only when report-only failure evidence is explicitly allowed.
- all bridge and executor reports include `executable=false`.

Still blocked:

- traversal outside inbox or outbox.
- malformed JSON, non-json files, unresolved placeholders, secrets, broker/API/order-execution paths, and live-trading paths.
- source-file edits, telemetry `.jsonl` writes, approval queue writes, and protected-path writes.
- commit, push, merge, rebase, force-push, OpenAI API, recursive Codex, shell passthrough, daemon, watcher, or service start.

Safe command:

```powershell
python -m automation.operator_relief.inbox_outbox_bridge --task-json reports/operator_relief/inbox/task.json
.\aios.ps1 -Mode bridge -TaskJson .\reports\operator_relief\inbox\task.json
```

Safe validation commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/inbox_outbox_bridge.py
git diff --check
git status --short --branch
```

## Validator Routing

v1 validators are intentionally narrow:

- `.py` runs `python -m py_compile`
- `.json` runs JSON parse
- `.md` returns manual-review/readback signal
- `.ps1` returns manual-review signal and is not executed

The router does not invent validators or run global test suites.

## Safety Boundaries

- No live trading.
- No broker/API/order execution.
- No credential loading.
- No governance mutation.
- No protected-path APPLY without explicit approval.
- No automatic commit.
- No automatic push.
- No PR creation.
- No merge.
- No recursive Codex call.
- No OpenAI API call.
- No background daemon.

## Future Notification Integration

Future work may add Telegram, desktop notifications, or dashboard notification cards only after a separate approval packet defines boundaries, dependencies, credentials policy, opt-out behavior, and validation.

## Current Stop Point

v1 runs once and exits. It does not watch the repo, start a service, or run as a daemon.
