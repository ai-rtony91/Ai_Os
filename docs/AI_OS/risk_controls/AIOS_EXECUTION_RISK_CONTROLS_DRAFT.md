# AIOS Execution Risk Controls Draft

Status: Draft scaffold

## Purpose

Define minimum risk-control placeholders required before any execution-related automation can advance.

## Required Controls

- Paper-trading-only default state.
- Kill-switch requirement before order routing.
- Max-risk placeholder with UNKNOWN until approved values exist.
- Human approval gate before APPLY.
- Audit log requirement for every execution-related decision.
- Error logging requirement for failed validation.

## Stop Conditions

- Missing approval.
- Missing risk limit.
- Missing broker sandbox boundary.
- Missing webhook validation.
- Any live-trading path detected.
- Any real secret detected.
