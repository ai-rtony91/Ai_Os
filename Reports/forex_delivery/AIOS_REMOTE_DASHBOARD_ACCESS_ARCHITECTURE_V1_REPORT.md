# AIOS Remote Dashboard Access Architecture V1 Report

## Packet

- Packet ID: `PKT-AIOS-REMOTE-DASHBOARD-ACCESS-ARCHITECTURE-V1`
- Mode: `LOCAL_APPLY`
- Lane: `AIOS remote dashboard access`
- Worktree: `C:\Dev\Ai.Os`
- Branch: `main`
- Report generated: `2026-06-29`

## Summary

AIOS has a repo-safe dashboard access path target, but remote mobile access is not production-ready yet.

The canonical dashboard surface remains:

```text
FOREX_DASHBOARD_RUNTIME_UI_V1
```

The current dashboard package is a static local preview backed by local repo artifacts. The future remote path must promote that same canonical surface through staged read-only access modes without creating a second dashboard, exposing ports publicly, starting tunnels, deploying services, reading secrets, or adding broker/demo/live controls.

## Evidence Read

Required files read:

- `AGENTS.md`
- `README.md`
- `docs/governance/source-of-truth-map.md`
- `docs/audits/active-system-map.md`
- `docs/trading_lab/forex/FOREX_DASHBOARD_END_USER_FINAL_UX_V1.md`
- `docs/trading_lab/forex/FOREX_DASHBOARD_EMOJI_WINDOW_MAP_FINAL_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_STATE.json`

Inspected paths:

- `apps/dashboard/`
- `services/orchestrator/`
- `scripts/control/`
- `telemetry/runtime/`
- `docs/trading_lab/forex/dashboard/`
- `Reports/forex_delivery/`

## Current Dashboard Evidence

Observed current dashboard state:

- Static dashboard package exists.
- Canonical dashboard ID is `FOREX_DASHBOARD_RUNTIME_UI_V1`.
- Runtime UI type is `STATIC_LOCAL_CLICKABLE_EMOJI_HTML`.
- Existing package includes local preview HTML, docs HTML, report, state JSON, script, implementation, and tests.
- Current local preview blocks broker contact, account inspection, orders, demo/live authorization, Bitwarden, Vaultwarden, secrets migration, token storage, scheduler, daemon, webhook, and background-loop actions.
- Current dashboard documentation says the preview can be opened directly in a browser and reads local Forex report artifacts only.

Observed current runtime/dashboard split:

- `apps/dashboard/src/runtimeVisibilityClient.js` expects `/api/runtime/visibility`, validates schema `aios.runtime_visibility_api.v1`, and rejects responses where `mode` is not `READ_ONLY`.
- `services/orchestrator/runtimeApiService.js` builds a read-only visibility snapshot with `execution_allowed: false`, `mutation_allowed: false`, blocked frontend actions, source paths, freshness metadata, and next safe action labels.
- `services/orchestrator/index.js` includes display/read-only Forex routes and blocks money-strip data unless runtime-only OANDA read-only environment gates are present. This packet did not start services or read environment variables.
- `apps/dashboard/server.js` can serve static files and a local live-data file, but it listens on `0.0.0.0` when started. This packet did not start it.

## Remote Dashboard Target

Future target:

```text
One canonical dashboard surface: FOREX_DASHBOARD_RUNTIME_UI_V1
```

Remote access should evolve through these modes:

1. `LOCAL_ONLY_STATIC_PREVIEW`
2. `LAN_READONLY_SERVER`
3. `TAILSCALE_READONLY_ROUTE`
4. `AUTHENTICATED_REMOTE_HOST`
5. `FUTURE_PRODUCTION_DASHBOARD`

Each mode must keep the dashboard display-only and must not add execution authority.

## Required Protections

Any remote or network-reachable dashboard route requires:

- Authentication required.
- HTTPS or private mesh route required.
- Read-only dashboard API.
- No secrets in frontend.
- No broker account identifiers.
- No order controls.
- No demo/live authorization controls.
- No scheduler, daemon, webhook, or background-loop controls.
- Kill-switch display only.
- Source freshness labels.
- Audit log display only.

## Current Access Status

- Static dashboard package exists.
- Local direct-file preview exists.
- Mobile remote access is not yet production-ready.
- No public remote server is approved.
- No tunnel is approved.
- No deployment is approved.
- No services were started by this packet.
- No ports were exposed by this packet.

## Deployment Status

Deployment status: `NOT_APPROVED`

Blocked actions:

- Public server exposure.
- Cloudflare tunnel.
- Tailscale Serve or Funnel.
- Always-on remote host.
- Production deployment.
- Broker/demo/live path activation.
- Secret-manager startup.
- Credential or `.env` reads.

## Broker Boundary

Broker boundary remains protected and separate.

The dashboard may display sanitized status only. It must not expose broker account identifiers, account state, order IDs, live payloads, credential values, demo/live authorization controls, or execution controls.

## Bitwarden Status

Bitwarden and Vaultwarden remain locked.

This architecture package does not start Bitwarden, read credentials, add secrets, migrate tokens, or create a secret storage path.

## Next Implementation Sequence

A. Build a read-only local dashboard server.

- Bind to localhost by default.
- Serve `FOREX_DASHBOARD_RUNTIME_UI_V1`.
- Expose only read-only JSON endpoints.
- Preserve `mode: READ_ONLY`, `execution_allowed: false`, and `mutation_allowed: false`.
- Add tests for route method restrictions and blocked controls.

B. Add authenticated local network access.

- Require authentication before any LAN access.
- Use a configured bind host, not default broad exposure.
- Preserve HTTPS where practical or explicitly label LAN as non-production.
- Add source freshness and audit display labels.

C. Prove Tailscale/private route access.

- Use private mesh only.
- Do not use Funnel for public exposure unless separately approved.
- Require owner approval before starting any private route proof.
- Validate mobile read-only display and blocked controls.

D. Prove remote host access.

- Use an authenticated remote host with HTTPS.
- Use sanitized, read-only API responses.
- Do not store secrets in frontend or repo.
- Do not expose broker account identifiers.

E. Production hardening.

- Add auth/session controls.
- Add rate limits and cache headers.
- Add route-level no-write enforcement.
- Add security headers.
- Add source freshness warnings.
- Add audit-log display only.
- Add negative tests for execution routes and secrets leakage.

F. Require owner approval before any always-on exposure.

- Always-on LAN, mesh, remote host, tunnel, or production exposure requires explicit Human Owner approval and protected-action review.

## Validation

Required validators for this packet:

```powershell
python -m json.tool Reports/forex_delivery/AIOS_FOREX_DASHBOARD_RUNTIME_UI_V1_STATE.json
git diff --check
git status --short --branch
```

## Result

Status: `REMOTE_DASHBOARD_ARCHITECTURE_DEFINED`

Commit status: no commit.

Push status: no push.
