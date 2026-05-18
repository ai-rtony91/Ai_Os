# ADR 0001: Document Infrastructure First

Status: accepted for current foundation pass.

Date: 2026-05-18

## Context

AI_OS contains a large and growing set of docs, automation scripts, reports, services, dashboard files, Trading Lab components, work packets, and validation artifacts.

The project needs a stable documentation foundation before adding more automation. Without that foundation, automation can amplify unclear ownership, duplicate docs, weak stop points, or unsafe trading boundaries.

## Decision

AI_OS will document infrastructure before adding automation.

For this foundation pass:

- Create the requested top-level documentation directories under `docs/`.
- Create infrastructure, governance, workflow, audit, and decision records.
- Preserve existing repo structure.
- Do not add Terraform, CloudFormation, CI/CD expansion, deployment tooling, or new automation.
- Do not commit or push.
- Mark unverified facts as UNKNOWN.

## Governance Rule

One role, one purpose, one output, one stop point.

This rule applies to:

- ChatGPT orchestration work.
- Claude Code isolated specialist worker tasks.
- Future Codex worker packs.
- Scripts.
- Validators.
- Reports.
- Workload packs.

## Role Boundary

ChatGPT acts as the orchestration layer. It maintains scope, safety rules, validation, reporting, and stop points.

Claude Code may act as an isolated specialist worker only when bounded by one role, one purpose, one output, one stop point, allowed paths, and blocked paths.

Neither role may bypass human approval for protected actions.

## Consequences

Positive:

- Reduces undocumented automation growth.
- Makes future IaC and tooling candidates reviewable.
- Keeps paper-only Trading Lab boundaries visible.
- Gives future workers a clear stop point.

Tradeoffs:

- Slower initial progress on automation.
- Some existing automation remains unmapped until later reassessment.
- Empty top-level foundation directories may exist locally until populated by later documentation passes.

## Stop Point

Stop after documentation foundation creation and validation. Further work should be a separate docs index consolidation task.
