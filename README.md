# AI_OS_V2

AI_OS_V2 is a governed AI-assisted operating environment for building, managing, and improving projects through human-readable prompts, scoped worker lanes, canonical authority files, and validation before mutation.

It is not an autonomous replacement for human judgment. It is a structured project operating system: humans set direction, AI workers perform bounded work, governance defines safe behavior, and validation proves what changed.

Trading Lab is the first production vertical. It is paper-only. Live broker execution, real orders, broker credentials, and uncontrolled automation are blocked.

## Current Status

- Active branch: `v2/aios`
- Active repo path: `C:\Users\mylab\OneDrive\GitHub\AI_OS_V2`
- Current focus: front-door documentation, source-of-truth clarity, worker orchestration, telemetry, safe workflows, and paper-only Trading Lab
- Operating model: Phase -> Stage -> Workload Pack -> Task ID -> DRY_RUN/APPLY -> validation -> selective commit
- Commit/push rule: never commit or push unless explicitly approved

## Start Here

For any human contributor, AI assistant, or Codex worker:

1. Read `AGENTS.md`.
2. Confirm the branch with `git status --short --branch`.
3. Read `docs/governance/source-of-truth-map.md`.
4. Read `docs/audits/active-system-map.md`.
5. Identify the existing canonical file that owns the topic.
6. Use DRY_RUN before APPLY unless the prompt explicitly authorizes edits.
7. Edit only the approved files.
8. Validate before reporting completion.

The default posture is: resume from existing authority, do not create a new brain.

## What AI_OS Is

AI_OS is a human-first automation and orchestration platform. It helps convert goals written in normal language into controlled project work:

- inspect the current repo state
- identify ownership and canonical authority
- prevent duplicate documentation and conflicting instructions
- route work to a bounded worker lane
- protect runtime, trading, security, dashboard, and orchestration systems
- run validation before mutation
- report exactly what changed and what remains unknown

The system is designed to make complex work easier to control, not to remove human decision-making.

## What AI_OS Is Not

AI_OS is not:

- AGI, sentience, consciousness, or magical autonomy
- a live trading engine
- a broker execution layer
- a secret manager
- a permission bypass
- a reason to skip validation
- a place for duplicate source-of-truth documents

AI_OS can help build systems. It must not silently become the authority over them.

## Operating Philosophy

AI_OS uses a few strict ideas to keep work safe and legible:

- Existing canonical file first.
- DRY_RUN before APPLY.
- Smallest safe edit first.
- One responsibility per file or folder.
- One worker, one lane, one task, one output.
- Human approval for risky actions.
- No mass delete, move, rename, reset, merge, push, or credential changes without explicit approval.
- Runtime, orchestration, trading, dashboard, telemetry, and protected governance files require clear scope before edits.

Canonical authority matters because AI-assisted projects can drift quickly. When multiple files claim to be the same "brain," workers lose the ability to resume safely. AI_OS prevents that by defining where authority lives and by treating generated reports, archives, drafts, and runtime state as different kinds of evidence.

## DRY_RUN vs APPLY

`DRY_RUN` means inspect, plan, report, and validate without changing files unless the user explicitly approves mutation.

`APPLY` means create or edit only the approved files, then validate and report the result.

Every work session should end with:

- files inspected
- files created
- files changed
- validation result
- git status
- commit status
- push status
- next safe action

## Repository Map

| Path | Role |
|---|---|
| `README.md` | Human front door, quick start, repo orientation, contributor entry point |
| `AGENTS.md` | Required behavior rules for Codex and AI coding workers |
| `docs/governance/` | Source-of-truth maps, ownership, doctrine, file placement rules |
| `docs/workflows/` | Operator workflows, resume flow, APPLY routing, branch/lane rules |
| `docs/security/` | Security posture, approval model, secret prevention, access boundaries |
| `docs/architecture/` | Durable system architecture and long-term AI_OS vision |
| `docs/audits/` | Inspection history, cleanup decisions, active system maps |
| `automation/` | Orchestration scripts, worker routing, approval gates, validators |
| `services/` | Runtime, dispatcher, policy, telemetry, and orchestrator services |
| `scripts/` | Developer and operator helper commands |
| `apps/` | User-facing apps, including dashboard and paper-only Trading Lab |
| `telemetry/` | Runtime state, work ledgers, visibility data, and generated evidence |
| `archive/` | Historical/reference-only material, not active authority |

## Authority Model

The active source-of-truth map is `docs/governance/source-of-truth-map.md`.

The active system dependency map is `docs/audits/active-system-map.md`.

Root authority files such as `README.md`, `AGENTS.md`, `RISK_POLICY.md`, `ARCHITECTURE.md`, `SOURCE_LOG.md`, `ERROR_LOG.md`, `HALLUCINATION_LOG.md`, `AAR.md`, `DAILY_REPORT.md`, and `WHITEPAPER.md` remain protected. Edit them only when explicitly scoped.

If a draft, archive, generated report, legacy CLEAN-era document, or runtime artifact conflicts with active root or governance authority, active authority wins unless the user approves a promotion.

## Worker Model

AI_OS workers are controlled contributors. A worker should know:

- purpose
- branch or worktree
- allowed files
- blocked files
- task ID or workload pack
- validation chain
- expected output
- stop condition

Codex workers must read `AGENTS.md` first. They should not create new docs when an existing canonical file owns the topic. They should not edit the same file tree as another worker. Main control owns merge and push approval.

## Branch Philosophy

Branches are work lanes, not memory storage.

Use a branch for a meaningful work batch. Finish, validate, report, and close the lane before starting unrelated work. Do not rely on a branch to remember context that belongs in canonical docs, workflow docs, ledgers, or audit records.

## Trading Lab Boundary

Trading Lab is the first production vertical, but it remains paper-only.

Allowed when explicitly scoped:

- paper simulation
- backtesting
- latency tracking
- signal validation
- paper route previews
- local-only telemetry

Blocked:

- live broker execution
- real orders
- OANDA integration
- broker credentials or API keys
- LLMs directly in live order execution paths

## Long-Term Direction

AI_OS may eventually help humans build and manage systems such as trading bots, dashboards, automation workflows, orchestration layers, validation pipelines, and operational tools.

The recursive idea is practical: AI_OS itself is also a project. The same governance, validation, workflow, ownership, and orchestration rules used to build another project should eventually help AI_OS organize and improve itself safely.

That means AI_OS should become better at identifying missing ownership, detecting duplicate authority, recommending next safe steps, improving maintainability, and stabilizing its own structure over time.

## Validate A Documentation Edit

For a documentation-only change to this front door, run:

```powershell
git diff --check
git diff -- README.md docs/architecture/AI_OS_V2_WHITEPAPER.md
git status --short --branch
```

Do not commit or push unless the user explicitly approves that action.
