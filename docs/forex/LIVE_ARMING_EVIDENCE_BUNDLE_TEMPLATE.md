# Live Arming Evidence Bundle Template

Status: sanitized template only. This file contains no live account data and no credential material.

## Evidence Bundle Requirements

| Evidence item | Required state |
|---|---|
| broker sandbox or demo proof | Present and sanitized. |
| risk gate result | PASS, with pair allowlist, spread, margin, position size, max loss, and stop-loss evidence. |
| kill switch state | Active before arming. |
| daily loss cap state | Active before arming. |
| approval hash verification | Verified against Human Owner approval field. |
| account mode confirmation | Explicit paper/live mode confirmation present. |
| order payload preview | Sanitized preview only, no broker order identifier. |
| fill verification plan | Status-only plan present. |
| position close plan | Status-only plan present. |
| final report path | Sanitized report path present. |

## Evidence Exclusions

The evidence bundle must not contain API keys, tokens, passwords, private keys, account identifiers, broker order identifiers, raw live payloads, private account data, screenshots with private data, or unredacted broker data.

## Required Evidence Events

1. Request review.
2. Risk gate result.
3. Evidence bundle review.
4. Manual arming decision.
5. Terminal result.
6. Final disarm.
7. Final trade report.

Each event must be sanitized, redacted where needed, and marked as evidence only. Evidence does not approve live execution.
