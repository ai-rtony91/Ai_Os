# Runtime APPLY Package Sequence

Phase 15.4 should be applied in small controlled packages.

This keeps runtime design, schemas, validators, scripts, and dashboard work from mixing together.

## Package A: Docs Only

Allowed path:

`docs/AI_OS/dispatcher/runtime/`

Purpose:

Define the architecture, ownership boundaries, lifecycle rules, validation model, approval model, queue monitoring model, and status output model.

This package is safest first because it creates no executable runtime behavior.

## Package B: Reports Example JSON Schemas

Allowed path:

`Reports/dispatcher/runtime/`

Purpose:

Add example JSON files that match the docs.

This package should not include scripts.

## Package C: PowerShell Validators

Allowed path:

`automation/dispatcher/runtime/validators/`

Purpose:

Add validators for schemas, allowed paths, blocked paths, protected files, JSON parsing, PowerShell parsing, and dirty repo checks.

This package should wait until Package B exists.

## Package D: Runtime Helper Scripts

Allowed path:

`automation/dispatcher/runtime/`

Purpose:

Add helper scripts for packet checks, lock checks, heartbeat checks, status writing, and queue monitoring.

This package should wait until validators exist.

## Package E: Dashboard Data Contract Only

Allowed path:

`docs/AI_OS/dispatcher/runtime/`

Purpose:

Document the final dashboard-safe data contract.

No dashboard UI files should be edited.

## Package F: Later Dashboard UI Integration

Allowed path:

Only paths approved in a separate dashboard APPLY prompt.

Purpose:

Connect dashboard panels to validated runtime summaries.

This package must be deferred until runtime outputs are stable.

## Blocked Until Validation Exists

Runtime helper scripts, queue mutation, worker launch automation, recovery override automation, and dashboard integration must wait until validators exist and pass.

