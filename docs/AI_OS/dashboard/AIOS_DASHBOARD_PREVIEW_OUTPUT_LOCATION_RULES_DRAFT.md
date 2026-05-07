# AI_OS Dashboard Preview Output Location Rules Draft

## Purpose

This draft defines allowed and blocked future preview output locations.

No protected root files are edited by this draft. Human approval is required before dashboard preview file generation. This draft creates no live automation, no production dashboard, and no trading automation.

## Allowed Future Preview Output Locations

- `docs/AI_OS/dashboard/`
- `Reports/health/`
- `Reports/dashboard_preview/`
- `internal/dashboard_fixtures/`

## Blocked Locations

- Protected root files.
- `.git/`.
- System folders.
- Startup folders.
- Credential stores.
- Browser profiles.
- Broker/API secret locations.
- Live trading execution folders.

## Approval Rule

Preview output locations require human approval before file generation. A future preview output writer must fail closed if the output path is not explicitly approved and allowlisted.

## Boundary

This draft does not create dashboard output, does not activate writers, and does not approve live automation.
