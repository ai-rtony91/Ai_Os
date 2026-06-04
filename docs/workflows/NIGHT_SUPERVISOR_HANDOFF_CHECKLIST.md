# Night Supervisor Handoff Checklist

Status: operator checklist

## Before Night

- Confirm active repo path is `C:\Dev\Ai.Os`.
- Confirm branch and index:

```powershell
git status --short --branch
git diff --cached --name-status
```

- Run onboarding readiness:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/onboarding/Test-AiOsOpenAiCodexNightSupervisorOnboarding.ps1 -Mode DRY_RUN
```

- Confirm no Codex, Claude, or Night Supervisor worker is sharing a dirty checkout silently.
- Confirm pending packets have identity, lane, branch/worktree, allowed paths, forbidden paths, validator chain, final report, and stop point.
- Confirm protected actions require Human Owner approval.
- Confirm live trading, broker, real order, API key, token, and secret paths are out of scope.

## During Night

Night Supervisor may:

- Observe allowed evidence.
- Classify packet and queue state.
- Identify stale, blocked, missing, or unsafe work.
- Rank next safe actions.
- Draft packet proposals for morning review.
- Produce report-only status.

Night Supervisor must not:

- APPLY changes.
- Stage, commit, push, merge, reset, or switch branches.
- Launch workers, terminals, loops, daemons, or scheduled tasks.
- Mutate queues, approvals, ledgers, source files, or authority maps.
- Call OpenAI APIs.
- Touch broker, live trading, real order, credential, token, secret, or `.env` scope.

## Morning Review

Review:

- Final Night Supervisor status.
- Blockers and warnings.
- Queue items needing Human Owner approval.
- Any claimed completed work.
- Any dirty repo or staged-index evidence.
- Any worker collision or lane overlap.
- Any packet proposal before execution.

Before acting, rerun:

```powershell
git status --short --branch
git diff --cached --name-status
```

## Evidence Required For Productive Work Claims

A productive-work claim requires visible evidence:

- GREEN task output or equivalent pass marker.
- Named marker, task ID, or packet ID.
- Validator result evidence.
- Ledger or report evidence.
- Exact changed files when mutation was approved.
- Git status and staged-index state.

No background autonomy claim is accepted without GREEN task output, marker, validator, ledger, and report evidence.

## Blocked Conditions

Stop and report when:

- Repo is dirty and work ownership is unknown.
- Staged index is non-empty before a new task.
- Branch does not match packet state.
- Packet identity, lane, path boundary, validator chain, or stop point is missing.
- Night Supervisor is asked to mutate state without explicit APPLY authority.
- Any live trading, broker, real order, API key, token, credential, or secret scope appears.
- Worker lanes overlap on the same file tree.
- Evidence is stale, contradictory, or missing.

## Log Locations

Known evidence locations include:

- `telemetry/night_supervisor/`
- `telemetry/runtime/`
- `relay/`
- `automation/orchestration/work_packets/`
- `automation/orchestration/night_supervisor/`

Generated runtime evidence is not authority and should not be staged unless a later exact-scope packet approves it.

## Packet Queue Expectations

- Queue items are evidence until Human Owner approves execution.
- DRY_RUN packets inspect and report only.
- APPLY packets edit only approved paths.
- Commit, push, merge, branch deletion, reset, and protected actions require separate approval.
- Night Supervisor may propose queue changes but must not move or clear queue files without explicit APPLY authority.

## Safe Next Action

If readiness is `READY`, run the next approved DRY_RUN packet or prepare an exact APPLY packet for Human Owner review.

If readiness is `REVIEW_REQUIRED`, resolve or accept the listed warnings before overnight work.

If readiness is `BLOCKED`, stop and fix the blocker before launching any worker or supervisor lane.
