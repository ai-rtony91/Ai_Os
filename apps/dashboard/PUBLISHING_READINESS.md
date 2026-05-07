# AI_OS Dashboard Publishing Readiness

This file is a planning note for future mobile and static-web publishing. It does not publish the dashboard, register a service worker, enable persistence, or activate any backend/API behavior.

## Current Working Dashboard

- `AIOS_STATIC_PREVIEW.html` is the current static dashboard preview.
- `css/aios-static-preview.css` contains the visual system and mobile layout rules.
- `js/aios-static-preview.js` contains local-only mock UI interactions.
- `manifest.webmanifest`, `service-worker.js`, and `icons/` are readiness files only.

## GitHub Pages Path

Future GitHub Pages publishing can serve the `apps/dashboard/` folder as static content if the repository settings and deployment workflow are explicitly approved. The initial preview target is:

`apps/dashboard/AIOS_STATIC_PREVIEW.html`

No backend, API calls, persistence, credentials, broker/trading automation, or live order path are approved by this note.

## Azure Static Web Apps Path

Future Azure Static Web Apps publishing can use `apps/dashboard/` as the static app location only after explicit human approval. Any package installation, workflow file, deployment token, or cloud configuration remains blocked until separately approved.

## PWA Boundary

The service worker is intentionally not registered. The placeholder contains no cache and no fetch handler. Service worker activation, offline caching, push notifications, storage, and persistence require a separate approval gate.

## Safety Boundary

- No backend/API calls.
- No credentials or OpenAI keys.
- No browser profile or private user data access.
- No persistence enabled.
- No startup task.
- No broker/trading automation.
- No live order path.
