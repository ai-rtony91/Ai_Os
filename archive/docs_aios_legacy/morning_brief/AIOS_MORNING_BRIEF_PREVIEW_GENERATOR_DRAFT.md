# AI_OS Morning Brief Preview Generator Draft

## Purpose

This draft explains the first DRY_RUN Morning Brief preview generator concept for AI_OS.

The generator previews intended Morning Brief output before any Morning Brief file can be written.

## Preview Scope

This stage is console-output-only.

The preview generator may print proposed target path, source inputs, Morning Brief sections, blocked fields, approval requirement, and validator to run after a future write.

## Preview Non-Scope

No Morning Brief file is written.

No startup task is created.

No app/window/browser launch occurs.

No telemetry writer, report writer, broker integration, trading execution, scheduled task, service, daemon, agent, startup automation, or credential access is created.

## Proposed Target Path

Future Morning Brief output may target:

`Reports\morning_brief\MORNING_BRIEF_yyyy-MM-dd_AI_OS.md`

The target path is conceptual in this stage.

## Proposed Morning Brief Sections

Future Morning Brief sections may include:

- Header
- Repo State
- Workflow State
- Approval State
- Dashboard State
- Report Preview State
- Telemetry Preview State
- Protected File Status
- Trading Execution Boundary Status
- Next Safe Action

## Blocked Fields

Blocked fields include:

- secrets
- credentials
- broker tokens
- private keys
- recovery keys
- live trading data
- uncontrolled screen contents

## Approval Requirements

Future APPLY writer requires separate approval.

Approval is required before any Morning Brief file write, DAILY_METRICS edit, CHECKPOINT_INDEX edit, production telemetry write, startup task, app launch, browser launch, broker/trading output, or credential-related handling.

## Startup Safety Rules

Morning Brief preview must not create startup tasks, scheduled tasks, services, daemons, agents, or startup automation.

Morning Brief preview must not launch apps, windows, or browsers.

## Future Stage 25

Future Stage 25 may propose a stricter Morning Brief preview schema validator or a dry-run Morning Brief content schema.

Future Stage 25 must not write Morning Brief files, create startup automation, or launch apps/browsers unless separate human approval explicitly changes scope.
