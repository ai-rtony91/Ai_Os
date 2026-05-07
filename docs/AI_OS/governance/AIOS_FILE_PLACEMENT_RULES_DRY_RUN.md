# AI_OS File Placement Rules DRY_RUN

## Purpose

This DRY_RUN defines placement rules for future Codex prompts, AI agents, scripts, and human work.

## Required Placement Rules

- Docs go in `docs/AI_OS/`.
- Scripts go in `automation/`.
- Generated reports go in `Reports/`.
- Dashboard code goes in `apps/dashboard/`.
- Backend services go in `services/`.
- Broker planning goes in `docs/AI_OS/brokers/`.
- Broker adapter planning goes in `docs/AI_OS/broker_adapters/`.
- Broker code is blocked until later explicit approval.
- Telemetry planning goes in `docs/AI_OS/telemetry/`.
- Telemetry execution is blocked until later explicit approval.
- Legal placeholders go in `docs/AI_OS/legal/`.
- Compliance placeholders go in `docs/AI_OS/compliance/`.
- Monetization planning goes in `docs/AI_OS/monetization/`.
- Mobile/PWA/app-store planning goes in `docs/AI_OS/mobile/`.
- Dashboard requirements go in `docs/AI_OS/dashboard/`.
- Dashboard implementation code goes in `apps/dashboard/`.

## Prompt Rules For Future Codex Work

Every future prompt should state:

- mode: DRY_RUN or APPLY
- approved output folders
- whether protected files may be edited
- whether code may be created
- whether existing files may be modified
- whether generated reports are required
- exact blocked actions

If the prompt does not specify an approved output folder, create a proposal report only.

## Planning vs Code Rules

Planning belongs under `docs/AI_OS/`.

Implementation belongs under approved code roots only:

- `automation/` for scripts
- `apps/dashboard/` for dashboard code
- `services/` for backend service code
- `agent/` for approved agent runtime work

No implementation code should be created inside planning folders unless the file is clearly marked as a non-executable example and the task explicitly approves it.

## Report Rules

Generated reports belong in `Reports/`.

Canonical planning and policy belong in `docs/AI_OS/`.

Reports should not become the only source of truth for governance unless promoted through an approved docs/governance workflow.

## Telemetry Rules

Telemetry schemas, privacy boundaries, consent, and retention planning belong in `docs/AI_OS/telemetry/`.

Telemetry scripts, if later approved, belong in `automation/telemetry/`.

Telemetry collectors, writers, persistence, private data capture, broker data capture, localStorage, sessionStorage, service-worker storage, and remote analytics are blocked until separately approved.

## Broker/OANDA Rules

Broker and OANDA planning belongs in `docs/AI_OS/brokers/`.

Broker adapter interface planning belongs in `docs/AI_OS/broker_adapters/`.

Broker code, OANDA API clients, credentials, account identifiers, `.env`, order paths, webhooks, strategy-to-broker automation, paper execution, practice execution, and live execution are blocked.

## Legal / Compliance / Monetization Rules

Legal placeholders belong in `docs/AI_OS/legal/` and must be marked not legal advice.

Compliance placeholders belong in `docs/AI_OS/compliance/`.

Monetization planning belongs in `docs/AI_OS/monetization/`.

Payment code, billing integration, app-store submission files, analytics SDKs, and final legal claims are blocked until later approval.

## Fail-Closed Rules

- If folder ownership is unclear, do not write.
- If file placement is ambiguous, write a proposal report only.
- If a file already exists, do not overwrite.
- If protected files need edits, stop and request approval.
- If a task asks for secrets, API keys, broker execution, or trading execution, block it.
- If a task asks for live code in a planning folder, block it.
- If a task asks for planning docs in an automation folder, block it.
- If a task would mix generated Reports with canonical source docs, stop and clarify placement.

## Blocked-Action Matrix

| Request type | Default result | Safe alternative |
| --- | --- | --- |
| Secret/API key/credential work | BLOCKED | Write a redacted boundary proposal |
| Broker/OANDA API code | BLOCKED | Write boundary docs under `docs/AI_OS/brokers/` |
| Broker adapter implementation | BLOCKED | Write adapter interface planning under `docs/AI_OS/broker_adapters/` |
| Telemetry writer/collector | BLOCKED | Write schema/privacy docs under `docs/AI_OS/telemetry/` |
| Dashboard code in docs folder | BLOCKED | Write requirements under `docs/AI_OS/dashboard/` |
| Planning docs in automation folder | BLOCKED | Write docs under `docs/AI_OS/` |
| Generated report in source docs | REVIEW | Write report under `Reports/` or promote later |
| Protected root edit | BLOCKED without approval | Request explicit approval and backup plan |
| Move/delete/rename | BLOCKED | Produce DRY_RUN proposal only |

## DRY_RUN Result

These rules are proposed governance docs only. They do not modify protected root files or approve implementation.
