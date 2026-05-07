# AI_OS Completion Percent Rules Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.15 - Development Metrics + Completion Dashboard Readiness

## Purpose

Define percent complete calculation rules for AI_OS workload, stage, and phase reporting.

## Formula

```text
percent_complete = completed_steps / planned_steps * 100
```

## Rules

- planned_steps must be greater than zero.
- completed_steps must not exceed planned_steps.
- Round display values to whole numbers unless a report requires more precision.
- If planned_steps is missing, zero, or invalid, percent_complete must be UNKNOWN.
- If completed_steps conflicts with report evidence, mark MISMATCH.

## Dashboard Display

- Show blocked status above percent complete.
- Show UNKNOWN if proof is missing.
- Do not display 100 percent unless checkpoint proof and completion status agree.

