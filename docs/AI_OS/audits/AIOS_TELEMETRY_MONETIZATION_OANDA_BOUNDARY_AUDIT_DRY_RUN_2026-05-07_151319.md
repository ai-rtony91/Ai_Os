# AI_OS Telemetry + Monetization + OANDA Boundary Audit DRY_RUN

## Scope

Audit current repo evidence for missing telemetry classes, monetization planning, legal/compliance placeholders, mobile dashboard readiness, left collapsible sidebar/panel planning, broker adapter placeholders, and OANDA boundary placement.

## Evidence Summary

Present:

- `docs/AI_OS/telemetry/` planning docs.
- `docs/AI_OS/trading/` execution blocking and trading readiness boundary docs.
- `docs/AI_OS/trading_laboratory/` review-only trading lab scaffold.
- `docs/AI_OS/dashboard/` dashboard/panel/static preview planning docs.
- `apps/dashboard/AIOS_STATIC_PREVIEW.html` and supporting CSS/JS with left sidebar behavior.
- `apps/dashboard/PUBLISHING_READINESS.md` with mobile/static publishing planning.

Missing:

- dedicated OANDA boundary docs/folders.
- broker adapter boundary docs/folders.
- user/app/business telemetry splits.
- monetization folder/docs.
- legal and compliance placeholder folders/docs.
- mobile dashboard docs folder.
- sidebar-specific requirement docs folder.

## Boundary Findings

### Telemetry

Telemetry is currently planning-only. Existing docs block secrets, credentials, broker data, account numbers, live market data, live order paths, and trade execution decisions.

Gap: telemetry is not yet split into user telemetry, app telemetry, and business telemetry. Monetization-related telemetry boundaries are missing.

### Monetization

No dedicated monetization planning folder was found.

Gap: pricing, packaging, revenue metrics, licensing, app-store revenue, and telemetry-for-monetization boundaries are UNKNOWN.

### OANDA / Broker

OANDA appears in `docs/White_Paper.md`, but no dedicated OANDA boundary folder was found under `docs/AI_OS/`.

Gap: OANDA must be isolated as Stage 8 boundary documentation before any adapter or API implementation is considered.

### Legal / Compliance

Privacy credential exclusion checklist exists under security docs.

Gap: no dedicated legal/compliance placeholder folders were found for privacy policy, terms, telemetry consent, app-store compliance, trading disclaimer, or monetization compliance.

### Mobile Dashboard / App Store

`apps/dashboard/PUBLISHING_READINESS.md`, manifest, icon files, and service worker placeholder exist.

Gap: app-store compliance and PWA/mobile readiness should be documented in `docs/AI_OS/mobile/` before publishing work.

### Left Collapsible Sidebar / Panels

Static preview has sidebar implementation and cockpit/panel docs exist.

Gap: no dedicated `docs/AI_OS/dashboard/sidebar/` requirement file was found. React app does not appear aligned with the static preview cockpit.

## Risk Register

| Risk | Severity | Status | Next Safe Action |
| --- | --- | --- | --- |
| Premature OANDA implementation | HIGH | BLOCKED | Create docs-only OANDA boundary first |
| Telemetry privacy gap | HIGH | REVIEW | Split user/app/business telemetry and retention docs |
| App-store compliance gap | MEDIUM | REVIEW | Add compliance placeholders before publishing |
| Monetization data boundary missing | MEDIUM | REVIEW | Add monetization planning docs |
| React/static dashboard mismatch | MEDIUM | REVIEW | Create dashboard parity plan |
| README folder mismatch | MEDIUM | MISMATCH | Document in audit, defer protected-file edit |
| Protected `White_Paper.md` path mismatch | MEDIUM | MISMATCH | Document in audit, defer protected-file edit |
| Duplicate folder ownership confusion | MEDIUM | REVIEW | Add ownership map before more implementation folders |

## Proposed Missing Path Set

Docs-only candidates:

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

Implementation folders such as `services/broker-adapters/` should remain deferred.

## Dry-Run Result

PASS with REVIEW items. No APPLY action is approved by this audit.

## Next Safe Action

Recommended next APPLY batch: Batch A docs only.
