# AI_OS Risk Mitigation + Dashboard Parity + Ownership DRY_RUN

## A. Executive Summary

Current risk level: HIGH for future large 1Liner APPLY prompts, mainly because the repo now has many adjacent planning, generated report, automation, dashboard, telemetry, broker, and legal/monetization folders with overlapping names.

Highest priority risks:

- Static dashboard preview and React app are not equivalent.
- React app contains a backend `fetch("http://localhost:5050/api/pipeline/run")` path while the static dashboard planning emphasizes no backend/API calls.
- Multiple folder roles overlap: telemetry, reporting, checkpoints, metrics, dashboard, automation, and reports.
- README and AGENTS references include paths not found in the current repo.
- Many folders lack `README_FOLDER_PURPOSE.txt`, increasing wrong-folder write risk.
- Timestamped duplicate draft variants exist and need review before future consolidation.

Immediate safe corrections:

- Add README_FOLDER_PURPOSE coverage in a docs-only/apply-only batch.
- Add a governance index that points to the folder ownership and placement docs.
- Create a dashboard parity planning document before any dashboard code changes.
- Create a duplicate/timestamped document review report before any consolidation.

What must remain blocked:

- Protected root edits without explicit approval and backup.
- Dashboard code changes.
- Telemetry writers, collectors, persistence, localStorage/sessionStorage behavior, and service-worker registration.
- Broker/OANDA code, API clients, tokens, account IDs, order paths, webhooks, paper/practice/live trading.
- Secrets, `.env`, commits, pushes, moves, deletes, renames, and overwrites.

## B. Dashboard Parity Audit

Compared:

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/css/`
- `apps/dashboard/js/`
- `apps/dashboard/src/App.jsx`
- `apps/dashboard/src/App.css`
- `docs/AI_OS/dashboard/`

Static preview features:

- App Dock / left sidebar.
- Sidebar toggle with `aria-expanded`.
- Drawer backdrop.
- Safety locks: no backend/API calls, no persistence/service-worker registration, no broker/trading automation.
- Work Table, App Store, Connectors, Calendar, Notes, Build Queue.
- Reports, Telemetry, Admin, System Status, Diagnostics display chips.
- Tool Registry and App Registry lanes.
- Static console output.
- Mobile and sidebar behavior in static CSS/JS.

React app features:

- Four-step upload wizard: Upload Inputs, Review & Confirm, Generate Project, Done.
- File inputs for White Paper and README.
- Backend pipeline button.
- Backend fetch to `http://localhost:5050/api/pipeline/run`.
- Alert-based success/failure messages.

Mismatches:

- Static preview is a dashboard/work-table cockpit; React app is a file upload pipeline wizard.
- Static preview has sidebar/dock behavior; React app has no equivalent sidebar.
- Static preview includes safety lock language; React app does not display the same safety lock model.
- Static preview includes app/registry/tool lanes; React app does not.
- Static preview has mobile drawer concepts; React app uses a card wizard layout.
- Static preview blocks backend/API behavior; React app has a backend fetch.

Backend fetch/API risks:

- The React app includes a backend call. This may be valid legacy wiring, but it conflicts with current static preview boundaries unless explicitly scoped.
- Any future dashboard parity APPLY must decide whether React should remain a pipeline UI or become the static cockpit parity target.

Sidebar parity gaps:

- Static sidebar exists in static HTML/CSS/JS.
- React sidebar is missing.
- Sidebar grouping docs now exist, but no code parity is approved.

Mobile parity gaps:

- Static preview has mobile responsive/drawer behavior.
- React app mobile behavior is simpler and not cockpit-parity.

Telemetry display gaps:

- Static preview includes telemetry labels only.
- React app has no telemetry panel.
- No telemetry persistence is approved.

Unsafe UI controls:

- Static preview uses buttons labeled diagnostics, telemetry, app store, etc., but static JS presents them as mock/display actions.
- React app `Run Generation (Backend)` is a real backend-triggering control if the backend is running.

Recommended docs-only next steps:

- Create a dashboard parity plan that declares the canonical target.
- Create a backend/API boundary decision doc for the React app.
- Create a sidebar parity checklist.
- Create a mobile parity checklist.

Recommended future code steps, not approved here:

- Decide whether React should be replaced by or aligned to the static preview.
- Remove or gate backend fetch behavior only after separate approval.
- Implement sidebar parity only after a code-specific DRY_RUN.

## C. Ownership Consistency Audit

| Overlap | Current role | Conflict risk | Recommended ownership rule | README_FOLDER_PURPOSE needed | Approval needed before future writes |
| --- | --- | --- | --- | --- | --- |
| `docs/AI_OS/telemetry/` vs `automation/telemetry/` | planning vs script | schemas may be confused with collectors | docs own schemas/privacy; automation owns approved scripts only | YES for both detailed subfolders | YES |
| `Reports/` vs `docs/AI_OS/reporting/` | generated output vs reporting policy | generated output may become canonical by accident | Reports are outputs; docs are source planning | YES for deeper report folders | YES |
| `docs/AI_OS/dashboard/` vs `apps/dashboard/` | requirements vs UI code | planning/code mixing | docs own requirements; apps own code | YES | YES |
| `docs/AI_OS/brokers/` vs `services/` | broker planning vs backend services | broker code may be created too early | broker docs only until Stage 8 approval | YES | YES |
| `docs/AI_OS/broker_adapters/` vs `services/` | adapter planning vs implementation | interface docs may be mistaken for code approval | adapter implementation remains blocked | YES | YES |
| `docs/AI_OS/legal/`, `compliance/`, `monetization/` | placeholders/planning | final legal or billing claims may appear too early | placeholders only; no enforcement/payment code | YES | YES |
| `docs/AI_OS/mobile/` vs `apps/dashboard/manifest.webmanifest` | mobile planning vs app assets | publishing assets may imply app-store readiness | planning docs do not approve publishing | YES | YES |

## D. Folder/File Integrity Gap Register

Detected gaps:

- Many folders lack `README_FOLDER_PURPOSE.txt`, including most `docs/AI_OS/*` subfolders, `apps/dashboard/*`, `automation/*` subfolders, `services/orchestrator`, `agent/runtime`, `Reports/daily`, and `Reports/checkpoints`.
- Timestamped duplicate variants exist for dashboard/mobile/OANDA/adapter and roadmap docs.
- README references `plugins/`, `scripts/`, and `tests/`, but those root folders were not found.
- AGENTS references root `White_Paper.md`, but root `White_Paper.md` was not found; `WHITEPAPER.md` and `docs/White_Paper.md` exist.
- AGENTS references folder-note automation files under `tools/` and a spec file under `docs/AI_OS/system_wizards/`; those exact paths were not found.
- Source-of-truth ambiguity exists between generated `Reports/` and canonical `docs/AI_OS/` planning docs.
- Empty folder tracking risk is reduced because many new folders now contain docs, but future empty folders will not be tracked by Git.

## E. 1Liner Safety Optimization

Required standards for future large Codex prompts:

- Include a required `MODE:` line.
- List exact approved output paths.
- List blocked output paths.
- State whether protected files may be read or edited.
- State overwrite rule explicitly.
- Require duplicate target detection before writing.
- Require `git status --short` before and after.
- Require verification of created files.
- Require fail-closed conditions.
- Split work into staged batches.
- Keep maximum safe APPLY scope to one folder family or one document family.
- Require final report fields: task, files inspected, files created, files changed, errors, unknowns, protected action involved, approval required, next safe action.

Fail-closed conditions:

- ambiguous folder ownership
- existing target file
- protected file edit required
- secret/API/broker request
- live code requested in planning folder
- planning docs requested in automation folder
- dashboard code requested during docs-only batch
- Git action requested without explicit approval

## F. Risk Register

| Risk | Severity | Folder/File | Cause | Impact | Prevention | Next Safe Action |
| --- | --- | --- | --- | --- | --- | --- |
| Wrong folder writes | HIGH | repo-wide | many overlapping names | misplaced source/docs/reports | enforce ownership map | Batch 1 README_FOLDER_PURPOSE coverage |
| Dashboard mismatch | HIGH | `apps/dashboard/AIOS_STATIC_PREVIEW.html`, `apps/dashboard/src/App.jsx` | static cockpit vs React upload wizard | future code may target wrong UI | parity plan before code | Batch 3 dashboard parity planning |
| Telemetry/report duplication | HIGH | `docs/AI_OS/telemetry/`, `automation/telemetry/`, `Reports/` | planning/scripts/output overlap | accidental collectors or reports as policy | placement rules | Batch 2 governance index docs |
| Broker/OANDA premature implementation | HIGH | `docs/AI_OS/brokers/`, `services/` | boundary docs could be mistaken for code approval | live broker/API risk | keep Stage 8 blocked | no implementation batch |
| Protected-file mismatch | HIGH | `AGENTS.md`, `White_Paper.md` | protected reference absent at root | wrong edit target | proposal-only audit | Batch 5 protected mismatch proposal |
| Empty folder tracking | MEDIUM | future empty folders | Git ignores empty dirs | missing intended structure | add purpose docs after approval | Batch 1 |
| Duplicate timestamped docs | MEDIUM | docs variants | no consolidation review yet | source-of-truth confusion | duplicate review only | Batch 4 |
| Stale README/AGENTS references | MEDIUM | `README.md`, `AGENTS.md` | references absent folders/files | operator confusion | protected proposal only | Batch 5 |
| AI agent overreach | HIGH | repo-wide | large 1Liner scope | wrong writes/code/secrets | 1Liner standard | Batch 6 |
| 1Liner scope creep | HIGH | repo-wide | too many actions in one prompt | accidental implementation | max APPLY scope rule | Batch 6 |

## G. Recommended Next Safe APPLY Batches

Do not apply them in this DRY_RUN.

- Batch 1: README_FOLDER_PURPOSE coverage only.
- Batch 2: governance index docs only.
- Batch 3: dashboard parity planning docs only.
- Batch 4: duplicate/timestamped doc review only.
- Batch 5: protected README/AGENTS mismatch proposal only.
- Batch 6: 1Liner template standardization docs only.

Recommended next APPLY batch: Batch 1 README_FOLDER_PURPOSE coverage only.

## Final DRY_RUN Summary

Files created:

- `Reports/daily/AIOS_RISK_MITIGATION_DASHBOARD_PARITY_OWNERSHIP_DRY_RUN_2026-05-07_161043.md`
- `docs/AI_OS/audits/AIOS_DASHBOARD_PARITY_AND_OWNERSHIP_CONSISTENCY_AUDIT_DRY_RUN.md`
- `docs/AI_OS/governance/AIOS_1LINER_SAFETY_OPTIMIZATION_DRY_RUN.md`
- `docs/AI_OS/governance/AIOS_FOLDER_FILE_INTEGRITY_GAP_REGISTER_DRY_RUN.md`
- `docs/AI_OS/dashboard/AIOS_STATIC_REACT_DASHBOARD_PARITY_DRY_RUN.md`

Protected files edited: NO.

Code edited: NO.

Secrets or `.env` touched: NO.

## Next Safe Codex Prompt

```text
APPROVED APPLY BATCH 1 ONLY: Create README_FOLDER_PURPOSE.txt coverage files only for approved folders identified in the latest DRY_RUN gap register. Do not edit existing files. Do not overwrite existing README_FOLDER_PURPOSE.txt files. Do not move, delete, rename, create implementation code, edit protected root files, edit dashboard code, create telemetry writers, create broker/OANDA code, touch secrets/.env, commit, or push. End with a final report and git status --short.
```
