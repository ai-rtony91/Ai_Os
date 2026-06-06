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

## Packet Drafts

Packet drafts include Codex prompt structure, resolved branch, allowed paths, forbidden paths, validator chain, stop point, and final report format.

Drafts are non-executable until Anthony approves them and replaces the placeholder execution token.

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
