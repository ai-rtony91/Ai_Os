# AI_OS Runtime Infrastructure

Status: canonical summary extracted from legacy `docs/AI_OS`

## Purpose

This document summarizes runtime and orchestration infrastructure boundaries from legacy `docs/AI_OS/dispatcher`, `docs/AI_OS/orchestration`, recent orchestration cleanup, and infrastructure foundation docs.

## Current Doctrine

Runtime infrastructure must keep state, summaries, reports, and dashboards separate.

Rules:

- Runtime truth must have an explicit owner.
- Summaries do not become editable source of truth.
- Reports/logs/heartbeats should not be active tracked runtime state unless intentionally committed as fixtures.
- Generated outputs belong outside active source paths unless reviewed.
- Dashboard-facing data is display context, not runtime control.

## Canonical Orchestration Paths

Current canonical paths:

- worker registry: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- worker profiles: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- worker inbox: `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- work packets: `automation/orchestration/work_packets/`
- command queue: `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- approval inbox: `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- approval gate: `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- validator chain: `automation/orchestration/validators/`
- commit packages: `automation/orchestration/commit_packages/`
- operator control: `automation/orchestration/control/`
- summaries: `automation/orchestration/control_summary/` and `automation/orchestration/health_summary/`

## Work Packet Model

Work packets are small files under `automation/orchestration/work_packets/`.

Expected states:

- `active`,
- `blocked`,
- `complete`,
- `templates`.

Packets should identify intent, owner lane, assigned worker, repo, branch, status, validator, next action, related files, and notes.

## Validator Model

Validators should answer one question at one stage:

- pre-claim: is the packet safe to assign?
- pre-apply: is the package approved and scoped?
- post-apply: did only approved files change?
- pre-commit-package: is exact-file staging safe?
- recovery-review: is human recovery approval needed?
- recovery-resume: is resume safe?

Most restrictive status wins: `BLOCKED`, then `FAIL`, then `REVIEW_REQUIRED`, then `PASS`.

## Planned/Future Ideas

- Runtime tables and ledgers may eventually become structured local state.
- Dashboard can show status summaries once source-of-truth ownership is stable.
- Worker heartbeat and stale-lock recovery can be made more visible.

## Remaining Risks

- Some v1 example files still have active display scripts.
- Some historical docs still point to old runtime and report paths.
- Report archives contain legacy runtime logs and generated state.
- Automation and scripts overlap.
- If summaries are edited as truth, the system can split into multiple brains.

## Human-Review Items

- Decide whether dispatcher runtime docs remain active or are folded under orchestration.
- Decide whether v1 examples are canonical, fixtures, or archive candidates.
- Decide the future role of `Reports/dispatcher/runtime` now that major reports are archived.
