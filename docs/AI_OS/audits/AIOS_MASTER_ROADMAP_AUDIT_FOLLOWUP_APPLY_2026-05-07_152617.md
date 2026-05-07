# AI_OS Master Roadmap Audit Follow-Up APPLY

## Purpose

This APPLY document records the follow-up audit actions from the master roadmap DRY_RUN. It is docs-only and does not implement telemetry, dashboard code, broker/OANDA logic, monetization, compliance systems, or automation.

## Scope Applied

Created an audit follow-up under `docs/AI_OS/audits/` to preserve the risks, missing placeholders, and next safe batch order identified in DRY_RUN.

No protected root file was edited.

## Audit Findings To Carry Forward

### Stage Position

Current next actionable stage is Stage 6 Telemetry + Reporting.

Reason: Stage 1-5 artifacts exist, but telemetry class separation, privacy boundaries, reporting evidence, mobile/compliance placeholders, monetization planning, and OANDA/broker boundaries remain incomplete.

### OANDA Boundary Gap

OANDA belongs in Stage 8 Broker/Execution. Current repo evidence has trading boundary docs and older OANDA references, but no dedicated AI_OS OANDA boundary path exists.

Required future rule: OANDA work starts as documentation only. No API client, credentials, `.env`, account ID, broker token, order placement, webhook, practice trading, paper trading, or live trading is approved by this audit.

### Broker Adapter Placeholder Gap

No approved broker adapter boundary folder or interface planning doc was found in the current AI_OS docs tree.

Future placeholder docs must define blocked actions before any service or adapter folder is considered.

### Telemetry Gap

Existing telemetry docs define broad safety boundaries, but the repo does not yet separate:

- user telemetry
- app telemetry
- business telemetry

Future telemetry drafts must explicitly block credentials, browser profiles, broker data, account identifiers, live market data, live execution data, and private user data.

### Monetization Gap

No dedicated monetization planning folder or docs were found.

Future monetization docs should clarify business model, pricing/packaging, revenue metrics, privacy limits, consent requirements, and app-store constraints before implementation.

### Legal / Compliance Gap

No dedicated legal or compliance placeholder folders were found.

Future docs should include privacy policy placeholder, terms placeholder, telemetry consent placeholder, app-store compliance checklist, trading disclaimer, and monetization compliance boundary.

### Mobile Dashboard Gap

Mobile/static publishing readiness exists in `apps/dashboard/PUBLISHING_READINESS.md`, but dedicated `docs/AI_OS/mobile/` planning was not found.

Future mobile docs should stay planning-only until app-store or PWA work receives separate approval.

### Left Collapsible Sidebar / Panel Gap

Static dashboard preview has left sidebar behavior, and dashboard layout docs exist. A dedicated sidebar requirement path was not found.

Future dashboard planning should define static/React parity, left collapsible sidebar behavior, accessibility, panel grouping, safe default layout, and blocked execution controls.

## Risk Register

| Risk | Severity | Status | Required Next Control |
| --- | --- | --- | --- |
| OANDA implementation before telemetry boundaries | HIGH | BLOCKED | Keep OANDA as Stage 8 docs-only boundary |
| Broker/API/security exposure | HIGH | BLOCKED | No credentials, `.env`, API clients, webhooks, or order paths |
| Telemetry/privacy policy gaps | HIGH | REVIEW | Draft telemetry class schemas and consent/retention rules |
| Monetization without privacy boundary | MEDIUM | REVIEW | Draft monetization boundary docs before business telemetry |
| App-store compliance placeholders missing | MEDIUM | REVIEW | Draft legal/compliance placeholders |
| Dashboard static/React mismatch | MEDIUM | REVIEW | Draft dashboard UI parity plan |
| Duplicate folder ownership confusion | MEDIUM | REVIEW | Clarify docs vs automation vs reports ownership before implementation |
| Protected file overwrite hazard | HIGH | BLOCKED | Continue no protected root edits without backup and approval |

## Future Batch Gate Criteria

### Batch B Gate

Only create empty placeholder folders. No files unless separately approved.

### Batch C Gate

Only create telemetry schema drafts. No writer, collector, persistence, service worker registration, localStorage, API call, broker data, or private data capture.

### Batch D Gate

Only create dashboard UI planning docs. No dashboard code changes.

### Batch E Gate

Only create OANDA/broker boundary placeholder docs. No broker adapter code or credentials.

### Batch F Gate

Only create legal/compliance placeholder docs. No legal claims should be treated as legal advice.

## APPLY Result

Batch A docs-only follow-up applied.

## Next Safe Action

Request approval for Batch B empty placeholder folders only.
