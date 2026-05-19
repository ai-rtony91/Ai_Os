# AI_OS Snapshot History Draft

## Purpose

This draft explains how future AI_OS systems may retain read-only historical workflow snapshots for dashboard and operator review.

## Snapshot Scope

Snapshot history may display prior DRY_RUN workflow states, dashboard states, approval requirements, risk levels, warning status, protected-file status, and git cleanliness.

## Snapshot Non-Scope

Snapshots are read-only.

Snapshots do not execute workflows.

Snapshots do not approve APPLY.

Snapshots do not touch broker or trading systems.

Snapshots do not yet write JSON or history files.

## Snapshot Sources

Potential future snapshot sources include:

- Dashboard text snapshot output.
- Workflow state helper output.
- Router workflow output.
- Repo health helper output.
- Approval state helper output.
- Protected-file diff checks.
- Git status output.

## Snapshot State Types

Conceptual snapshot states:

- `IDLE`
- `DRY_RUN_READY`
- `WARN_REVIEW_REQUIRED`
- `FAIL_BLOCKED`
- `APPLY_PENDING_APPROVAL`

## Snapshot Retention Concepts

Future retention should preserve enough context for human review without storing secrets, credentials, broker tokens, private keys, uncontrolled recordings, or sensitive screen content.

Snapshot retention should use an approved path, naming pattern, and DRY_RUN report before any file-writing history feature is created.

## PASS/WARN/FAIL History Concepts

PASS history means the prior state was ready for human review.

WARN history means the prior state needed review before continuing.

FAIL history means the prior state was blocked.

Historical PASS does not approve future APPLY.

## Human Review Visibility

Snapshot history should make approval requirements visible. A human should be able to see when APPLY approval, git checkpoint approval, protected file approval, or high-risk review was required.

## Future Dashboard Timeline Concepts

Future dashboard timelines may show:

- `timestamp`
- `dashboard_state`
- `workflow_name`
- `git_status_clean`
- `approval_required`
- `risk_level`
- `warnings_present`
- `protected_files_changed`

## Future Stage 12C

Future Stage 12C may propose a DRY_RUN-only snapshot-history writer or JSON history contract. It must not write files, execute workflows, approve actions, or expose sensitive data without separate approval.
