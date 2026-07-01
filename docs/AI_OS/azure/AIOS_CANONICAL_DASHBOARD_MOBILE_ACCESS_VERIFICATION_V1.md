# AIOS Canonical Dashboard Mobile Access Verification V1

## Purpose

This checklist verifies that the canonical AIOS dashboard is reachable on mobile without mistaking a support preview, a legacy surface, or the raw Azure origin for the actual protected front door.

## Dashboard URL

- Raw Azure origin reference: `https://algotradez-aios.azurewebsites.net`
- Protected hostname: use the Cloudflare Access hostname that the owner actually configured
- Do not assume the raw Azure URL is the Cloudflare front door

## Canonical Expected Surface

- Public root document: `apps/dashboard/dist/index.html`
- Source entry chain: `apps/dashboard/index.html` -> `apps/dashboard/src/main.jsx` -> `apps/dashboard/src/App.jsx` -> `apps/dashboard/src/MinimalOperatorDashboard.jsx`
- Support artifact only: `apps/dashboard/AIOS_STATIC_PREVIEW.html`

## Build Verification

- Run `npm ci` in `apps/dashboard`
- Run `npm run build` in `apps/dashboard`
- Confirm `apps/dashboard/dist/index.html` exists
- Confirm `apps/dashboard/dist/AIOS_STATIC_PREVIEW.html` exists
- Confirm the build does not stage `AIOS_MUSIC_COMPANION.html` as the root document

## Deployment Verification

- Confirm the GitHub Actions workflow deploys `apps/dashboard/dist`
- Confirm the workflow deploy target is `algotradez-aios`
- Confirm the deploy package contains `dist/index.html`
- Confirm the deploy package contains `dist/server.js`
- Confirm the deploy package contains `dist/AIOS_STATIC_PREVIEW.html`

## Azure Auth Check

- App Services -> `algotradez-aios` -> Authentication
- Verify whether unauthenticated requests are blocked
- If unauthenticated requests are blocked, record whether the login path is intentional and mobile-friendly

## Azure Networking Check

- App Services -> `algotradez-aios` -> Networking -> Access restrictions
- Confirm whether mobile/public traffic is intentionally allowed or intentionally blocked
- Record any IP restrictions, deny rules, or private access boundaries

## Cloudflare Access Check

- Zero Trust -> Access -> Applications
- Confirm the dashboard application exists
- Confirm the hostname or route matches the actual protected dashboard hostname
- Confirm the approved identity provider exists
- Confirm the allowed user/email/domain policy is populated
- Confirm mobile login completes
- Confirm the access result is a login challenge, not an unexplained raw 403

## Mobile Pass / Fail Criteria

Pass:

- HTTP 200 on the protected dashboard hostname and the canonical dashboard loads
- or Cloudflare Access presents a mobile-friendly login challenge and the dashboard loads after login

Fail:

- raw unexplained 403
- wrong host
- wrong dashboard surface
- legacy or archived page
- blank/default Azure page
- Cloudflare challenge missing when protection is expected

## Owner Action Checklist

- Check the protected hostname first, not only the raw Azure origin
- Check Cloudflare Zero Trust if a custom hostname is meant to be protected
- Check Azure App Service Authentication and Networking if the raw origin is blocked
- Capture screenshots or notes before changing anything

## No-Secrets Rule

- Do not store passwords, API tokens, publish profiles, recovery codes, or `.env` values in the repo
- Do not paste secret material into reports or verification notes
