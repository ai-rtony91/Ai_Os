# AI_OS Dashboard Workflow State Draft

## Purpose

This draft explains how future AI_OS dashboard and operator panels may display workflow and router state without directly executing unsafe actions.

## Dashboard Scope

At this stage, the dashboard concept is visibility-only. It may display workflow names, router readiness, repo health, session evidence status, checkpoint draft status, daily metrics draft status, approval requirements, and protected file state.

## Dashboard Non-Scope

No buttons launch actions.

No buttons execute workflows.

No dashboard UI is created in this stage.

No broker, trading, or live execution visibility is approved yet.

No startup control is approved.

No credential visibility is approved.

No autonomous orchestration is approved.

## Workflow Status Concepts

Conceptual workflow states:

- `IDLE`: No workflow selected.
- `DRY_RUN_READY`: Required DRY_RUN components are present and the repo state is ready for review.
- `WARN_REVIEW_REQUIRED`: A check completed but needs human review, such as a dirty git status.
- `FAIL_BLOCKED`: A required component is missing or a blocking condition exists.
- `APPLY_PENDING_APPROVAL`: A future APPLY action has been proposed but not approved.

## Router State Concepts

Router state should show whether the workflow router exists, whether registered workflow names are available, whether helper scripts are mapped, and whether the selected workflow remains DRY_RUN-only.

## Repo Health State

Repo health state should summarize active repo path, git branch/upstream status, working tree status, protected root file presence, Reports folder presence, and helper-script availability.

## Session State

Session state should show proposed session evidence status only. It should not capture recordings, screenshots, credentials, or private content.

## Metrics State

Metrics state should show draft-only daily metrics readiness. It must not edit `Reports\DAILY_METRICS.csv` unless a later approved APPLY work-order explicitly allows it.

## PASS/WARN/FAIL Visualization Concepts

PASS can be shown as ready for review.

WARN can be shown as review required before continuing.

FAIL can be shown as blocked until fixed or reviewed.

The dashboard should preserve the exact text output source when possible so the human can audit why a state was assigned.

## Human Approval Visibility

The dashboard should make approval requirements visible before any APPLY, report write, git checkpoint, app launch, browser open, startup change, protected file edit, broker action, or trading action.

## Future Dashboard Panels

Conceptual dashboard panels:

- Repo Health
- Workflow Router
- Session Evidence
- Checkpoint Drafts
- Daily Metrics Drafts
- Approval Queue
- Protected File State

## Future Stage 11C

Future Stage 11C may define dashboard data contracts, static mockups, or text-only state snapshots. It must remain visibility-first and must not add live control, autonomous execution, or unsafe buttons.
