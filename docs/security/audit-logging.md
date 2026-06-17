# Audit Logging Specification

Status: baseline scaffold, pending human review.

## Purpose

AI_OS should preserve enough evidence to reconstruct security-relevant actions, approvals, validations, and execution mode transitions.

## Events To Log

| Event | Required Fields |
|---|---|
| DRY_RUN started | timestamp, actor, command/task, files inspected |
| APPLY requested | timestamp, actor, requested change, affected files |
| APPLY approved | timestamp, approver, approval scope |
| File modified | timestamp, actor/tool, path, summary |
| Validation run | timestamp, command, result, output location |
| Security check run | timestamp, check/tool, result |
| Secret detection | timestamp, path, action taken |
| CI run | timestamp, branch/commit, result |
| Rejected action | timestamp, reason, requested action |
| Trading/broker blocked action | timestamp, reason, requested action |

## Single Live Micro-Trade Exception Audit Boundary

Audit logs for any future Single Live Micro-Trade Exception must be append-only and sanitized.

Allowed audit events are limited to:
- request
- review
- approval
- rejection
- expiry
- arming
- kill switch state
- daily loss gate
- credential-handle release or denial
- order terminal result
- final disarm

Only redacted identifiers and pass/fail facts are allowed. Audit logs must not contain secrets, account IDs, broker order IDs, live payloads, raw request bodies, credential values, private account data, or secret material.

## Minimum Requirements

- Logs must not contain secrets.
- Logs must not contain broker credentials.
- Logs must distinguish DRY_RUN from APPLY.
- Failed validation must be visible.
- Human approval must be attributable.
- Security-relevant actions must be reviewable.

## Retention

Retention policy is pending human review.
