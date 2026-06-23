# Azure Dashboard Deployment Binding V1

## Scope

Bind the Azure deployment target to the canonical AI_OS dashboard preview in `apps/dashboard` without claiming live operation, broker access, or profit.

## Repository State

- Branch: `azure-dashboard-deployment-binding-v1`
- Base commit: `cfe38364 Add post-trade ledger replay closeout V1 (#1035)`
- Repo state before edits: `main...origin/main` clean

## Dashboard Source

- Source path: `apps/dashboard`
- Canonical preview file: `apps/dashboard/AIOS_STATIC_PREVIEW.html`
- Current deployment package path: `apps/dashboard/dist`
- Package manager: `npm`
- Build command: `npm run build`
- Test command: `npm run test --if-present`

## Azure Target

- Target App Service: `algotradez-aios`
- Target URL reference: `https://algotradez-aios.azurewebsites.net`
- Deployment workflow: `.github/workflows/azure-deploy.yml`

## Binding Change

- `apps/dashboard/vite.config.js` now copies `AIOS_STATIC_PREVIEW.html` to `dist/index.html` so the App Service root URL serves the canonical preview rather than the React shell.
- `.github/workflows/azure-deploy.yml` now verifies that `dist/index.html` matches `dist/AIOS_STATIC_PREVIEW.html` before deploy.

## Cloudflare Access

- Status: not configured in repo
- Public exposure: blocked until Cloudflare Access/login protection is active and externally verified

## Live-Readiness Claims

- Live OANDA credentials used: no
- Real OANDA trade placed: no
- Profit proven: no
- 120% objective achieved: no
- Live operation claimed: no

## Validation

- Repo inspection confirmed the Azure deploy workflow is manual-only and packages `apps/dashboard/dist`.
- Repo inspection confirmed the dashboard preview exists at `apps/dashboard/AIOS_STATIC_PREVIEW.html`.
- Local Node build/test could not be executed in this sandbox because `node` / `npm` process launch fails with `CreateProcessAsUserW failed: 1312`.

## Next Gate

- Verify Cloudflare Access is active in the actual hosting environment.
- Re-run the dashboard build and deploy workflow from the approved Azure/App Service lane.
- Confirm the root URL serves the canonical preview before any public exposure.

