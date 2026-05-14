# Blocked Path Validator

## Purpose

This validator stops a package when it touches a blocked path.

Blocked paths are stricter than allowed paths. A file can be useful and still blocked for the current package.

## Blocked Paths For This Package

This package must not touch:

- `automation/operator/`
- `Reports/security/`
- `apps/dashboard/`
- `automation/telemetry/`
- `Reports/telemetry/`
- broker files
- OANDA files
- API key files
- live trading files

## PASS Logic

Return `PASS` when no changed file is in a blocked path and no changed file appears to be a broker, OANDA, API key, or live trading file.

## FAIL Logic

Return `FAIL` when:

- the blocked path list is missing
- file classification cannot be completed
- a path cannot be normalized for comparison

## BLOCKED Logic

Return `BLOCKED` when:

- a changed file starts with a blocked path
- a changed file name or path clearly indicates broker, OANDA, API key, or live trading behavior
- a report attempts to route this docs-only package into a blocked path

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- a file name is ambiguous
- a text reference mentions a blocked area but does not edit it
- a dirty repo entry exists in a blocked path before this package starts

## Example

Changed file:

`Reports/security/security_findings.json`

Result:

`BLOCKED`

Reason:

`Reports/security/` is blocked for this package.

## Next Safe Action Examples

- `Stop. Remove blocked path from package scope.`
- `Keep blocked path changes out of commit packaging.`
- `Ask for a separate approval if blocked path work is needed later.`

