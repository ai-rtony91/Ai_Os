# OpenAI Codex Night Supervisor Onboarding

Status: onboarding workflow

## Purpose

This workflow closes the OpenAI CLI, Codex, ChatGPT, and Night Supervisor onboarding loop for AI_OS.

It gives the Human Owner one safe readiness command, one packet handoff model, and one shared-checkout collision rule before Codex, Claude, or Night Supervisor work starts.

This document is not a source-of-truth map. Active authority remains:

- `AGENTS.md` for Codex and AI worker behavior.
- `README.md` for human front-door orientation.
- `docs/governance/source-of-truth-map.md` for source-of-truth placement.
- `docs/audits/active-system-map.md` for active-system context.

## Actors

| Actor | Role |
|---|---|
| Human Owner | Approves APPLY, commit, push, merge, protected actions, and live workflow changes. |
| ChatGPT | Plans, explains, drafts packets, and keeps operator-facing summaries compact. |
| OpenAI CLI / Codex | Executes scoped repo tasks from approved packets. |
| Night Supervisor | Observes, reports, queues recommendations, and flags blockers. |
| Claude reviewer | Reviews, refines, or inspects when assigned a bounded lane. |

## Safe Operating Model

AI_OS uses approval-gated execution. No worker, CLI, or supervisor should claim real autonomy.

Default behavior:

- ChatGPT drafts or explains.
- Codex executes only complete tokenized packets or explicit operator commands.
- Claude reviews or implements only assigned lanes.
- Night Supervisor observes, reports, and queues evidence.
- Human Owner approves protected actions.

Night Supervisor is observe/report/queue by default. It may not APPLY, stage, commit, push, merge, launch workers, start loops, mutate queues, or write authority unless a later packet grants exact APPLY authority.

## Startup Order

1. Open the active repo at `C:\Dev\Ai.Os`.
2. Confirm repo state:

```powershell
pwd
git status --short --branch
git diff --cached --name-status
git branch --show-current
git remote -v
```

3. Run the onboarding readiness command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/onboarding/Test-AiOsOpenAiCodexNightSupervisorOnboarding.ps1 -Mode DRY_RUN
```

4. If the wrapper path is preferred:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/bootstrap/Test-AiOsOnboardingReadiness.ps1 -Mode DRY_RUN
```

5. Continue only when the result is `READY` or when `REVIEW_REQUIRED` warnings are understood and accepted for read-only work.

## Handoff Order

1. Human Owner states the goal.
2. ChatGPT converts the goal into a scoped packet when execution is needed.
3. Codex reads `AGENTS.md`, runs preflight, and checks the staged index before mutation.
4. Night Supervisor may review evidence and propose next packets, but does not execute them.
5. Claude reviewer may inspect or refine only the assigned lane.
6. Human Owner approves APPLY, commit, push, merge, or protected actions separately.

## Worktree Separation Rule

Codex, Claude, and Night Supervisor must not silently share dirty branch state.

Rules:

- One worker, one lane, one branch or worktree, one output.
- If the active checkout is dirty, classify the dirty state before starting another worker.
- If two workers need overlapping paths, stop and assign a single owner.
- If a packet targets `main`, verify the current branch and dirty state first.
- Dirty non-main work must be reviewed, preserved, or completed before switching branches.
- Night Supervisor must treat dirty state as a collision risk, not as permission to continue.

## Staged-Index Safety Rule

Before any staging, commit, push, merge, or packet that may mutate files, run:

```powershell
git diff --cached --name-status
```

If output is not empty, stop and classify the staged files. Do not overwrite, unstage, commit, or mix scopes unless the packet explicitly approves that exact action.

## Packet Execution Requirements

Executable Codex packets must include:

- `CODEX-ONLY PROMPT` routing marker or assigned worker type.
- `AI_OS EXECUTION TOKEN`.
- Identity marker, supervisor identity, packet ID, mode, zone, worker identity, lane, approval authority, validator chain, and stop point.
- Branch and worktree resolved after preflight when state is unknown.
- Allowed paths and forbidden paths.
- Mission.
- Validation.
- Final report.
- Stop condition.
- No secrets policy.
- Push/merge/commit authorization only when explicit.

## Night Supervisor Authority Limits

Night Supervisor may:

- Inspect allowed evidence.
- Summarize status.
- Classify blockers.
- Rank next safe actions.
- Draft packet proposals.
- Report queue and readiness state.

Night Supervisor must not:

- Write source files without explicit APPLY authority.
- Stage, commit, push, merge, reset, or switch branches.
- Start itself, workers, loops, daemons, scheduled tasks, or terminals.
- Call OpenAI APIs.
- Touch secrets, credentials, broker routes, live trading, or real order paths.
- Claim background autonomy without evidence.

## OpenAI CLI Readiness Checks

The readiness command verifies local availability only. It never prints secrets and never calls the OpenAI API.

It checks:

- Active repo path.
- Current Git branch.
- `git status --short --branch`.
- Staged index state.
- `openai` command availability.
- `codex` command availability.
- `AGENTS.md`.
- `README.md`.
- This onboarding workflow.
- Night Supervisor script and folder presence.
- `telemetry/night_supervisor` presence.
- Shared-checkout collision risk.

Manual version checks are allowed when needed:

```powershell
openai --version
codex --version
```

Do not paste, print, store, or commit API keys, tokens, session files, `.env` values, or local auth material.

## Readiness Status

| Status | Meaning |
|---|---|
| `READY` | Required repo, index, workflow, and local tool checks passed with no blockers or warnings. |
| `REVIEW_REQUIRED` | No immediate repo blocker, but one or more optional readiness warnings need human review. |
| `BLOCKED` | A required condition failed. Do not start shared-checkout work until fixed. |

The readiness script exits nonzero only for `BLOCKED`.

## No Secrets Policy

Readiness checks may detect whether commands exist. They must not:

- Print secret values.
- Write `.env`.
- Create tokens.
- Call OpenAI APIs.
- Store local session output.
- Commit auth files.

## No Live Trading Policy

This onboarding workflow does not enable live trading.

Live broker execution, real orders, broker credentials, OANDA paths, and uncontrolled automation remain blocked unless a separate explicit Human Owner packet authorizes a bounded paper/live boundary review.

## Troubleshooting

| Symptom | Meaning | Next safe action |
|---|---|---|
| `BLOCKED` with staged files | The Git index already contains work. | Review `git diff --cached --name-status`; do not mix scopes. |
| `BLOCKED` with dirty files | Shared checkout collision risk exists. | Classify dirty files before launching another worker. |
| `BLOCKED` on wrong branch | Packet state does not match repo state. | Stop and resolve branch/worktree alignment. |
| `REVIEW_REQUIRED` with dirty files | Shared checkout collision risk exists. | Classify dirty files before launching another worker. |
| `REVIEW_REQUIRED` for missing `openai` | OpenAI CLI is not available on PATH. | Install or repair CLI separately; do not store secrets in repo. |
| `REVIEW_REQUIRED` for missing `codex` | Codex CLI is not available on PATH. | Repair local Codex install separately. |
| `REVIEW_REQUIRED` for Night Supervisor path | Supervisor files are missing or incomplete. | Run a scoped inspection packet before starting supervisor work. |
| Missing telemetry folder | Runtime evidence path is absent or ignored. | Create only through an approved runtime/onboarding packet if needed. |
| Packet missing identity fields | Work order is incomplete. | Stop and request the missing fields. |

## Operator Commands

Primary readiness:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/onboarding/Test-AiOsOpenAiCodexNightSupervisorOnboarding.ps1 -Mode DRY_RUN
```

JSON stdout:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/onboarding/Test-AiOsOpenAiCodexNightSupervisorOnboarding.ps1 -Mode DRY_RUN -OutputJson
```

Bootstrap wrapper:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/bootstrap/Test-AiOsOnboardingReadiness.ps1 -Mode DRY_RUN
```

Safe next action after `READY`: execute the next approved onboarding closeout, worker handoff, or Night Supervisor DRY_RUN packet from clean `main`.
