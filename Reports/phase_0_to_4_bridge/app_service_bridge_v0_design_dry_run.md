# AI_OS App Service Bridge v0 Design DRY_RUN

Status: APPLY implementation evidence for a local DRY_RUN-first service bridge.

## Summary

AI_OS App Service Bridge v0 extends the existing repo-native `services/orchestrator` Express layer. It provides a local-only preview/read API between packet-producing tools and canonical repo orchestration state.

The bridge does not call providers, launch Codex, run queued commands, install hooks, mutate approvals, mutate worker state, mutate locks, start Night Supervisor, deploy cloud resources, create tunnels, store secrets, or enable live trading or broker runtime work.

## Endpoints

- `GET /health`: local bridge health and safety boundary.
- `POST /packets`: packet draft validation and route preview only.
- `GET /queue`: command queue and worker inbox status only.
- `POST /approvals`: approval request preview only.
- `GET /workers`: worker registry, inbox, profile, and lock status only.
- `GET /reports/latest`: latest bridge report evidence only.
- `POST /sos`: SOS-only notification preview, no send and no telemetry write.

## State Store

V0 does not write a recurring state store. The proposed future generated-output root is:

`telemetry/app_service_bridge/`

Before recurring writes are enabled, `.gitignore` handling should be proposed and reviewed so local JSONL receipts do not create source-control churn.

## Night Supervisor Integration Proposal

Night Supervisor can later read:

- bridge health mode.
- pending approval counts.
- worker inbox counts.
- lock status.
- latest report path.
- SOS preview status.

Night Supervisor must remain sandboxed and must not mutate bridge, approval, worker, lock, or telemetry state without a later approved packet.

## Codex Worker Queue Integration Proposal

Codex-facing queue integration should stay as packet preview and queue visibility only. Any real Codex execution must remain a separate explicit operator action or a separately approved packet.

## Validation

Expected validation chain:

- `node --check services/orchestrator/index.js`
- `node --check services/orchestrator/runtimeApiService.js`
- `npm --prefix services run typecheck`
- `npm --prefix services run test:services`
- `python automation/validators/aios_governance_validator.py --sample-check`
- `python automation/validators/aios_governance_validator.py --input automation/orchestration/work_packets/proposed/AIOS-APP-SERVICE-BRIDGE-V0-DRY-RUN-FIRST.md`
- `git diff --check`

Observed validation note:

- Bridge JS parser checks passed.
- Service bridge tests passed.
- Packet governance validator passed for the proposed packet.
- `git diff --check` passed with line-ending warnings for existing Windows checkout behavior.
- `npm --prefix services run typecheck` failed on pre-existing TypeScript errors under `services/dispatcher/`, `services/runtime/`, `services/supervisor/`, and `services/telemetry/`. Those paths are outside the approved App Service Bridge v0 edit scope.
