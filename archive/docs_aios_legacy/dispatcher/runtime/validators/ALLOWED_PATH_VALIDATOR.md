# Allowed Path Validator

## Purpose

This validator confirms that a package changes only the paths approved in the prompt.

For this package, the allowed paths are:

- `docs/AI_OS/dispatcher/runtime/validators/`
- `Reports/dispatcher/runtime/validators/`

## Inputs

Future validator inputs:

- allowed path list
- changed file list
- approved package name

## PASS Logic

Return `PASS` when every changed file begins with one of the approved path prefixes.

## FAIL Logic

Return `FAIL` when:

- the allowed path list is missing
- the changed file list cannot be read
- path comparison cannot be completed

## BLOCKED Logic

Return `BLOCKED` when a changed file is outside the allowed paths and the stage is APPLY, post-APPLY, or commit packaging.

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- a file appears related but is not inside the allowed path
- path casing or slash format needs human review
- the package references a path that does not exist yet

## Example

Changed file:

`docs/AI_OS/dispatcher/runtime/validators/VALIDATOR_IMPLEMENTATION_PLAN.md`

Result:

`PASS`

Changed file:

`automation/operator/Start-AIOSWorkerQueueRunner.ps1`

Result:

`BLOCKED`

## Next Safe Action Examples

- `Continue. All files are inside allowed paths.`
- `Stop. Request a new approval for any file outside allowed paths.`

