# AI_OS Dashboard Validator Health Input Contract Draft

Status: DRAFT
Phase: Phase 12 Pack C
Stage: 12.12 - Dashboard Status Wiring Readiness

## Purpose

Define the planned dashboard input contract for validator health summaries under Reports/health.

## Required Health Fields

- Overall status
- Validators discovered
- Validators run
- PASS count
- WARN count
- FAIL count
- SKIPPED count
- Blockers
- Next safe action

## Status Rules

- Any FAIL means dashboard status should show blocked.
- WARN means dashboard status should show review required.
- PASS with zero validators is INVALID DATA.
- Missing health report means UNKNOWN, not PASS.

## Boundary

This draft does not authorize running validators from the dashboard.

