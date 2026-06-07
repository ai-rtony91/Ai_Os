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

## Operator Relief Runtime Bridge v1

Runtime Bridge v1 is the single one-shot pipeline for the existing Operator Relief autonomy components. It reads the oldest `*.json` task from `reports/operator_relief/inbox/`, processes exactly one task, writes one result JSON to `reports/operator_relief/outbox/`, archives the processed inbox item under `reports/operator_relief/archive/processed/`, and exits.

Runtime pipeline:

1. Task Discovery
2. Policy Evaluation
3. Approval Processing
4. Validator Planning
5. Bounded Executor
6. Write Enabled Safe Executor
7. Outbox Result

Allowed runtime behavior:

- process one inbox task per run.
- select the oldest inbox JSON first.
- block duplicate outbox results instead of overwriting.
- write report-only blocked or approval-required evidence to outbox.
- archive only tasks that were processed into an outbox report.
- return `executable=false` in runtime, bridge, executor, and bounded reports.

Still blocked:

- source-file edits.
- telemetry `.jsonl` writes.
- approval queue writes.
- traversal outside inbox, outbox, or archive roots.
- malformed JSON, unresolved placeholders, secrets, broker/API/order-execution paths, and live-trading paths.
- commit, push, merge, rebase, force-push, OpenAI API, recursive Codex, shell passthrough, daemon, watcher, or service start.

Safe command:

```powershell
python -m automation.operator_relief.runtime_bridge
```

Optional explicit inbox task command:

```powershell
python -m automation.operator_relief.runtime_bridge --task-json reports/operator_relief/inbox/task.json
```

Safe validation commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/runtime_bridge.py
git diff --check
git status --short --branch
```

## Operator Relief Auto Commit Push Executor v1

Auto Commit Push Executor v1 is the first bounded closeout executor for high-friction Git steps. It can evaluate whether the current feature-branch work is eligible for exact-file staging, generated-message commit, and push to the current feature branch.

Modes:

- `DRY_RUN`: returns the exact Git commands that would run and executes nothing.
- `APPLY_COMMIT_PUSH`: may run only exact approved `git add -- <files>`, `git commit -m <generated message>`, and `git push origin feature/full-operator-relief-closed-loop-v1` after all hard gates pass.

Hard gates:

- validators must have passed.
- branch must be `feature/full-operator-relief-closed-loop-v1`.
- upstream must be `origin/feature/full-operator-relief-closed-loop-v1`.
- dirty files must exactly match the approved task `changed_paths`.
- every changed file must stay inside task `allowed_paths`.
- forbidden, protected, secret, broker/API, and live-trading paths are blocked.
- merge, rebase, force-push, main-branch push, tag push, broad staging, and unknown dirty files are blocked.

Generated outputs:

- machine-readable JSON report.
- explicit files staged or proposed.
- generated commit message.
- push target.
- captured command stdout/stderr in apply mode.
- `executable=true` only after successful `APPLY_COMMIT_PUSH`.

Still blocked:

- merge, rebase, force-push, main-branch push, tag push, and broad staging.
- protected paths, secrets, broker/API/order execution, and live trading.
- OpenAI API calls, recursive Codex calls, daemons, watchers, and services.

Safe DRY_RUN command:

```powershell
python -m automation.operator_relief.auto_commit_push_executor --task-json reports/operator_relief/inbox/task.json --validators-passed
```

Apply mode is intentionally explicit and must not be used unless the operator has approved that exact closeout action:

```powershell
python -m automation.operator_relief.auto_commit_push_executor --task-json reports/operator_relief/inbox/task.json --validators-passed --mode APPLY_COMMIT_PUSH
```

Safe validation commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/auto_commit_push_executor.py
git diff --check
git status --short --branch
```

## Operator Relief Night Mission Control v1

Night Mission Control v1 turns the remaining night-autonomy red items into bounded local scaffolds. It composes the existing runtime bridge, approval handling, ADB wake rail, and one-shot mission loop without creating unsafe unattended autonomy.

Green in v1:

- mission scheduler scaffold returns next-run metadata.
- phone/Pi approval station scaffold reads bounded local approval decision JSON.
- ADB emergency alert target is planned through the existing Android wake script.
- unattended mission runner processes bounded cycles and stops on safety states.

Mission scheduler behavior:

- plans a next local run time and max cycle count.
- does not register Task Scheduler.
- does not start a background process.
- returns `executable=false`.

Phone/Pi approval station target:

- bounded local input path: `automation/operator_relief/approval_input/`.
- supported decisions: `APPROVE`, `REJECT`, `CONTINUE_MISSION`, `HOLD`.
- traversal, malformed JSON, and unknown decisions are blocked.
- no network listener, open port, or credential storage is created.

ADB emergency alert target:

- existing script path: `tools/android/Send-AiosAdbSosWake.ps1`.
- triggers: approval required, blocked task, validator failure, bridge failure, dirty repo state.
- default mode plans the exact PowerShell command only.
- `APPLY_ADB_ALERT` is required before the ADB alert command may run.
- no Telegram dependency and no credential material required.

Unattended mission runner behavior:

- one-shot only; not a resident runner.
- default `max_cycles=3`.
- calls Runtime Bridge for one task per cycle.
- stops on approval required, blocked task, validator failure, bridge failure, dirty repo, no inbox task, safety violation, or max cycles.
- builds an ADB escalation plan when human attention is required.
- does not commit, push, or merge by default.

Still gated:

- actual recurring registration.
- phone/Pi hosted approval UI or network service.
- ADB alert execution unless explicit `APPLY_ADB_ALERT` is passed.
- commit/push unless the existing Auto Commit Push Executor hard gates pass in its explicit apply mode.
- merge, rebase, force-push, live trading, broker/API/order execution, secrets, OpenAI API calls, recursive Codex calls, daemons, watchers, and services.

Safe commands:

```powershell
python -m automation.operator_relief.unattended_mission_runner
python -m automation.operator_relief.unattended_mission_runner --max-cycles 3
```

Safe validation commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/mission_scheduler.py automation/operator_relief/approval_station.py automation/operator_relief/adb_escalation.py automation/operator_relief/unattended_mission_runner.py
git diff --check
git status --short --branch
```

## Operator Relief Overnight Autonomy Integration v1

Overnight Autonomy Integration v1 connects the night mission CLI hook, commit/push smoke harness, ADB alert smoke harness, local phone/Pi approval station scaffold, overnight scheduler plan, and merge approval gate into one bounded overnight model.

Integrated capabilities:

- `.\aios.ps1 -Mode night-mission -MaxCycles 3` runs the one-shot unattended mission runner.
- Commit/push smoke harness proves exact-file staging and feature-branch push command shape against a generated smoke task or injected runner.
- ADB alert smoke harness plans the existing Android wake script by default and gates actual alert execution behind `APPLY_ADB_ALERT`.
- Phone/Pi approval model remains local file-based JSON under `automation/operator_relief/approval_input/`.
- Scheduler model prints or returns a Windows launch command plan for the night mission CLI.
- Merge approval gate returns machine-readable readiness only; it executes no merge.

Phone/Pi approval model:

- supported decisions: `APPROVE`, `REJECT`, `HOLD`, and existing `CONTINUE_MISSION`.
- the phone or Pi can later write a bounded local JSON decision file.
- no web server, open port, credential storage, or network dependency exists in v1.

ADB escalation model:

- default command plan targets `tools/android/Send-AiosAdbSosWake.ps1`.
- default mode is `DRY_RUN`.
- `APPLY_ADB_ALERT` may call only the existing wake script path.
- the smoke harness reports JSON success or failure.

Scheduler model:

- default mode is `DRY_RUN`.
- planned launch command:

```powershell
.\aios.ps1 -Mode night-mission -MaxCycles 3
```

- `APPLY_SCHEDULE_PLAN` is explicit and gated.
- no daemon, watcher, service, or recurring registration is started by default.

Commit/push smoke model:

- default mode is `DRY_RUN`.
- generated smoke path: `automation/operator_relief/generated_smoke/auto_commit_push_smoke.txt`.
- apply smoke mode requires `APPLY_COMMIT_PUSH_SMOKE` and an explicit command runner in v1 test harnesses.
- it proves exact-file staging and push to `origin/feature/full-operator-relief-closed-loop-v1`.
- merge, rebase, force-push, main push, tag push, and broad staging remain blocked.

Merge gate model:

- statuses: `MERGE_BLOCKED`, `MERGE_REQUIRES_APPROVAL`, `MERGE_READY_FOR_HUMAN`.
- validators and PR readiness are required before human merge readiness.
- no merge, rebase, force-push, or main mutation executes in v1.

Exact safe commands:

```powershell
.\aios.ps1 -Mode night-mission -MaxCycles 3
python -m automation.operator_relief.commit_push_smoke_harness
python -m automation.operator_relief.adb_alert_smoke_harness
python -m automation.operator_relief.overnight_scheduler --max-cycles 3
```

Safe validation commands:

```powershell
python -m pytest tests/operator_relief
python -m py_compile automation/operator_relief/commit_push_smoke_harness.py automation/operator_relief/adb_alert_smoke_harness.py automation/operator_relief/overnight_scheduler.py automation/operator_relief/merge_approval_gate.py
git diff --check
git status --short --branch
```

## Operator Relief Safe CLI Modes v1

Safe CLI Modes v1 exposes the bounded Operator Relief commands through `aios.ps1` so the operator can run the autonomy bridge without remembering Python module names.

Safe modes:

```powershell
.\aios.ps1 -Mode bridge -TaskJson .\reports\operator_relief\inbox\task.json
.\aios.ps1 -Mode runtime-bridge
.\aios.ps1 -Mode night-mission -MaxCycles 3
.\aios.ps1 -Mode commit-push-dry-run -TaskJson .\reports\operator_relief\inbox\task.json
```

Mode routing:

- `bridge` runs only `python -m automation.operator_relief.inbox_outbox_bridge --task-json <resolved path>`.
- `runtime-bridge` runs only `python -m automation.operator_relief.runtime_bridge`.
- `night-mission` runs only `python -m automation.operator_relief.unattended_mission_runner --max-cycles <N>`.
- `commit-push-dry-run` runs only `python -m automation.operator_relief.auto_commit_push_executor --task-json <resolved path> --validators-passed`.

Required parameter behavior:

- `bridge` blocks when `-TaskJson` is missing or not a real file.
- `commit-push-dry-run` blocks when `-TaskJson` is missing or not a real file.
- `night-mission` defaults `-MaxCycles` to `3` and blocks non-positive values.
- `runtime-bridge` requires no task argument and processes the oldest inbox JSON through the runtime bridge.

Blocked capabilities from `aios.ps1` safe modes:

- no commit execution.
- no push execution.
- no merge, rebase, or force-push.
- no OpenAI API call.
- no recursive Codex call.
- no daemon, watcher, or service.
- no shell passthrough.
- no live trading, broker/API/order execution, secrets, or credentials.

Next planned APPLY gates:

- commit/push remains outside `aios.ps1` safe modes until a separate protected-action approval lane authorizes an exact apply closeout.
- ADB alert apply remains gated behind explicit alert mode and is not exposed through these safe modes.
- scheduler registration remains a command plan only unless a separate schedule-apply lane is approved.
- merge remains human-only through the merge approval gate and executes no merge in v1.

Safe validation commands:

```powershell
powershell -NoProfile -Command '$tokens=$null; $errors=$null; $null=[System.Management.Automation.Language.Parser]::ParseFile("aios.ps1",[ref]$tokens,[ref]$errors); if ($errors.Count -gt 0) { $errors | ForEach-Object { $_.Message }; exit 1 } else { "AIOS_PS1_PARSE_OK" }'
python -m pytest tests/operator_relief
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
