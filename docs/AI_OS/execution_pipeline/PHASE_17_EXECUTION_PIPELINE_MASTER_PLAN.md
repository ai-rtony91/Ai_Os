# Phase 17 Execution Pipeline Master Plan

Status: DRY_RUN design and fixture scaffold

## Purpose

Phase 17 turns the Phase 16 OpenAI planner pipeline preview into a structured AI_OS execution pipeline design.

Phase 16 proved a local-only path from fake goal to planner result, Codex packet draft, worker assignment preview, validator chain preview, approval inbox preview, commit package preview, clean-state verifier preview, and real OpenAI API boundary. Phase 17 organizes that preview into reusable execution pipeline contracts and stage boundaries.

## What Phase 17 Does

Phase 17 defines:

- 17.1 Automatic Packet Generator
- 17.2 Worker Router
- 17.3 Validator Dispatcher
- 17.4 Approval Engine
- 17.5 Execution Supervisor

It creates docs, schemas, fixtures, and a local DRY_RUN preview runner. The runner converts one fake goal into a full execution supervisor preview without live autonomy.

## What Phase 17 Does Not Do

Phase 17 does not:

- call OpenAI.
- request or store API keys.
- create or read `.env`.
- install packages.
- make network calls.
- write real approval inbox state.
- write telemetry runtime state.
- modify Night Supervisor.
- touch broker, OANDA, live trading, real orders, or webhooks.
- commit, push, merge, rebase, or force push.

## OpenAI API Boundary

Real OpenAI API work remains blocked. A future real adapter requires a separate human-approved packet with dry-run first, no-write validation, environment-variable-only configuration, redaction, timeout, retry, audit, and fail-closed behavior.

## Copy-Paste Reduction

Phase 17 reduces future manual relay by generating a complete packet lifecycle preview from one goal:

```text
goal -> packet draft -> worker assignment -> validator chain -> approval preview -> commit package preview -> clean-state verifier -> supervisor state
```

The operator still controls APPLY, commit, push, merge, API keys, runtime, and trading decisions.

## Human-Controlled Safety Gates

Validator output, preview output, and generated packets are evidence only. They do not approve APPLY, commit, push, merge, real API calls, broker work, OANDA, or live trading.

## Future 17.6+ Ideas

Out of scope for this pack:

- 17.6 real adapter DRY_RUN design.
- 17.7 approval-gated packet writer.
- 17.8 dashboard projection.
- 17.9 operator queue integration.
- 17.10 real API adapter APPLY packet.
