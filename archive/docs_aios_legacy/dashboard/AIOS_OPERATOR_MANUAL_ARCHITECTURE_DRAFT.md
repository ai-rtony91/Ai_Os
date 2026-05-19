# AI_OS Operator Manual Architecture Draft

## Purpose

This draft defines the DRY_RUN-only operator manual architecture for future AI_OS cockpit usability. It does not create production dashboard UI or dashboard outputs.

Dashboard production outputs require separate approval.

## Onboarding Philosophy

The operator manual should help a beginner understand the cockpit without encouraging unsafe actions. Guidance should explain what the dashboard shows, what remains blocked, and what the next safe action means.

## Operator Learning Flow

The future manual may guide the operator through:

1. system status
2. validator state
3. protected-file status
4. alert severity
5. daily analytics
6. Morning Brief
7. trading readiness boundaries
8. next-safe-action guidance

## Contextual Explanations

Contextual explanations should answer why a panel matters, what changed, what is safe to inspect, and what remains blocked.

## Safe-Mode Explanations

Safe-mode explanations must state that the dashboard is a read-only dashboard unless a separate stage approves output writing or execution behavior.

## Validator Explanation System

Validator explanations should translate PASS, WARN, FAIL, BLOCKED, REVIEW REQUIRED, READY, and INFO into operator-readable meaning.

## Alert Explanation System

Alert explanations should identify the affected area, likely source, severity, and recommended next safe action without implying autonomous remediation.

## What Changed Concepts

The future manual may include a "what changed?" section for new files, changed files, validator results, protected-file status, and boundary status.

## Beginner And Operator Modes

Beginner mode may include more plain-language explanation. Operator mode may show concise summaries, direct evidence, and validation status.

## Low-Noise Guidance Philosophy

Manual guidance should be concise, non-intrusive, and focused on operator decisions. It should not create noisy popups, fake urgency, or hidden actions.

## Future Stage 44

Future Stage 44 may define static manual content fixtures or panel help fixtures. No production dashboard output is approved here.
