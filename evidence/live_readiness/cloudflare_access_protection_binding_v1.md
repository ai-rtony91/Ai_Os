# Cloudflare Access Protection Binding V1

## Canonical Azure URL

`https://algotradez-aios-dnh4djahbne6bzfc.westus2-01.azurewebsites.net`

## Source Deployment Proof

- PR #1036 merged
- commit `573f1fe5ea28e8baa9a73795139416543813327d`
- workflow run `27994154513`
- artifact path `apps/dashboard/dist`
- Azure App Service deployment successful

## Protection Requirement

- Azure dashboard must sit behind Cloudflare Access before public production exposure
- Public unauthenticated access is not accepted as live-ready
- Old Azure website must not be treated as canonical dashboard

## Required Cloudflare Access Checks

- Cloudflare zone identified
- Protected hostname or route defined
- Access application created
- Allowed identity provider configured
- Allowed user/email/domain rule configured
- Login prompt required
- Unauthenticated access denied
- Bypass disabled
- Audit/log visibility noted

## Operator Manual Verification Checklist

- Open protected dashboard URL in normal browser
- Confirm Cloudflare Access login appears
- Authenticate as approved operator
- Confirm dashboard loads after login
- Open incognito/private browser
- Confirm dashboard does not load without authentication
- Verify Azure raw URL exposure decision documented

## Explicit Non-Claims

- No OANDA live credentials used
- No real trade placed
- No profit claim made
- No 120 percent claim made
- No live-operational claim until Access and broker gates pass

## Final Gate Statement

Cloudflare Access Protection Binding V1 is complete only when operator evidence confirms authenticated access is required before dashboard exposure.
