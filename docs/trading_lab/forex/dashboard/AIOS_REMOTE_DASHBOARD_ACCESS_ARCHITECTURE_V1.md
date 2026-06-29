# AIOS Remote Dashboard Access Architecture V1

## Canonical Surface

AIOS remote dashboard access must preserve one canonical dashboard surface:

```text
FOREX_DASHBOARD_RUNTIME_UI_V1
```

Remote access must not create a competing dashboard, alternate product surface, one-off website, or image-only preview. The future target is a protected read-only route to the canonical AIOS Forex dashboard surface that can eventually be reached from mobile.

## Current State

Current status:

- Static dashboard package exists.
- Canonical dashboard state exists at `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_STATE.json`.
- Current dashboard docs exist at `docs/trading_lab/forex/dashboard/FOREX_DASHBOARD_RUNTIME_UI_V1.md`.
- Current preview is local/static and display-only.
- Mobile remote access is not yet production-ready.
- No public remote server is approved.
- No tunnel is approved.
- No deployment is approved.

This document defines architecture only. It does not start services, expose ports, create tunnels, deploy, read secrets, or authorize broker/demo/live paths.

## Remote Access Modes

### 1. `LOCAL_ONLY_STATIC_PREVIEW`

Purpose: current repo-safe preview.

Allowed:

- Open local HTML directly.
- Display local report-derived dashboard state.
- Show critical status, blocker, next safe action, and safety state.
- Keep detail behind report windows.

Blocked:

- Network exposure.
- Public sharing.
- Authentication claims.
- Broker/demo/live controls.
- Secrets or account identifiers.

Status: `EXISTS`

### 2. `LAN_READONLY_SERVER`

Purpose: local network read-only access after an approved implementation packet.

Required:

- Read-only routes only.
- Authentication before LAN access.
- Configured bind host and explicit operator approval before LAN exposure.
- Source freshness labels.
- Audit display only.
- Method restrictions and no mutation routes.

Status: `FUTURE_STEP`

### 3. `TAILSCALE_READONLY_ROUTE`

Purpose: private mesh read-only proof for mobile access.

Required:

- Private mesh route only.
- Authentication preserved.
- No Tailscale Funnel unless separately approved.
- No always-on route without owner approval.
- Mobile display validation.
- Negative validation that no controls can execute.

Status: `FUTURE_STEP`

### 4. `AUTHENTICATED_REMOTE_HOST`

Purpose: authenticated HTTPS remote host proof.

Required:

- HTTPS.
- Authentication.
- Read-only dashboard API.
- Sanitized responses.
- No frontend secrets.
- No broker account identifiers.
- No execution, scheduler, daemon, webhook, or background-loop controls.

Status: `FUTURE_STEP`

### 5. `FUTURE_PRODUCTION_DASHBOARD`

Purpose: hardened production dashboard after staged proofs.

Required:

- Authentication and session controls.
- HTTPS or private mesh controls appropriate to deployment.
- Strict read-only API contract.
- Source freshness labels.
- Audit log display only.
- Kill-switch display only.
- Security headers and route tests.
- Owner approval before any always-on exposure.

Status: `FUTURE_STEP`

## Required Remote Protections

Every remote mode above `LOCAL_ONLY_STATIC_PREVIEW` requires:

- Authentication required.
- HTTPS or private mesh route required.
- Read-only dashboard API.
- No secrets in frontend.
- No broker account identifiers.
- No order controls.
- No demo/live authorization controls.
- No scheduler/daemon/webhook/background-loop controls.
- Kill-switch display only.
- Source freshness labels.
- Audit log display only.

## API Boundary

The read-only dashboard API should preserve the existing runtime visibility contract:

```text
schema: aios.runtime_visibility_api.v1
mode: READ_ONLY
execution_allowed: false
mutation_allowed: false
```

The frontend must reject non-read-only responses. Future routes must expose display projections only and must not mutate approvals, locks, queues, workers, runtime processes, broker state, credentials, orders, or live/demo authorization state.

## Broker Boundary

Broker boundary status: `PROTECTED_AND_SEPARATE`

Remote dashboard access must not show:

- Broker account identifiers.
- Secret values.
- Credential presence details that help recover secrets.
- Real order IDs.
- Order payloads.
- Demo or live authorization controls.
- Broker execution controls.

Allowed display:

- Sanitized readiness status.
- Sanitized blocker status.
- Kill-switch state as display-only.
- Audit/evidence links as display-only.

## Bitwarden Boundary

Bitwarden status: `LOCKED`

This architecture does not start Bitwarden or Vaultwarden. It does not migrate secrets, read credentials, add tokens, read `.env`, or define a frontend secret path.

## Next Implementation Sequence

A. Read-only local dashboard server.

- Use localhost as the default safe bind.
- Serve `FOREX_DASHBOARD_RUNTIME_UI_V1`.
- Expose read-only JSON endpoints only.
- Preserve read-only response validation.
- Add tests for blocked mutation and method restrictions.

B. Authenticated local network access.

- Add authentication before any LAN exposure.
- Require explicit operator approval before non-local bind.
- Add freshness and audit display labels.

C. Tailscale/private route proof.

- Use private mesh only.
- Require owner approval before starting the proof.
- Validate mobile access and blocked controls.

D. Remote host proof.

- Use HTTPS and authentication.
- Serve sanitized read-only projections.
- Keep secrets out of frontend and repo.

E. Production hardening.

- Add route security tests.
- Add auth/session controls.
- Add rate limits and security headers.
- Add source freshness warnings.
- Add audit-log display-only panels.

F. Owner approval before any always-on exposure.

- Always-on LAN, mesh, remote host, tunnel, or production exposure remains blocked until explicitly approved.

## Stop Conditions

Stop before:

- Starting services.
- Exposing a port.
- Starting Tailscale Serve or Funnel.
- Starting Cloudflare tunnel.
- Deploying.
- Reading `.env`.
- Reading credentials.
- Starting Bitwarden.
- Adding secrets.
- Adding broker/demo/live controls.
- Adding scheduler, daemon, webhook, or background-loop controls.

Status: `REMOTE_DASHBOARD_ARCHITECTURE_DEFINED`
