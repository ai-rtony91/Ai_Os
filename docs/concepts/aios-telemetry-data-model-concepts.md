# AI_OS Telemetry Data Model Concepts

Status: canonical concept summary
Sources: `docs/AI_OS/telemetry`

## Purpose

This document preserves AI_OS telemetry doctrine without enabling telemetry collection, persistence, writers, browser storage, remote analytics, broker data capture, or live trading.

## Evidence Model

Telemetry values must be evidence-backed. Acceptable evidence includes repository files, git output, committed reports, committed fixtures, explicit operator-provided QA results, and rerun validator output.

Use `UNKNOWN` when evidence is absent, partial, stale, or not directly verified. Partial evidence must be labeled `PARTIAL`, not promoted to complete lifetime truth.

Do not infer:

- lifetime time spent from commit timestamps.
- lifetime byte totals from line counts.
- missing QA results.
- missing validator runs.
- missing push events.
- blocker history not backed by evidence.

## Safe Field Classes

Future non-live telemetry may describe:

- session IDs.
- timestamps.
- repo and branch state.
- validator names and results.
- file counts and byte counts when evidence-backed.
- progress percentages.
- operator notes.
- dashboard render or fixture health.
- approval prompt visibility and decision labels.
- compliance or privacy gate status.

## Blocked Data

Telemetry must not include:

- credentials, tokens, API keys, passwords, private keys, recovery keys, SSH keys, OAuth secrets.
- browser profile data or credential store paths.
- private user material or uncontrolled screen contents.
- broker account identifiers.
- broker data.
- live market data.
- order details.
- live order path data.
- trade execution decisions.
- payment card data, bank data, tax identifiers, or app-store credentials.

## Storage Boundary

Potential future storage paths such as `Reports/telemetry/` require a separate approved APPLY stage.

No current telemetry doctrine authorizes:

- background telemetry writers.
- file watchers.
- API calls.
- localStorage or sessionStorage.
- service-worker storage.
- remote analytics.
- deployment telemetry.
- broker/trading telemetry.
- live AI telemetry.

## User, App, And Business Split

User telemetry may support safety, onboarding, workflow clarity, accessibility, and operator control.

App telemetry may support dashboard health, render reliability, validator visibility, accessibility checks, and operator safety.

Business telemetry may support product planning, packaging, licensing readiness, support demand review, and compliance gate tracking.

Each class requires an approved field allowlist, privacy boundary, consent model, retention rule, deletion workflow, and review process before persistence.

## Error And Mismatch Reporting

Telemetry/reporting plans must keep mismatches visible. Failed validators, unknown repo state, stale evidence, duplicate reports, push failures, permission errors, and credential warnings must be reported rather than hidden.

Allowed labels include `PASS`, `REVIEW`, `NEEDS_REFACTOR`, `BLOCKED`, and `INVALID DATA`.

