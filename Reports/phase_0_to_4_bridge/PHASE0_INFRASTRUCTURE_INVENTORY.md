# Phase 0 Infrastructure Inventory

Status: evidence, not authority.

## SUMMARY

Inventory generated from tracked files and current Git state. This report is evidence only.

## WHAT EXISTS

```json
{
  "automation_files_sampled": 200,
  "governance_files": 27,
  "validator_files_sampled": 200,
  "workflow_files": 38
}
```

## WHAT IS MISSING

- None

## WHAT IS DISCONNECTED

- `GOVERNANCE_DOC_ONLY where rules have no hook or CI enforcement`
- `APPLY_NOT_WIRED for DRY_RUN scripts without APPLY counterparts`
- `DOC_ONLY for future automation claims represented only in docs`

## WHAT IS UNSAFE TO TOUCH

- `AGENTS.md`
- `README.md`
- `live trading`
- `broker credentials`
- `commit`
- `push`
- `merge`

## WHAT CAN BE BUILT NOW

- `subordinate bridge evidence`
- `approval compressor`
- `governance validator`
- `self-build inspector`

## WHAT REQUIRES APPROVAL

- `protected root edits`
- `commit`
- `push`
- `merge`
- `live or broker work`

## SAFE NEXT ACTION

Run the bridge in DRY_RUN and inspect reports.
