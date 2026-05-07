# AI_OS Validator Naming Status Exit-Code Convention Draft

## Purpose

This draft defines naming, output, and exit-code conventions for future AI_OS validators and preview helpers.

No protected root files are edited by this draft. Human approval is required before adopting this convention as authoritative. This file creates no live automation.

## Naming Rules

- `Test-AiOs*.DRY_RUN.ps1` for validators.
- `Preview-AiOs*.DRY_RUN.ps1` for preview helpers.
- `Invoke-AiOs*.DRY_RUN.ps1` for router-style dry-run invocations.

## Output Rules

Each validator should print:

- task name
- mode
- repo root
- branch/status
- checks performed
- PASS/FAIL summary
- stop condition

## Exit-Code Rule

- `exit 0` only on full PASS.
- `exit 1` on FAIL.

## Writer Boundary

Validators must not write files unless separately approved. DRY_RUN validators inspect, parse, and report only.

## Boundary

This draft does not approve protected root file edits, does not grant human approval, and creates no live automation.
