> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# Phase 15.2 Codex Persistent Instruction Layer

Stage 15.2 adds repo-level Codex operating instructions through the root `AGENTS.md` file.

`AGENTS.md` gives Codex workers persistent project guidance before they begin work in the repository. It defines the AI_OS workflow, safety boundaries, validation expectations, and reporting shape that should apply across normal Codex runs.

AI_OS needs this layer now because the project is moving into production intelligence, telemetry, workflow orchestration, and multi-worker coordination. Repeating the same safety rules and Big Pack Mode guidance in every prompt creates drift. A repo-level instruction file makes the baseline rules easier to load consistently.

For multi-worker Codex windows, this file helps each worker start from the same operating model. Workers should see the same paper-only trading boundary, protected path rules, validator expectations, telemetry scope, and selective commit discipline.

This reduces repeated prompting by placing stable instructions in the repository instead of requiring every workload pack to restate all behavior rules. Prompts can still add task-specific allowed paths, blocked paths, and validation commands.

The instruction layer protects Big Pack Mode by making it the default for evolved AI_OS work. It tells workers to prefer one controlled workload per objective, with safety rules, ledgers, validators, and selective commit guidance included.

It also supports telemetry and safer automation. Workers are instructed to report validation results, git status, commit status, push status, and file changes. Those outputs can feed future production heatmaps, stage percentages, worker activity ledgers, and AI-vs-human productivity estimates.

Codex workers must be restarted after `AGENTS.md` changes. Instruction loading happens when a new Codex run or worker session starts, so currently open workers may not pick up the new rules until they restart.
