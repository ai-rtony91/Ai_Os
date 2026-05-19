# AI_OS Static React Dashboard Parity DRY_RUN

## Purpose

This DRY_RUN compares the static dashboard preview with the React dashboard app and defines planning-only next steps.

## Compared Files

- `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- `apps/dashboard/css/aios-static-preview.css`
- `apps/dashboard/js/aios-static-preview.js`
- `apps/dashboard/src/App.jsx`
- `apps/dashboard/src/App.css`
- `docs/AI_OS/dashboard/`

## Static Preview Features

- App Dock left sidebar.
- Sidebar toggle.
- Mobile drawer/backdrop concept.
- Safety locks.
- Work Table.
- Assistant guide.
- Tool Registry.
- App Registry.
- Reports/Telemetry/Admin status chips.
- Console output.
- No backend/API/persistence/trading automation messaging.

## React App Features

- Upload Inputs step.
- Review & Confirm step.
- Generate Project step.
- Done step.
- File inputs for White Paper and README.
- Backend fetch to `http://localhost:5050/api/pipeline/run`.
- Alert-based status messages.

## Parity Mismatches

| Area | Static preview | React app | Risk |
| --- | --- | --- | --- |
| Primary purpose | AI_OS cockpit/work table | input upload pipeline | future code targets wrong product |
| Sidebar | present | absent | left navigation requirement not met |
| Mobile drawer | present in static concept | absent | mobile parity gap |
| Safety locks | visible | absent | operator safety not visible |
| Telemetry view | mock/status labels | absent | telemetry display gap |
| Reports/Admin | mock/status labels | absent | operator control gap |
| Backend/API | explicitly blocked in UI text | fetch to local backend | boundary conflict |
| App registry/tool registry | present | absent | app system gap |

## Backend Fetch/API Risk

`apps/dashboard/src/App.jsx` includes a backend fetch. This is not edited in this DRY_RUN, but it should be treated as a REVIEW item before any dashboard parity implementation.

## Sidebar Parity Gap

React does not currently implement the static preview App Dock/sidebar behavior. Future code work should be preceded by a sidebar parity checklist and approved UI code batch.

## Mobile Parity Gap

React does not currently match the static preview's mobile drawer planning. Future code work should test 375px width, drawer open/close, keyboard escape, focus order, and critical alert visibility.

## Telemetry Display Gap

React does not have telemetry panel parity. Any future telemetry display must remain fixture-only/read-only unless telemetry persistence is separately approved.

## Unsafe UI Controls

The React `Run Generation (Backend)` control can trigger a backend call if a backend is running. This conflicts with current static preview no-backend messaging unless explicitly scoped as a separate pipeline tool.

## Recommended Docs-Only Next Steps

- Create canonical dashboard target decision doc.
- Create React/static parity checklist.
- Create backend/API boundary decision doc.
- Create mobile/sidebar parity acceptance criteria.

## Recommended Future Code Steps Not Approved Here

- Align React app with static cockpit if approved.
- Gate or remove backend fetch if React becomes the AI_OS control dashboard.
- Add sidebar/mobile parity only in a separately approved code batch.

## Non-Approval Statement

This DRY_RUN does not edit dashboard code, create UI code, call APIs, create telemetry persistence, register service workers, or implement broker/trading behavior.
