# AI_OS Morning Brief Text Contract Draft

## Purpose

This draft defines the required structure for future AI_OS Morning Brief text output.

## Contract Scope

The contract describes the sections and fields a future Morning Brief text generator should print or write after separate approval.

## Contract Non-Scope

No real Morning Brief files are written yet.

No apps launch.

No startup automation is enabled.

No trading or broker content is included.

## Required Brief Sections

Future Morning Brief text should include:

- Header
- Repo State
- Workflow State
- Approval State
- Dashboard State
- Snapshot Boundary State
- Report Boundary State
- Pending Approvals
- Warnings
- Next Safe Action

## Required State Fields

Required state fields should include repo path, branch, git status, workflow state, dashboard state, Morning Brief state, approval queue state, and snapshot boundary state.

## Required Warning Fields

Required warning fields should include current warnings, blocked conditions, dirty git status, missing components, protected-file changes, and stale or invalid evidence.

## Required Approval Fields

Required approval fields should include APPLY approval status, git checkpoint approval status, protected file approval status, high-risk approval status, and blocked action categories.

## Required Next Action Fields

Required next action fields should include the exact next safe command or review instruction, the stop condition, and whether human approval is required.

## Protected Data Restrictions

Morning Brief text must not include secrets, credentials, broker tokens, private keys, recovery keys, uncontrolled screen contents, broker execution data, live trading data, or private user material.

## Future Stage 16

Future Stage 16 may propose a DRY_RUN Morning Brief text generator. It must remain console-output-only unless separate approval authorizes a file-writing report helper.
