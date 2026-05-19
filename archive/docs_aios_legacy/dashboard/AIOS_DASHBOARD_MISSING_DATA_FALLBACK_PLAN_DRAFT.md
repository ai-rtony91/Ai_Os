# AI_OS Dashboard Missing Data Fallback Plan Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.14 - Dashboard Status Implementation Readiness

## Purpose

Plan fallback behavior for future dashboard implementation when required status data is missing, stale, invalid, or conflicting.

## Fallback States

- UNKNOWN: source missing or not inspected
- STALE: source exists but appears outdated
- INVALID DATA: source content is malformed or unsupported
- MISMATCH: two or more sources conflict
- BLOCKED: safety, validator, or approval state prevents next action

## Display Rules

- Show the fallback state and source path.
- Do not hide missing data behind optimistic defaults.
- Do not infer PASS from absence of evidence.
- Keep the next safe operator action visible when available.

