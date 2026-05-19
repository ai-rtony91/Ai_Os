# AI_OS Alert Hierarchy And Color System Draft

## Purpose

This draft defines the future alert hierarchy and color system for AI_OS dashboard prototype planning.

Dashboard production outputs require separate approval.

## Alert States

Future dashboard alert states should include:

- FAIL
- BLOCKED
- WARN
- REVIEW REQUIRED
- READY
- INFO

## Visual Intensity Hierarchy

FAIL and BLOCKED states should carry the strongest visual intensity. WARN should be visible but less dominant. REVIEW REQUIRED should prompt human attention. READY and INFO should remain calm and low intensity.

## Color Restraint Philosophy

Color must be used sparingly. Alert colors should indicate operational meaning rather than decorate the UI.

## Operator Attention Priorities

Operator attention should prioritize:

1. protected-file risk
2. validator failure
3. blocked trading or execution readiness
4. stale dashboard data
5. telemetry or report boundary warnings
6. general informational state

## Suggested Color Concepts

Future color concepts may include:

- FAIL: restrained red
- BLOCKED: high-contrast red or magenta accent
- WARN: amber
- REVIEW REQUIRED: violet or blue accent
- READY: green
- INFO: muted cyan or neutral gray

## Glassmorphism Compatibility

Glassmorphism, glow, and dark mode concepts should not reduce alert readability or create false urgency.

## Future Stage 43

Future Stage 43 may define token names for alert colors. No production UI theme output is approved here.
