# Change Request Template

Use this template before any AI_OS change.

## User Goal

What does the user want?

## Change Type

Examples: UI / UX, tools, gallery, radio dock player, dashboard panel, app connector, API planning, Trading Lab, product docs, mock data, validator.

## Owner / Agent

Who owns the change?

## Allowed Files

List exact files or folders that may be changed.

## Blocked Files

List exact files or folders that must not be touched.

## DRY_RUN Required

YES by default.

## APPLY Approval Required

YES by default.

## Validation Required

List checks that must pass before commit.

## Commit Package

Name the files that belong together in one commit.

## Rollback Note

Describe how to recover if the change is wrong.

## Safety Boundary

No secrets, no installs, no broker, no OANDA, no live trading, no real API activation, no dashboard edit unless exact dashboard paths are approved.
