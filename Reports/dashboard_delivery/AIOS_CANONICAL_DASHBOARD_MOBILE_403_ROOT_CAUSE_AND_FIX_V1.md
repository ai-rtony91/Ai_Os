# AIOS Canonical Dashboard Mobile 403 Root Cause And Fix V1

## 1. STATUS

REPO_FIX_APPLIED_PENDING_DEPLOY

## 2. OWNER FAILURE

- URL: `https://algotradez-aios.azurewebsites.net`
- Mobile result: owner observed HTTP `403`
- Current public/mobile access confirmed?: `no`
- Note: the sandbox could not directly probe the URL because outbound socket access to `algotradez-aios.azurewebsites.net:443` was blocked, so live response headers were not available from this run.

## 3. CANONICAL DASHBOARD TARGET

- Canonical source path: `apps/dashboard/`
- Canonical source entry chain: `apps/dashboard/index.html` -> `apps/dashboard/src/main.jsx` -> `apps/dashboard/src/App.jsx` -> `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- Canonical root output path: `apps/dashboard/dist/index.html`
- Deployment package path: `apps/dashboard/dist`
- Workflow path: `.github/workflows/azure-deploy.yml`
- Target app service: `algotradez-aios`
- Dashboard URL: `https://algotradez-aios.azurewebsites.net`
- Confidence: `HIGH` for the repo-side canonical root, `MEDIUM` for the external access path because Cloudflare hostname/policy state is unresolved in repo evidence

## 4. NON-CANONICAL SURFACES EXCLUDED

- `apps/dashboard/AIOS_MUSIC_COMPANION.html`
- archived dashboard files
- report-only dashboard pages
- local-only preview surfaces that are not the published root
- static preview pages used as support artifacts rather than the root document
- unrelated React shell variants that do not match the active `index.html -> main.jsx -> App.jsx -> MinimalOperatorDashboard.jsx` chain

## 5. REPO BUILD FINDINGS

- Package manager: `npm`
- Build command: `npm run build`
- Output directory: `apps/dashboard/dist`
- Root file behavior: `dist/index.html` is emitted by the build and is the public entry document
- Static preview copy behavior: `vite.config.js` copies `AIOS_STATIC_PREVIEW.html` and other support files into `dist`, but it does not rewrite the root document to be the static preview
- Build validation status: `PASS`
- Additional validation:
  - `npm ci` succeeded in `apps/dashboard`
  - `npm run test --if-present` completed with no reported failures
  - `Test-Path apps/dashboard/dist/index.html` returned `True`
  - `Test-Path apps/dashboard/dist/AIOS_STATIC_PREVIEW.html` returned `True`

## 6. AZURE WORKFLOW FINDINGS

- Workflow file: `.github/workflows/azure-deploy.yml`
- Trigger type: `workflow_dispatch` only
- Deployed package path: `apps/dashboard/dist`
- Target app/service reference: `algotradez-aios`
- Validation checks:
  - checks `apps/dashboard/package.json`
  - checks `apps/dashboard/index.html`
  - checks `apps/dashboard/package-lock.json`
  - checks `apps/dashboard/dist/server.js`
  - checks `apps/dashboard/dist/AIOS_STATIC_PREVIEW.html`
  - checks `apps/dashboard/dist/index.html`
  - checks `apps/dashboard/dist/css`, `dist/js`, `dist/assets`, and `dist/mock-data`
- Secrets used by workflow, names only:
  - `AZUREAPPSERVICE_PUBLISHPROFILE_ALGOTRADEZ_AIOS`
- Repo-correctness:
  - Correct after removing the stale equality check that treated `AIOS_STATIC_PREVIEW.html` as the root document
  - Still manual-only and still scoped to `apps/dashboard/dist`

## 7. PUBLIC HTTP FINDINGS

- HEAD status: not directly verifiable from this sandbox because the outbound probe failed with a socket permission error
- GET status: not directly verifiable from this sandbox because the outbound probe failed with a socket permission error
- Response headers that help classify 403: unavailable from this run
- Classification:
  - owner-observed mobile `403` is real, but this run could not capture the live HTTP headers
  - repo evidence does not show Cloudflare headers, a Cloudflare Access app, or a protected hostname bound to this raw Azure URL
  - the raw Azure URL is therefore not proven to be the Cloudflare front door
- Mobile-specific issue confirmed?: `no`, because the live host headers were not captured and Cloudflare/mobile policy state is unresolved

## 8. CLOUDFLARE / AZURE ACCESS FINDINGS

- Cloudflare Access evidence:
  - `Reports/security/login/AIOS_CLOUDFLARE_ACCESS_DASHBOARD_ACTION_PREP.md` leaves the Cloudflare account identity, zone/domain, public hostname, and recovery details unresolved
  - `Reports/security/login/AIOS_CLOUDFLARE_ACCESS_DASHBOARD_ACTION_PREP.json` also leaves the public hostname and access inputs unresolved
  - no repo evidence shows a created Cloudflare Access application, allowed email list, or identity policy
- Azure Authentication evidence:
  - no repo evidence shows Azure Auth / Easy Auth configured for this dashboard
- Azure Networking / Access Restrictions evidence:
  - no repo evidence shows access restriction rules for this dashboard
- Repo evidence on public exposure:
  - `evidence/live_readiness/azure_dashboard_deployment_binding_v1.md` says public exposure is blocked until Cloudflare Access/login protection is active and externally verified
  - `docs/deployment/CLOUDFLARE_ACCESS_PROTECTION_BINDING_V1.md` says the Azure origin should sit behind a dedicated protected hostname and not the raw Azure URL
- Mobile login path:
  - unknown in repo evidence
  - no allowed email/provider policy is proven in repo evidence

### Cloudflare-specific classification

- `CLOUDFLARE_NOT_CONFIGURED`
- `CLOUDFLARE_NOT_IN_PATH_FOR_AZUREWEBSITES_URL`
- `AZURE_RAW_URL_BYPASSES_CLOUDFLARE`
- `OWNER_TESTING_WRONG_HOSTNAME`

## 9. ROOT CAUSE CLASSIFICATION

- `DEPLOYMENT_NOT_RUN_OR_NOT_VERIFIED`
- `EXTERNAL_PORTAL_ACTION_REQUIRED`
- `UNKNOWN_NEEDS_PORTAL_CHECK`

## 10. REPO FIXES APPLIED

- `.github/workflows/azure-deploy.yml`
  - removed the stale `cmp` assertion that incorrectly treated `AIOS_STATIC_PREVIEW.html` as the root document
  - preserved the deployed package path `apps/dashboard/dist`
  - preserved the manual-only trigger and the existing artifact validation
- `docs/AI_OS/azure/AIOS_CANONICAL_DASHBOARD_MOBILE_ACCESS_VERIFICATION_V1.md`
  - added a mobile verification checklist that distinguishes the public root document from the static preview artifact and calls out the Cloudflare front-door check

## 11. OWNER ACTION REQUIRED

### Azure Portal

- App Services -> `algotradez-aios` -> Overview -> confirm app is running
- App Services -> `algotradez-aios` -> Deployment Center -> confirm latest GitHub deployment succeeded
- App Services -> `algotradez-aios` -> Authentication -> check whether unauthenticated requests are blocked
- App Services -> `algotradez-aios` -> Networking -> Access restrictions -> check mobile IP/public restrictions
- App Services -> `algotradez-aios` -> Configuration -> confirm runtime/static package settings if applicable

### Cloudflare

- Zero Trust -> Access -> Applications -> confirm dashboard app exists
- confirm hostname / path matches the protected dashboard hostname, not only the raw Azure URL
- confirm owner mobile identity/email is allowed
- confirm login challenge works on mobile
- confirm the denial is not a raw unexplained 403

### GitHub

- Actions -> Azure deploy workflow -> confirm latest run
- confirm artifact/build contains `dist/index.html`
- confirm deploy target is `algotradez-aios`

## 12. MOBILE VERIFICATION CHECKLIST

Pass conditions:

- HTTP 200 and canonical dashboard loads
- or a mobile-compatible Cloudflare/Azure login challenge loads and grants access after login

Fail conditions:

- raw unexplained 403
- wrong dashboard surface
- music companion instead of the canonical dashboard
- legacy page
- blank/default Azure page
- root route missing

## 13. SECURITY STANCE

- Do not remove protection blindly.
- Public access requires explicit owner approval.
- Protected mobile access is acceptable if login works.
- Raw 403 without an intended login path is not acceptable.

## 14. FINAL NEXT ACTION

Open Cloudflare Zero Trust -> Access -> Applications, verify the protected hostname and allowed identity policy, then re-test the correct dashboard hostname from mobile after the next Azure deploy.
