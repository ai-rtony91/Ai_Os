# Runtime JSON Validator

## Purpose

This validator confirms that runtime report examples are valid JSON.

This docs-only package includes example JSON files but no scripts.

## Inputs

Future validator inputs:

- changed file list
- JSON files under `Reports/dispatcher/runtime/validators/`
- parser result for each changed JSON file

## PASS Logic

Return `PASS` when:

- every changed `.json` file parses
- each example includes a `schema`
- each example includes a `status`
- each example includes a `next_safe_action`

## FAIL Logic

Return `FAIL` when:

- a JSON file cannot parse
- required fields are missing
- a status value is outside `PASS`, `FAIL`, `BLOCKED`, or `REVIEW_REQUIRED`

## BLOCKED Logic

Return `BLOCKED` when:

- a JSON example describes live trading execution
- a JSON example includes secrets, API keys, credentials, broker tokens, or private keys
- a JSON example routes this package outside allowed paths

## REVIEW_REQUIRED Logic

Return `REVIEW_REQUIRED` when:

- a JSON file is valid but contains an unknown owner
- a JSON file is valid but references stale worker or lock recovery
- a JSON file is valid but describes dirty repo state

## Example Required Shape

```json
{
  "schema": "AIOS_VALIDATOR_RESULT.v1",
  "validator": "dirty_repo",
  "status": "REVIEW_REQUIRED",
  "next_safe_action": "Review dirty repo state before commit packaging."
}
```

## Next Safe Action Examples

- `Fix JSON parse errors before continuing.`
- `Review stale recovery fields before using this result.`
- `Continue. Runtime JSON examples parse successfully.`

