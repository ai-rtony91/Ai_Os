# AI_OS System Architecture

Status: canonical summary extracted from legacy `docs/AI_OS`

## Purpose

This document summarizes the current AI_OS architecture from legacy `docs/AI_OS` planning files. It is a compact source for review and cleanup. It does not claim that planned systems are implemented.

## Current Doctrine

AI_OS is a local-first guided operating environment for planning, building, validating, and governing work through human-approved workflows.

Core rules:

- Document infrastructure first. Automate second.
- Default to DRY_RUN until APPLY is explicitly approved.
- Human approval is required before protected edits, commits, pushes, deletes, moves, renames, secrets work, deployment, or trading execution.
- Archive is historical memory, not active runtime.
- Trading Lab remains paper-only. Broker/OANDA/live execution remains blocked.

## Main Layers

| Layer | Path | Current role |
| --- | --- | --- |
| Apps | `apps/` | Active product surfaces, especially `apps/dashboard` and `apps/trading_lab`. |
| Services | `services/` | Backend/service prototypes and future runtime support. Production role needs review. |
| Automation | `automation/` | DRY_RUN/APPLY helpers, orchestration, validators, intake, and operator tooling. |
| Scripts | `scripts/` | Utility scripts that overlap with automation and need consolidation review. |
| Core modules | `aios/` | Python package/code surface. Exact production boundary remains review-sensitive. |
| Schemas | `schemas/` | Shared structured contracts. |
| Docs | `docs/` | Canonical documentation target. Legacy `docs/AI_OS` is being summarized and cleaned. |
| Archive | `archive/` | Historical reports, legacy docs, and retired examples. Not active runtime. |

## Orchestration Canonicalization Status

Recent cleanup established canonical orchestration paths:

- worker registry: `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- worker profiles: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- worker inbox: `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- work packets: `automation/orchestration/work_packets/`
- command queue: `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- approval inbox: `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- approval gate: `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- validators: `automation/orchestration/validators/`
- commit packages: `automation/orchestration/commit_packages/`
- control/status: `automation/orchestration/control/`, `control_summary/`, and `health_summary/`

Legacy root fallback examples were archived to `archive/orchestration_legacy/root_examples/`.

## Planned Ideas

Planned but not proven complete:

- dashboard as an operator command center,
- worker orchestration with packets, approvals, validators, and commit packages,
- runtime summaries and dashboard-facing telemetry,
- secure access model for future hosted or portal use,
- product roadmap with modular AI_OS capabilities,
- paper-only Trading Lab as the first serious vertical.

## Human-Review Items

- Define whether `dispatcher` is an active subsystem name or legacy vocabulary under orchestration.
- Decide which service/runtime components are active versus scaffold.
- Confirm which docs become canonical and which `docs/AI_OS` folders move to archive.
- Keep broker/trading language paper-only until separate governance changes approve otherwise.

## Architecture Risks

- `docs/AI_OS` still contains hundreds of drafts that may conflict with current policy.
- Automation and scripts overlap.
- Runtime state has appeared in reports, examples, and orchestration folders; canonical state boundaries must remain explicit.
- Dashboard drafts can imply controls that are not implemented or not approved.
- Historical broker/OANDA/trading plans must not be interpreted as current capability.
