# AI_OS Persistent Snapshot Boundary Draft

## Purpose

This draft defines the boundary for future persistent dashboard snapshots. Future snapshots may store dashboard-readable state, but writing snapshots is not approved yet.

## Current Boundary

AI_OS snapshot work remains DRY_RUN-first and console-output-only. Snapshot helpers may print state for human review, but they must not write snapshot files without a later approved work-order.

## Approved Read-Only Sources

Approved read-only sources may include:

- Dashboard snapshot helper output.
- Morning Brief state helper output.
- Approval queue validator output.
- Workflow registry.
- Workflow router output.
- Repo health output.
- Git status output.
- Protected-file diff output.

## Proposed Future Snapshot Fields

Proposed future fields:

- `timestamp`
- `repo_root`
- `git_branch`
- `dashboard_state`
- `approval_state`
- `morning_brief_state`
- `workflow_name`
- `risk_level`
- `approval_required`
- `protected_files_changed`
- `daily_metrics_changed`
- `checkpoint_index_changed`

## Proposed Future Snapshot Location

Proposed future snapshot path concept:

```text
Reports\snapshots
```

This path is not approved for creation or writing in this stage.

## Snapshot Write Approval Requirements

Future snapshot writing requires separate approval. Approval must define the output path, file format, naming pattern, fields, retention rule, protected data exclusions, and whether the action is DRY_RUN or APPLY.

## Snapshot Non-Scope

No snapshot files are written yet.

No JSON files are written yet.

No dashboard UI is created.

No broker or trading data is stored.

No secrets or credentials are stored.

## Protected Data Restrictions

Snapshots must not include secrets, credentials, broker tokens, private keys, recovery keys, live trading data, broker execution data, uncontrolled screen content, or private user material.

Snapshots must not edit protected root files, `Reports\DAILY_METRICS.csv`, or `Reports\CHECKPOINT_INDEX.md`.

## Human Review Rules

Humans must review snapshot content and approval scope before any persistent snapshot writer is created. Git checkpointing remains a separate human-approved action.

## Future Stage 15

Future Stage 15 may propose a DRY_RUN-only snapshot writer plan, static JSON fixture, or `Reports\snapshots` folder purpose note. It must not write persistent history without separate approval.
