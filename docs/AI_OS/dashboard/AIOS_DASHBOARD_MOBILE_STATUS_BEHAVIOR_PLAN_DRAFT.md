# AI_OS Dashboard Mobile Status Behavior Plan Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.16 - Dashboard Read-Only Mock Status Wiring

## Purpose

Plan mobile behavior for future read-only dashboard status cards.

## Mobile Layout Rules

- Collapse status cards into a single-column stack on narrow screens.
- Keep safety, validator failure, blocked status, and next action above lower-priority metrics.
- Prevent horizontal scrolling for status card content.
- Keep card labels short and scannable.
- Preserve existing sidebar and drawer behavior unless a later approved implementation explicitly changes it.

## Mobile Fallback Rules

- Show UNKNOWN when data is missing.
- Show INVALID DATA when JSON cannot be parsed.
- Show BLOCKED when safety or validation state prevents work.
- Keep the next safe action visible when available.

## Boundary

This document does not authorize edits to dashboard HTML, CSS, or JavaScript.

