# AI_OS Dashboard Parity And Ownership Consistency Audit DRY_RUN

## A. Executive Summary

Current risk level: HIGH for large future Codex 1Liner workloads.

Highest priority risks:

- Dashboard static preview and React app are different products right now.
- React app includes backend fetch behavior.
- Folder ownership overlaps can cause wrong-folder writes.
- README/AGENTS references are stale or unresolved.
- Many folders lack `README_FOLDER_PURPOSE.txt`.

Immediate safe corrections:

- Add folder purpose coverage.
- Add governance index docs.
- Add dashboard parity planning docs.
- Review duplicate/timestamped docs before consolidation.

What must remain blocked:

- Protected root edits, dashboard code edits, broker/OANDA implementation, telemetry writers/collectors, persistence, secrets, `.env`, commits, pushes, moves, deletes, renames, and overwrites.

## B. Dashboard Parity Audit

Static preview source:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/css/aios-static-preview.css`
- `apps/dashboard/js/aios-static-preview.js`

React source:

- `apps/dashboard/src/App.jsx`
- `apps/dashboard/src/App.css`

Planning source:

- `docs/AI_OS/dashboard/`

Static preview features:

- App Dock.
- Left collapsible/sidebar drawer behavior.
- Safety locks.
- Work Table.
- Tool Registry.
- App Registry.
- Reports, Telemetry, Admin status chips.
- Static console.
- Mobile/PWA metadata and manifest references.

React app features:

- Upload/review/generate/done wizard.
- File selection for white paper and README.
- Backend pipeline run button.
- Fetch to local backend.
- Alert notifications.

Mismatches:

- Sidebar absent in React app.
- Static Work Table absent in React app.
- App Dock and app registry absent in React app.
- Safety lock model absent in React app.
- Telemetry/report/admin panels absent in React app.
- Static preview says no backend/API calls; React app calls a backend.

Recommended docs-only next steps:

- Define canonical dashboard target.
- Define whether React should follow static preview or remain a separate pipeline tool.
- Create sidebar parity checklist.
- Create backend/API boundary decision draft.

Recommended future code steps, not approved:

- Gate or remove backend fetch if React becomes static cockpit.
- Port App Dock/sidebar into React if React becomes the canonical dashboard.
- Add fixture-only telemetry display if approved.

## C. Ownership Consistency Audit

| Folder path | Current role | Conflict risk | Recommended ownership rule | README_FOLDER_PURPOSE needed | Approval needed before future writes |
| --- | --- | --- | --- | --- | --- |
| `docs/AI_OS/telemetry/` | telemetry schemas/planning | confused with collectors | docs only | YES | YES |
| `automation/telemetry/` | future telemetry scripts | scripts may collect data too soon | scripts only after approval | YES | YES |
| `Reports/` | generated outputs | mistaken as source policy | generated output only | partial, more needed | YES |
| `docs/AI_OS/dashboard/` | dashboard planning | confused with UI code | requirements only | YES | YES |
| `apps/dashboard/` | dashboard code | code may be edited in docs-only batch | code only with approval | YES | YES |
| `docs/AI_OS/brokers/` | broker planning | mistaken for implementation approval | boundary docs only | YES | YES |
| `docs/AI_OS/broker_adapters/` | adapter planning | mistaken for code approval | interface planning only | YES | YES |
| `docs/AI_OS/legal/` | legal placeholders | mistaken for final legal text | placeholders only | YES | YES |
| `docs/AI_OS/compliance/` | compliance placeholders | mistaken for enforcement | checklist/docs only | YES | YES |
| `docs/AI_OS/monetization/` | monetization planning | mistaken for billing approval | planning only | YES | YES |
| `docs/AI_OS/mobile/` | mobile/PWA planning | mistaken for publishing approval | planning only | YES | YES |

## D. Folder/File Integrity Gap Register

Key gaps:

- Many inspected folders lack `README_FOLDER_PURPOSE.txt`.
- Several timestamped variants exist next to non-timestamped drafts.
- README references root folders not found: `plugins/`, `scripts/`, `tests/`.
- AGENTS references root `White_Paper.md`, which was not found.
- AGENTS references folder automation paths under `tools/` and a spec path not found.
- Source-of-truth ambiguity exists between `Reports/` and `docs/AI_OS/`.

## E. 1Liner Safety Optimization

Future 1Liners should require:

- one mode line
- exact approved paths
- exact blocked paths/actions
- duplicate target precheck
- protected-file policy
- no-overwrite statement
- git status before and after
- verification table
- batch separation
- mandatory final report

## F. Risk Register

| Risk | Severity | Folder/File | Cause | Impact | Prevention | Next Safe Action |
| --- | --- | --- | --- | --- | --- | --- |
| Wrong folder writes | HIGH | repo-wide | overlapping folder names | misplaced docs/code/reports | folder purpose coverage | Batch 1 |
| Dashboard mismatch | HIGH | dashboard files | static vs React divergence | wrong implementation target | parity doc | Batch 3 |
| Telemetry/report duplication | HIGH | telemetry/reporting folders | planning/script/output overlap | accidental persistence | governance index | Batch 2 |
| Broker/OANDA premature implementation | HIGH | broker/services | boundary docs imply code | execution risk | block implementation | no code batch |
| Protected-file mismatch | HIGH | AGENTS/README | stale references | wrong edits | proposal only | Batch 5 |
| Duplicate timestamped docs | MEDIUM | docs | repeated variants | source ambiguity | review report | Batch 4 |
| 1Liner scope creep | HIGH | repo-wide | broad APPLY scope | overreach | 1Liner standard | Batch 6 |

## G. Recommended Next Safe APPLY Batches

1. README_FOLDER_PURPOSE coverage only.
2. Governance index docs only.
3. Dashboard parity planning docs only.
4. Duplicate/timestamped doc review only.
5. Protected README/AGENTS mismatch proposal only.
6. 1Liner template standardization docs only.

## DRY_RUN Result

PASS with REVIEW items. No implementation is approved.
