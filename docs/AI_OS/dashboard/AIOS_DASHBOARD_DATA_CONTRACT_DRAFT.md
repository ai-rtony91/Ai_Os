# AI_OS Dashboard Data Contract Draft

## Purpose

This contract defines future dashboard-readable fields for AI_OS workflow and status visibility. It gives future dashboard work predictable text/state fields without launching a dashboard or writing live reports.

## Data Contract Scope

The data contract describes read-only status fields that may be displayed by future dashboard or operator panels.

## Data Contract Non-Scope

This contract does not create a dashboard UI, execute workflows, approve APPLY, launch apps, open browsers, change startup settings, edit reports, write JSON, touch credentials, touch broker systems, place trades, or enable live trading.

## Required Status Fields

Required fields:

- `timestamp`
- `repo_root`
- `git_branch`
- `git_status_clean`
- `dashboard_state`
- `router_available`
- `registry_available`
- `workflow_count`
- `active_workflow`
- `last_result`
- `approval_required`
- `risk_level`
- `protected_files_changed`
- `daily_metrics_changed`
- `checkpoint_index_changed`

## Workflow Fields

Workflow fields describe the active or selected workflow state:

- `workflow_count`
- `active_workflow`
- `last_result`
- `dashboard_state`
- `approval_required`
- `risk_level`

## Repo Fields

Repo fields describe the local repo state:

- `repo_root`
- `git_branch`
- `git_status_clean`
- `protected_files_changed`
- `daily_metrics_changed`
- `checkpoint_index_changed`

## Approval Fields

Approval fields describe whether human approval is required before continuing:

- `approval_required`
- `risk_level`
- `dashboard_state`

Dashboard display must make clear that APPLY, report writes, protected file edits, git add, git commit, git push, app launch, browser open, startup changes, broker actions, and trading actions require separate human approval.

## Risk Fields

Risk fields should use LOW, MEDIUM, HIGH, or UNKNOWN.

LOW means read-only DRY_RUN console-output.

MEDIUM means creates approved files but no git commit.

HIGH means moves, deletes, overwrites, launches, changes settings, touches credentials, or touches trading systems.

## Panel Mapping

Conceptual panel mapping:

- Repo Health -> `dashboard_state`
- Workflow Router -> `router_available`
- Daily Metrics -> `daily_metrics_changed`
- Checkpoint Index -> `checkpoint_index_changed`
- Approval Queue -> `approval_required`

## Future JSON Binding

This contract is read-only. It does not write JSON yet.

Future JSON output requires separate approval, exact output path scoping, and a DRY_RUN plan before any file is written.

## Future Stage 12

Future Stage 12 may propose JSON snapshot output, dashboard mock data, or a static dashboard contract test. It must remain DRY_RUN-first and must not enable live dashboard control or autonomous execution.
