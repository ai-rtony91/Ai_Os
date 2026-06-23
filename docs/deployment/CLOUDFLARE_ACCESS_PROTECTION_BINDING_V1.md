# Cloudflare Access Protection Binding V1

## Strict Wording

- AIOS is in final governed live-readiness activation
- The engineering spine is complete
- Azure dashboard deployment is proven
- Cloudflare Access protection is the current gate
- Live trading is not authorized by this packet

## 1. Purpose

Define the manual Cloudflare Access gate that must sit in front of the Azure AIOS dashboard before any public production exposure is treated as live-ready.

## 2. Scope

- Applies to the Azure App Service dashboard origin at the canonical Azure URL: `https://algotradez-aios-dnh4djahbne6bzfc.westus2-01.azurewebsites.net`
- Covers the Cloudflare Access front door, identity policy, verification, and failure conditions
- Does not configure Cloudflare by API
- Does not read or use secrets, tokens, publish profiles, or broker credentials
- Does not authorize live trading

## 3. Manual Cloudflare Setup Steps

1. Select the Cloudflare zone for the public AIOS dashboard hostname.
2. Choose the protected hostname or route.
3. Create a Cloudflare Access application.
4. Bind the Azure App Service origin to the protected route.
5. Configure the approved identity provider.
6. Add allowed user, email, or domain rules.
7. Require a login prompt.
8. Disable bypass.
9. Verify audit and log visibility.

## 4. Recommended Protected Hostname Pattern

- Use a dedicated public hostname such as `dashboard.<approved-domain>` or `aios.<approved-domain>`.
- Keep the Azure App Service URL as the origin, not the public canonical address.
- Do not advertise the raw Azure URL as the production dashboard entry point.

## 5. Access Policy Requirements

- Zone identified
- Application bound to hostname or route
- Identity provider configured
- Allowed user, email, or domain rule in place
- Login required for every public visit
- Unauthenticated access denied
- Bypass disabled
- Audit and log review possible

## 6. Verification Procedure

1. Open the protected URL in a normal browser and confirm the Cloudflare Access login appears.
2. Authenticate with the approved operator identity.
3. Confirm the dashboard loads after login.
4. Open an incognito or private browser session.
5. Confirm access is denied until authentication succeeds.
6. Open the raw Azure URL and document whether it is blocked, redirected, or otherwise not treated as the canonical public entry.
7. Record screenshots or notes in the evidence artifact.

## 7. Failure Conditions

- Public dashboard loads without authentication
- Bypass or equivalent unguarded path is active
- Protected hostname is not defined
- Identity provider is not configured
- Allowed identity rule is missing
- Logs or audits cannot show access decisions
- Raw Azure URL is treated as the canonical public dashboard
- Any live-trading claim is made before Access and broker gates pass

## 8. Completion Definition

This binding is complete only when manual verification proves that authenticated Cloudflare Access is required before dashboard exposure and the result is recorded in evidence.

## 9. Next Lane After Completion

GOVERNED LIVE-READINESS ACTIVATION V1
