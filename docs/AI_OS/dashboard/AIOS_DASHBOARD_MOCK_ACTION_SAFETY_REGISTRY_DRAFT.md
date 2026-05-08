# AI_OS Dashboard Mock Action Safety Registry Draft

Status: Draft
Mode: Static dashboard action safety registry
Date: 2026-05-08

## Purpose

Define which dashboard actions are safe mock actions, which actions are blocked, and which future actions require explicit approval before any implementation.

## Safe Mock Actions

Safe mock actions are allowed only when they change local visual state or static preview text.

Current safe mock actions:

- Select App Dock items.
- Select status strip navigation chips.
- Select status panel tabs.
- Select Work Table cards.
- Select Tool Registry chips.
- Select App Registry cards.
- Change the local theme selector.
- Display local fixture-backed status panels.
- Display local Work Table AI safe/blocked action chips.
- Display static assistant and console output.

Safe mock actions must not write files, call APIs, connect accounts, install software, deploy, place trades, run live AI, or start background services.

## Blocked Actions

Blocked actions:

- API calls.
- Account connections.
- Credential capture.
- Secret storage.
- Software installation.
- Deployment.
- Broker connection.
- Trading execution.
- Live AI execution.
- Destructive file operations.
- Background automation.
- React app changes without explicit approval.

Blocked actions may be displayed as text, but must not be executable buttons in the static dashboard.

## Approval-Required Future Actions

Future actions that require explicit DRY_RUN, approval, validator coverage, and checkpoint reports:

- Running validators from the dashboard.
- Generating reports from the dashboard.
- Writing checkpoint files from the dashboard.
- Starting local automation.
- Persisting operator notes.
- Reading local project files through a UI.
- Connecting to local service adapters.
- Invoking AI-assisted review.

Approval-required does not mean pre-approved. It means blocked until a future stage explicitly approves the exact scope.

## Fixture-Only Action Display

Fixture-only action display means:

- Local mock fixture data can be read.
- Static action labels can be shown.
- Safe and blocked action categories can be displayed.
- Approval-required flags can be displayed.

Fixture-only action display does not mean:

- A live action can run.
- A tool can install.
- A credential can be read.
- A service can deploy.
- A broker or trading path can execute.

## Assistant Rail Send Button

The assistant rail `Send` button is mock-only.

Allowed behavior:

- Update local preview text.
- Keep the interaction inside the static page.

Blocked behavior:

- Sending prompts to any service.
- Calling live AI.
- Writing files.
- Persisting messages.
- Connecting accounts.
- Reading secrets.

## Work Table AI Safe And Blocked Action Display

The Work Table AI panel may display:

- Safe mock actions.
- Blocked actions.
- Source references.
- Approval-required flags.
- Local fixture metadata.

The Work Table AI panel must remain read-only until a separate approved stage defines a safe local execution model.

## Future APPLY Escalation Boundaries

Any future APPLY action must define:

- Exact files to edit.
- Exact data source.
- Whether the action is read-only or write-capable.
- Required validator.
- Required checkpoint report.
- Human approval state.
- Stop condition.

If an action touches APIs, secrets, deployment, broker/trading execution, or live AI execution, it remains blocked until separate governance exists.

## Safety Statement

This registry introduces no APIs, secrets, installs, deployment, broker/trading execution, live AI execution, or dashboard code behavior.
