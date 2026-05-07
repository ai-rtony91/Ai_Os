# AI_OS Master Strategic Order Roadmap APPLY

## Purpose

This APPLY document promotes the Batch A docs-only roadmap from the prior DRY_RUN into a stable planning artifact. It defines the strategic order for AI_OS work and keeps OANDA, broker execution, live telemetry, monetization implementation, and legal/compliance activation behind later approval gates.

## Approval Scope

Approved scope:

- Create docs-only roadmap and audit follow-up files.
- Use only `docs/AI_OS/roadmap/` and `docs/AI_OS/audits/`.
- Do not edit protected root files.
- Do not create implementation folders.
- Do not create broker code, telemetry writers, API clients, secrets, `.env` changes, Git commits, pushes, or GitHub actions.

## Current Stage Position

AI_OS is currently positioned at Stage 6 Telemetry + Reporting as the next actionable strategic stage.

Stages 1 through 5 have meaningful foundation, context, scaffold, safety, and dashboard planning evidence, but they still contain REVIEW items. Stage 6 should come before OANDA because telemetry and reporting boundaries are required before broker or execution planning can be safely represented.

## Stage Sequence

| Stage | Strategic Position | Current Status | Next Safe Work |
| --- | --- | --- | --- |
| Stage 1 Foundation/Governance | Base rules and protected-file policy | Present | Keep protected root edits gated |
| Stage 2 Context Persistence | Recovery packets and source-of-truth context | Present | Keep context docs current |
| Stage 3 Scaffold Architecture | Repo folders, ownership, and path roles | Present with mismatch risk | Clarify ownership before implementation folders |
| Stage 4 Operational Safety | DRY_RUN/APPLY gates and execution blocking | Present | Strengthen review-only boundaries |
| Stage 5 Visualization/Human Control | Dashboard and operator control planning | Partial | Reconcile static preview and React app direction |
| Stage 6 Telemetry + Reporting | System/user/app/business evidence planning | Current next stage | Split telemetry classes and privacy rules |
| Stage 7 Signal Intelligence | Signal review, fixtures, and intelligence | Future | Keep review-only until telemetry is stable |
| Stage 8 Broker/Execution | OANDA and broker adapter boundary | Future blocked | Docs-only boundaries after Stage 6 planning |
| Stage 9 Multi-Agent Automation | Coordinated agents and orchestration | Future blocked | Requires telemetry and approval evidence |
| Stage 10 Production Hardening | Security, dependency, rollback, readiness | Future blocked | Requires stable lower stages |
| Stage 11 Autonomous AI_OS | Autonomous local-first AI_OS behavior | Future blocked | Requires explicit human policy change |

## Strategic Order Rules

1. Telemetry and reporting boundaries must precede broker/OANDA adapter work.
2. OANDA belongs in Stage 8 and must start as boundary documentation only.
3. User telemetry, app telemetry, and business telemetry must be separated before monetization metrics are proposed.
4. Monetization planning must not collect private data, broker data, credentials, live market data, or live execution data.
5. Legal and compliance placeholders must exist before mobile/app-store or monetization implementation.
6. Dashboard UI planning must preserve read-only human control until separate approval.
7. Broker adapter placeholders must not imply API clients, credential access, order placement, webhooks, or live trading.

## Approved Batch Plan

### Batch A: Docs Only

Status: Applied by this document.

Allowed output: docs-only roadmap and audit follow-up files under `docs/AI_OS/roadmap/` and `docs/AI_OS/audits/`.

### Batch B: Empty Placeholder Folders Only

Future approval required.

Candidate folders:

- `docs/AI_OS/brokers/`
- `docs/AI_OS/brokers/oanda/`
- `docs/AI_OS/broker_adapters/`
- `docs/AI_OS/telemetry/user/`
- `docs/AI_OS/telemetry/app/`
- `docs/AI_OS/telemetry/business/`
- `docs/AI_OS/monetization/`
- `docs/AI_OS/legal/`
- `docs/AI_OS/compliance/`
- `docs/AI_OS/mobile/`
- `docs/AI_OS/dashboard/sidebar/`

### Batch C: Telemetry Schema Drafts

Future approval required. Create schema drafts only. No telemetry writer, persistence, service worker registration, localStorage, background collector, API call, broker data, or private data capture.

### Batch D: Dashboard UI Planning

Future approval required. Create planning docs only for left collapsible sidebar, panels, mobile dashboard readiness, and static/React dashboard parity. No dashboard code changes.

### Batch E: Broker/OANDA Boundary Placeholders

Future approval required. Create docs-only OANDA and broker adapter boundary placeholders. No API client, credential access, `.env`, broker token, webhook, order placement, or live execution path.

### Batch F: Legal/Compliance Placeholder Docs

Future approval required. Create privacy, terms, telemetry consent, app-store compliance, trading disclaimer, and monetization compliance placeholders.

## Non-Approval Statement

This file does not approve live API code, OANDA integration, broker adapter implementation, broker credential access, `.env` edits, telemetry persistence, telemetry writers, report writers, dashboard production activation, service-worker registration, app-store submission, monetization launch, trading execution, paper trading, live trading, order placement, Git staging, Git commit, Git push, delete, move, rename, overwrite, or protected root file edits.

## Next Safe Action

Request approval for Batch B empty placeholder folders only after reviewing this Batch A result.
