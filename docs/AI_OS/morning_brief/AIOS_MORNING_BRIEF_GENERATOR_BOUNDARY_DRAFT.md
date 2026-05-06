# AI_OS Morning Brief Generator Boundary Draft

## Purpose

This draft explains the difference between a future Morning Brief generator and current DRY_RUN console helpers.

## Current Boundary

Current Morning Brief helpers are DRY_RUN and console-output-only. They may print state, warnings, pending approvals, and next safe actions, but they do not write Morning Brief files.

## Generator Non-Scope

No generator writes files yet.

No startup task is created.

No app or window launch occurs.

No credential, broker, or trading data is included.

No browser is opened, no settings are changed, and no APPLY workflow is executed.

## Allowed Future Inputs

Allowed future inputs may include repo health state, workflow state, dashboard state, approval state, snapshot boundary state, report boundary state, protected-file diff status, and pending approval summaries.

## Proposed Future Output Path

Proposed future output path concept:

```text
Reports\morning_brief
```

This folder is not approved for creation in this stage.

## Approval Requirements

Future Morning Brief file writing requires separate approval. Approval must define output path, naming rules, retention rules, protected data exclusions, backup/checkpoint expectations, and verification steps.

## Protected Data Restrictions

Morning Brief output must not include secrets, credentials, broker tokens, private keys, recovery keys, uncontrolled screen contents, broker execution data, live trading data, or private user material.

## Startup Safety Rules

Morning Brief generation must not create startup tasks, change startup settings, launch apps, open windows, open browsers, or auto-continue into APPLY work.

## Human Review Rules

Human review is required before APPLY, report writing, protected file editing, git add, git commit, git push, app launch, browser open, startup change, settings change, credential handling, broker action, trading action, or live execution.

## Future Stage 16

Future Stage 16 may propose a DRY_RUN-only Morning Brief text generator that prints a complete brief to console. File-writing remains blocked until separately approved.
