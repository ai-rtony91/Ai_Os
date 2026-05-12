# AI_OS Portal Zone Model

## Zones

AI_OS should expose zones behind the protected front door:

- Home Portal
- Trading Lab
- Work Table
- Personal Apps
- Admin Zone

## Home Portal

The Home Portal is the first approved landing page after Cloudflare Access, Microsoft Entra SSO, and strong factor checks.

## Trading Lab

Trading Lab remains paper-only.

Secure access does not enable broker login, live orders, OANDA, Webull, or trading execution.

## Work Table

Work Table is for local planning, project packets, reports, and guided build workflow.

## Personal Apps

Personal Apps should remain protected by the same access boundary and should not request credentials unless a future approved connector design exists.

## Admin Zone

Admin Zone requires stronger re-check and should be separated from daily user flow.

