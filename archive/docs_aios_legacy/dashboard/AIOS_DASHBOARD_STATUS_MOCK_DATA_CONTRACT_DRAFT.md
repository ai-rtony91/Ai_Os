# AI_OS Dashboard Status Mock Data Contract Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.14 - Dashboard Status Implementation Readiness

## Purpose

Define the example JSON shape for future dashboard status fixtures. These fixtures support planning and preview readiness only.

## Top-Level Contract

```json
{
  "generated_at": "YYYY-MM-DDTHH:mm:ss",
  "phase": "Phase 12",
  "stage": "Stage 12.14",
  "overall_status": "UNKNOWN",
  "validator_health": {},
  "progress": {},
  "checkpoint": {},
  "safety": {},
  "next_action": {}
}
```

## Status Values

Allowed status values:

- PASS
- WARN
- FAIL
- UNKNOWN
- STALE
- BLOCKED
- COMPLETE
- PENDING_APPLY

## Rules

- Fixtures must not contain secrets, tokens, account IDs, or broker data.
- Fixtures must not imply live trading readiness.
- Fixture values should be clearly marked as examples.

