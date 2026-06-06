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
