# Phase 189A Agent Runtime Doctrine Review

Branch: `phase-189-high-risk-doctrine-review`
Date: 2026-05-19

## Purpose

Classify the authority of `docs/AI_OS/agent_runtime` and decide whether it can be canonicalized or moved.

## Files Inspected

- `docs/AI_OS/agent_runtime`
- `docs/AI_OS/agent_runtime/README.md`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_QUEUE.json`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_STATUS.json`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_OWNERSHIP_RULES.json`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_TASK_SCHEMA.json`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_GAP_LOG.json`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_VALIDATION_REPORT.json`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_CONTROL_MODEL.md`
- `docs/AI_OS/agent_runtime/AGENT_RUNTIME_TIME_OF_NO_RETURN_RULES.md`
- `docs/AI_OS/agent_runtime/LLM_WORKER_CONNECTION_BOUNDARY.md`
- `docs/AI_OS/agent_runtime/AGENT_WORKFLOW_TASK_LIFECYCLE.json`
- `docs/AI_OS/agent_runtime/AGENT_WORKFLOW_HANDOFF_PACKET_SCHEMA.json`
- `docs/AI_OS/agent_runtime/AGENT_WORKFLOW_BLOCKED_ACTIONS_MATRIX.json`
- `apps/dashboard/mock-data/aios-orchestration-control-room.example.json`
- `automation/agent_runtime/Test-AiOsOrchestrationControlRoom.DRY_RUN.ps1`

## Active References Found

Dashboard mock data:

- `apps/dashboard/mock-data/aios-orchestration-control-room.example.json`
  - References `AGENT_RUNTIME_QUEUE.json`
  - References `AGENT_RUNTIME_STATUS.json`
  - References `AGENT_RUNTIME_OWNERSHIP_RULES.json`
  - References `AGENT_WORKFLOW_TASK_LIFECYCLE.json`
  - References `AGENT_WORKFLOW_BLOCKED_ACTIONS_MATRIX.json`

Agent runtime automation:

- `automation/agent_runtime/Test-AiOsOrchestrationControlRoom.DRY_RUN.ps1`
  - Requires the same five dashboard source references.
- `automation/agent_runtime/Test-AiOsAgentWorkflowReadiness.DRY_RUN.ps1`
  - Requires workflow state machine, lifecycle, handoff schema, runner spec, validator chain, blocked actions matrix, next action router, implementation plan, and Codex summary files.
- `automation/agent_runtime/Test-AiOsAgentRuntimeReadiness.DRY_RUN.ps1`
  - Requires the runtime README, core runtime docs, task schema, queue, status, gap log, ownership rules, validation report, next action, summaries, time-of-no-return rules, Trading Lab bridge, LLM boundary, and non-technical operator README.
- `automation/agent_runtime/Get-AiOsAgentWorkflowSnapshot.DRY_RUN.ps1`
  - Reads `docs\AI_OS\agent_runtime`.
- `automation/agent_runtime/Get-AiOsAgentRuntimeSnapshot.DRY_RUN.ps1`
  - Reads runtime status, queue, and gap log JSON files.

Self-references inside `docs/AI_OS/agent_runtime`:

- Runtime queue and handoff schema identify `docs/AI_OS/agent_runtime` as the active lane.
- Ownership rules grant multiple agents read/write scope for `docs/AI_OS/agent_runtime`.
- Runtime and workflow summaries point to `automation/agent_runtime` validators.

## Classification

`docs/AI_OS/agent_runtime` is an active runtime fixture/model and an active doctrine source.

It is not just legacy draft documentation. The JSON files are used as source references for dashboard mock data, read by snapshot scripts, and required by DRY_RUN validators. The Markdown files also define runtime boundaries, validation expectations, next-action rules, LLM worker boundaries, and high-risk safety constraints.

The folder is also a canonical source candidate, but it should not be canonicalized by moving or repointing references until a dedicated phase updates validators, mock data, snapshot scripts, and ownership rules together.

## Must Remain Active

- Runtime queue, status, gap log, validation report, ownership rules, and task schema JSON files.
- Workflow lifecycle, blocked actions matrix, and handoff packet schema JSON files.
- Control model, workflow state machine, validator chain, runner spec, next-action router, implementation plan, and Codex summaries.
- LLM worker boundary, time-of-no-return rules, Trading Lab bridge, and operator README.
- Active references from `automation/agent_runtime` and dashboard mock data.

## Can Be Canonicalized Later

The following doctrine could be summarized later into `docs/concepts/aios-agent-runtime-concepts.md` without moving the active folder in the same phase:

- Local file-based runtime model.
- One work packet at a time.
- Agent ownership and blocked path checks.
- Required validation before review.
- Summary and next-safe-action rules.
- Local-only dashboard mock fixture relationship.
- No background autonomy, no external LLM install, no broker execution, no live trading, no secrets.

Canonicalization should happen before any archive move, and references should be retired only after the concept doc and any replacement runtime fixture location are reviewed.

## Move-Ready

NO.

Moving `docs/AI_OS/agent_runtime` now would break active validators, snapshot scripts, dashboard mock source references, and self-declared ownership/runtime lanes.

## Recommended Next Action

Create a separate blocker-retirement phase for `automation/agent_runtime` and the dashboard mock fixture. That phase should decide whether to keep `docs/AI_OS/agent_runtime` as the active runtime model or split stable doctrine into `docs/concepts/aios-agent-runtime-concepts.md` while leaving runtime JSON fixtures in an approved active location.

## Validation

- No files moved.
- No references repointed.
- No apps, services, schemas, tests, or `.github` files edited.
- No APPLY scripts run.
- Push: NO
