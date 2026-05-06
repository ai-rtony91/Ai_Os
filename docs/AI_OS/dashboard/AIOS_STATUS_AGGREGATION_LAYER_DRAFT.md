# AI_OS Status Aggregation Layer Draft

## Purpose

This draft explains how future AI_OS dashboards may aggregate router status, workflow status, repo health, metrics drafts, checkpoint drafts, approval state, warnings, and failures.

## Aggregation Sources

Potential read-only aggregation sources include:

- Workflow router output.
- Workflow registry draft.
- Operator command map.
- Repo health helper output.
- Session evidence helper output.
- Checkpoint draft helper output.
- Daily metrics draft helper output.
- Protected file checks.
- Git status output.

## Aggregation Rules

The aggregation layer is read-only.

Aggregation does not approve APPLY.

Aggregation does not edit reports.

Aggregation does not touch trading or broker systems.

Aggregation should preserve source text or source paths where practical so human review can trace why a state was assigned.

## PASS/WARN/FAIL Prioritization

FAIL has highest priority and should block continuation until reviewed.

WARN means human review is required before continuing.

PASS means the state can be reviewed as ready, but it does not approve APPLY.

When multiple sources disagree, the dashboard should show the most restrictive state and flag the mismatch for review.

## Human Review Requirements

Human review is required before any APPLY, report write, protected file edit, git add, git commit, git push, app launch, browser open, startup change, settings change, credential handling, broker action, or trading action.

## Non-Scope

This layer does not create a dashboard UI, execute workflows, modify startup settings, create scheduled tasks, open browsers, launch apps, edit `Reports\DAILY_METRICS.csv`, update `Reports\CHECKPOINT_INDEX.md`, handle credentials, touch broker systems, place trades, or enable live trading.

## Future Dashboard Binding

Future dashboard binding may map read-only status fields to panels such as Repo Health, Workflow Router, Session Evidence, Checkpoint Drafts, Daily Metrics Drafts, Approval Queue, and Protected File State. Binding must remain visibility-first until a separate approved work-order defines any controlled interaction.
