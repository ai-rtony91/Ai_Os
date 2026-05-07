# AI_OS Repo Folder Ownership Map

## Purpose

This governance document defines where AI_OS files belong so future agents, Codex tasks, scripts, and humans do not mix planning, automation, reports, UI code, broker boundaries, telemetry schemas, legal placeholders, or execution surfaces.

## Fail-Closed Standard

- If folder ownership is unclear, do not write.
- If file placement is ambiguous, create a proposal report only.
- If a file already exists, do not overwrite.
- If protected files need edits, stop and request approval.
- If a task asks for secrets, API keys, broker execution, or order placement, block it.
- If a task asks for live code in a planning folder, block it.
- If a task asks for planning docs in an automation folder, block it.

## Folder Ownership Table

| Folder path | Owner category | Allowed contents | Blocked contents | Related folders | Risk level | Current status | Recommended correction | Approval needed before writes? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `docs/AI_OS/` | AI_OS planning source | Planning, policies, schemas, architecture, boundaries, requirements, drafts | Secrets, live broker/API execution logic, production executable code unless clearly marked examples | `automation/`, `Reports/`, `apps/dashboard/` | MEDIUM | Active planning root with many subdomains | Keep as canonical planning root; require specific subfolder ownership before writes | YES for new subdomains |
| `automation/` | Automation scripts | PowerShell/Python automation scripts, DRY_RUN/APPLY helpers, validators | Final source-of-truth reports, secrets, unapproved broker execution, protected-file edits without approval | `docs/AI_OS/automation/`, `Reports/` | HIGH | Script root with mirrored docs topics | Require script vs docs separation in prompts | YES |
| `Reports/` | Generated outputs | Daily reports, checkpoint reports, health reports, evidence/session outputs, generated audit outputs | Canonical source policy, implementation code, secrets, live broker controls | `docs/AI_OS/audits/`, `docs/AI_OS/reporting/`, `automation/reporting/` | MEDIUM | Generated output root | Treat as output, not source of truth | YES for generated report writes |
| `apps/dashboard/` | Dashboard UI code | Dashboard app/static preview code, assets, mock data, UI docs local to app | Broker execution, secrets, hardcoded API keys, live trading buttons, telemetry persistence unless approved | `docs/AI_OS/dashboard/`, `docs/AI_OS/mobile/` | HIGH | Active dashboard code/static preview area | Planning belongs in `docs/AI_OS/dashboard/`; code changes require separate approval | YES |
| `services/` | Future backend services | Backend service code after approval | OANDA/broker code before Stage 8 approval, secrets, live execution without approval | `docs/AI_OS/brokers/`, `docs/AI_OS/broker_adapters/` | HIGH | Minimal orchestrator service exists | Block broker/service expansion until approved | YES |
| `agent/` | Agent runtime/instructions | Future agent instructions/planning unless otherwise approved | Autonomous execution logic without approval, secrets, broker execution | `docs/AI_OS/codex/`, `docs/AI_OS/orchestration/` | HIGH | Minimal agent area exists | Keep execution logic blocked until explicit approval | YES |
| `docs/AI_OS/telemetry/` | Telemetry planning | Telemetry planning, schemas, consent, retention, privacy boundaries | Collectors, writers, persistence, broker/private data capture | `automation/telemetry/`, `Reports/` | HIGH | Planning docs plus user/app/business schema folders | Keep schema docs separate from scripts | YES |
| `automation/telemetry/` | Future telemetry scripts | Future telemetry scripts after approval | Data capture without approval, private/broker data, persistence without approval | `docs/AI_OS/telemetry/`, `Reports/` | HIGH | Contains DRY_RUN preview script | Require explicit approval before capture/write behavior | YES |
| `docs/AI_OS/trading_laboratory/` | Review-only trading lab planning | Mock schemas, paper-review templates, review-only signal logs, expectancy notes | Live broker execution, credentials, order paths, broker API calls | `docs/AI_OS/trading/`, `docs/AI_OS/brokers/` | HIGH | Trading lab scaffold exists | Maintain review-only boundary | YES |
| `docs/AI_OS/brokers/` | Broker boundary planning | Broker boundary planning, OANDA planning, no-execution rules | API clients, credentials, execution, orders, webhooks | `docs/AI_OS/broker_adapters/`, `services/` | HIGH | Broker boundary docs exist | Keep Stage 8 docs-only until approval | YES |
| `docs/AI_OS/broker_adapters/` | Adapter interface planning | Adapter boundary and approval gate docs | Adapter implementation, broker classes, API clients, credentials, order submission | `docs/AI_OS/brokers/`, `services/` | HIGH | Adapter planning docs exist | Do not create implementation here | YES |
| `docs/AI_OS/legal/` | Legal placeholders | Legal placeholders only, not legal advice | Final legal claims, enforcement code, secrets | `docs/AI_OS/compliance/`, `docs/AI_OS/monetization/` | MEDIUM | Placeholder docs exist | Keep all text marked placeholder until reviewed | YES |
| `docs/AI_OS/compliance/` | Compliance planning | Compliance checklists, consent/retention drafts, disclaimer placeholders | Enforcement code, app submission files, analytics SDKs | `docs/AI_OS/legal/`, `docs/AI_OS/mobile/` | MEDIUM | Placeholder docs exist | Keep checklists planning-only | YES |
| `docs/AI_OS/monetization/` | Monetization planning | Pricing, packaging, revenue model planning | Payment code, billing integration, app-store payments, user billing collection | `docs/AI_OS/legal/`, `docs/AI_OS/compliance/` | MEDIUM | Placeholder docs exist | Require legal/privacy review before implementation | YES |
| `docs/AI_OS/mobile/` | Mobile/PWA/app-store planning | Mobile readiness, PWA/app-store planning | Production publishing, service-worker registration, app submission | `apps/dashboard/`, `docs/AI_OS/compliance/` | MEDIUM | Mobile planning docs exist | Keep publishing blocked until legal/compliance approval | YES |
| `docs/AI_OS/dashboard/` | Dashboard requirements/planning | Dashboard requirements, layouts, fixture contracts, panel/sidebar planning | Live UI code, broker execution buttons, telemetry persistence | `apps/dashboard/`, `docs/AI_OS/mobile/` | MEDIUM | Large planning area with sidebar subfolder | Use for requirements only; code belongs in `apps/dashboard/` | YES |
| `docs/AI_OS/audits/` | Audit source docs | Audit drafts, decision matrices, ownership reviews | Generated daily reports unless copied as docs, execution code | `Reports/daily/`, `Reports/health/` | MEDIUM | Audit docs exist | Keep audits distinct from generated Reports | YES |
| `docs/AI_OS/governance/` | Governance docs | AI_OS governance, promotion criteria, invalid-data handling, ownership policy | Protected root replacements, secrets, execution code | `AGENTS.md`, `RISK_POLICY.md` | HIGH | Governance docs exist | Use for proposed governance; protected roots need separate approval | YES |

## Source-Of-Truth Folder Map

- Planning and policy source: `docs/AI_OS/`
- Automation scripts: `automation/`
- Generated outputs: `Reports/`
- Dashboard code: `apps/dashboard/`
- Backend services: `services/`
- Agent instructions/runtime: `agent/`
- Telemetry schemas and privacy planning: `docs/AI_OS/telemetry/`
- Telemetry scripts if later approved: `automation/telemetry/`
- Trading lab review-only docs: `docs/AI_OS/trading_laboratory/`
- Broker/OANDA boundary planning: `docs/AI_OS/brokers/`
- Broker adapter planning: `docs/AI_OS/broker_adapters/`
- Legal placeholders: `docs/AI_OS/legal/`
- Compliance placeholders: `docs/AI_OS/compliance/`
- Monetization planning: `docs/AI_OS/monetization/`
- Mobile/PWA/app-store planning: `docs/AI_OS/mobile/`
- Dashboard requirements: `docs/AI_OS/dashboard/`

## Protected Root Boundary

Protected root files such as `README.md`, `AGENTS.md`, `RISK_POLICY.md`, `SOURCE_LOG.md`, `ERROR_LOG.md`, `HALLUCINATION_LOG.md`, `AAR.md`, and `DAILY_REPORT.md` require explicit approval and backup before edits.

## Status

Active governance ownership map for AI_OS non-protected folder placement. This file does not approve automation, code moves, cleanup, protected-file edits, broker execution, telemetry persistence, or Git actions.
