# AI_OS File Placement Rules

Status: canonical governance rule
Source: `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md`

## Purpose

This document defines where AI_OS work belongs so planning, automation, reports, UI code, broker boundaries, telemetry schemas, legal placeholders, and execution surfaces do not get mixed.

## Core Placement Rules

- Canonical governance, workflow, security, concept, architecture, roadmap, and spec summaries belong under `docs/`.
- Legacy AI_OS planning docs may remain under `docs/AI_OS/` until their live references are retired.
- Scripts belong in `automation/`.
- Generated reports belong in `Reports/`.
- Dashboard code belongs in `apps/dashboard/`.
- Backend services belong in `services/`.
- Broker and OANDA planning remain docs-only until separately approved.
- Broker execution code, credentials, account identifiers, order paths, real webhooks, and live trading are blocked.

## Planning Vs Implementation

Planning belongs in documentation folders. Implementation belongs only in approved code roots:

- `automation/` for scripts and validators.
- `apps/dashboard/` for dashboard code and local mock data.
- `services/` for approved backend service code.
- `agent/` for approved agent runtime material.

Do not create executable implementation inside planning folders unless the file is clearly marked as a non-executable example and the task explicitly approves it.

## Reports

Generated reports belong in `Reports/`.

Reports are evidence and history. They do not become the only source of truth for governance unless promoted through an approved docs/governance workflow.

## Telemetry

Telemetry schemas, privacy boundaries, consent, and retention planning are documentation-only until separately approved.

Telemetry scripts, if later approved, belong in `automation/telemetry/`.

Telemetry collectors, writers, persistence, private data capture, broker data capture, browser storage, service-worker storage, and remote analytics are blocked until separately approved.

## Broker And Trading Boundary

Broker and OANDA planning is documentation-only.

Broker code, OANDA API clients, credentials, account identifiers, `.env`, order paths, webhooks, strategy-to-broker automation, paper execution, practice execution, and live execution are blocked until separately approved.

## Legal, Compliance, Monetization

Legal placeholders must stay marked as placeholders and not legal advice.

Compliance planning is documentation-only until reviewed.

Payment code, billing integration, app-store submission files, analytics SDKs, and final legal claims are blocked until later approval.

## Fail-Closed Rules

- If folder ownership is unclear, do not write.
- If file placement is ambiguous, write a proposal report only.
- If a file already exists, do not overwrite it outside explicit scope.
- If protected files need edits, stop and request approval.
- If a task asks for secrets, API keys, broker execution, or trading execution, block it.
- If a task asks for live code in a planning folder, block it.
- If a task asks for planning docs in an automation folder, block it.
- If generated reports and canonical source docs would be mixed, stop and clarify placement.

## Blocked-Action Matrix

| Request type | Default result | Safe alternative |
| --- | --- | --- |
| Secret/API key/credential work | BLOCKED | Write a redacted boundary proposal |
| Broker/OANDA API code | BLOCKED | Write boundary docs only |
| Broker adapter implementation | BLOCKED | Write adapter interface planning only |
| Telemetry writer/collector | BLOCKED | Write schema/privacy docs only |
| Dashboard code in docs folder | BLOCKED | Write requirements/specs instead |
| Planning docs in automation folder | BLOCKED | Write docs under `docs/` |
| Generated report as source policy | REVIEW | Write report under `Reports/` or promote later |
| Protected root edit | BLOCKED without approval | Request explicit approval and backup plan |
| Move/delete/rename | BLOCKED without approval | Produce a DRY_RUN proposal |

