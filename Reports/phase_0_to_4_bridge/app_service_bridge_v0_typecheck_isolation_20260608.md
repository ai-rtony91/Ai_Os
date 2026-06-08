# AI_OS App Service Bridge v0 Typecheck Isolation 2026-06-08

Status: DRY_RUN evidence only.

## Scope

Packet: `AIOS-APP-SERVICE-BRIDGE-V0-DRY-RUN-FIRST`

Goal: determine whether the App Service Bridge v0 introduced TypeScript typecheck errors.

## Changed Bridge Files Reviewed

- `services/orchestrator/index.js`
- `services/orchestrator/appServiceBridge.js`
- `services/package.json`
- `tests/services/appServiceBridge.test.js`
- `Reports/phase_0_to_4_bridge/app_service_bridge_v0_design_dry_run.md`
- `Reports/phase_0_to_4_bridge/app_service_bridge_v0_endpoint_contract.example.json`
- `Reports/phase_0_to_4_bridge/app_service_bridge_v0_validator_result.example.json`

## Focused Bridge Validation

Passed:

- `node --check services/orchestrator/index.js`
- `node --check services/orchestrator/appServiceBridge.js`
- `npm --prefix services run test:services`

Service test result:

- 3 tests passed.
- 0 tests failed.

## Typecheck Command

```powershell
npm --prefix services run typecheck
```

Result: failed.

## Typecheck Scope Evidence

`services/tsconfig.json` includes:

```json
"include": [
  "**/*.ts"
]
```

`services/tsconfig.json` excludes:

```json
"exclude": [
  "node_modules",
  "dist",
  "orchestrator"
]
```

The new bridge implementation files are JavaScript files under `services/orchestrator/`, and the tests are JavaScript files under `tests/services/`. They are not TypeScript compilation inputs for `npm --prefix services run typecheck`.

## Typecheck Error Classification

### NEW_APP_SERVICE_BRIDGE_SCOPE

None found.

### PRE_EXISTING_OUT_OF_SCOPE

Failing folders and representative errors:

- `services/dispatcher/`
  - `dispatcher/autonomousScheduler.ts`: `staleAssignedPackets` missing on `WorkerLeaseResult`.
  - `dispatcher/deadLetterQueue.ts`: object missing `DeadLetterPacket` fields.
  - `dispatcher/packetResumeEngine.ts`: `invalidPacketStatuses` missing on `RebuiltDispatcherState`.

- `services/runtime/`
  - `runtime/index.ts`: missing Node type definitions for `process`.
  - `runtime/index.ts`: object literals include unknown `entries` and `leases` properties.
  - `runtime/runtimeAutomationExecutor.ts`: `AutomationDispatchPacket` missing fields such as `mode`, `approvalId`, `approvalDecidedAt`, and `approvalDecision`.
  - `runtime/runtimeTick.ts`: `RebuiltDispatcherState` missing `invalidLineCount` and `invalidPacketStatuses`.

- `services/supervisor/`
  - `supervisor/runtimeSupervisor.ts`: `staleAssignedPackets` missing on `WorkerLeaseResult`.
  - `supervisor/runtimeSupervisor.ts`: telemetry replay shape missing `ledger`.
  - `supervisor/runtimeSupervisor.ts`: `RuntimeVisibilityInput` does not accept `telemetryLedger`.

- `services/telemetry/`
  - `telemetry/automationAuditReplay.ts`: missing Node module type declarations for `fs`.
  - `telemetry/telemetryReplay.ts`: missing Node module type declarations for `fs` and `Buffer`.
  - `telemetry/telemetryWriter.ts`: missing Node module type declarations for `fs` and `path`.

### UNKNOWN_REQUIRES_REVIEW

None found.

## Bridge Error Determination

Did App Service Bridge v0 introduce TypeScript errors: NO.

Reason: the global TypeScript failure is confined to existing `.ts` systems outside `services/orchestrator/`, while the bridge code is JavaScript under a path excluded by `services/tsconfig.json`.

## Recommendation

Commit readiness recommendation: commit the App Service Bridge v0 only if Anthony accepts the known global typecheck blocker as pre-existing and out of scope for this lane.

Conservative alternative: block commit until a separate services TypeScript repair lane fixes `services/dispatcher/`, `services/runtime/`, `services/supervisor/`, and `services/telemetry/`.

Best practical next step: keep the bridge lane commit separate from the broader TypeScript repair lane so the local preview bridge is not tangled with unrelated service debt.

## Next Safe Command

```powershell
npm --prefix services run test:services
```
