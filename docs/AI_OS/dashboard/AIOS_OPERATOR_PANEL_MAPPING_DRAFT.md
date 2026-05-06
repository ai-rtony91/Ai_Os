# AI_OS Operator Panel Mapping Draft

## Purpose

This draft explains how future dashboard panels may map to approved workflow names, validators, and read-only status helpers.

## Mapping Scope

The mapping is conceptual and visibility-only. It helps future dashboard work show which workflow, validator, or helper each operator panel would reference.

## Mapping Non-Scope

No dashboard UI is created.

No buttons execute actions.

All dashboard controls remain conceptual.

No apps launch, no browsers open, no startup settings change, no telemetry collectors run, and no broker or trading actions are enabled.

## Operator Panels

Conceptual panels:

- Repo Health
- Workflow Router
- Morning Brief
- Approval Queue
- Snapshot Boundary
- Report Boundary
- Daily Metrics
- Production Telemetry
- Protected File State

## Panel To Workflow Mapping

Repo Health maps to `REPO_HEALTH`.

Workflow Router maps to registered workflow names in the workflow registry.

Morning Brief maps to Morning Brief state and contract validators.

Approval Queue maps to approval-state and approval-queue validators.

Snapshot Boundary maps to snapshot-history boundary validation.

Report Boundary maps to report-writer boundary documentation and protected report checks.

Daily Metrics maps to daily metrics draft state only.

Production Telemetry maps to future telemetry readiness fields only.

Protected File State maps to protected-file diff checks.

## Panel To Validator Mapping

Panel validators may include:

- `automation\status\Test-AiOsOperatorTelemetryMap.DRY_RUN.ps1`
- `automation\startup\Test-AiOsMorningBriefTextContract.DRY_RUN.ps1`
- `automation\status\Test-AiOsSnapshotHistoryBoundary.DRY_RUN.ps1`
- `automation\status\Test-AiOsApprovalQueueValidator.DRY_RUN.ps1`
- `automation\router\Test-AiOsWorkflowRegistry.DRY_RUN.ps1`

## Risk Labels

LOW means read-only DRY_RUN console-output.

MEDIUM means creates approved files but no git commit.

HIGH means moves, deletes, overwrites, launches, changes settings, touches credentials, or touches trading systems.

BLOCKED means no action until explicit human review.

## Approval Visibility

Future panels should display whether APPLY approval, git checkpoint approval, protected file approval, telemetry approval, report writer approval, or high-risk approval is required.

## Blocked Controls

Blocked controls include app launch, browser open, startup task creation, startup setting changes, report writing, snapshot writing, production telemetry collection, credential access, broker actions, trading actions, and live execution.

## Future Stage 17

Future Stage 17 may propose static dashboard panel data or a DRY_RUN-only dashboard mapping report. It must not create a live dashboard UI or executable controls.
