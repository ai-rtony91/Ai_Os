# AI_OS Writer System Concepts

Status: canonical concept summary extracted from legacy `docs/AI_OS/writers`

Last reviewed: Phase 99 writers doc cleanup

## Purpose

This document summarizes AI_OS writer doctrine from the legacy writers planning folder. It is a concept and validation reference, not an active writer implementation and not approval to write files.

## Core Doctrine

Writer work in AI_OS means controlled, human-reviewed file population or report generation. The useful concepts from the legacy folder are:

- writer output must be previewed before any file write,
- output paths must be allowlisted before APPLY,
- protected root files must remain excluded unless a future prompt explicitly allows them,
- human approval is required before APPLY or any file population,
- every writer output needs source metadata, validation metadata, and a clear next safe action,
- no active writer should bypass the operator workflow,
- no live automation should run from writer planning docs,
- rollback and error logging must be planned before promotion.

## Boundaries

The writer system is planning-only until a future scoped APPLY explicitly promotes code or workflow behavior.

Allowed concepts:

- report writer input contracts,
- telemetry writer boundaries,
- dashboard writer boundaries,
- fixture and schema examples,
- validator chains,
- safe file population workflow,
- output preview and review summaries.

Blocked concepts:

- active writer execution without preview,
- protected root edits without explicit approval,
- secrets, credentials, API keys, broker/OANDA/webhook/live trading data,
- silent telemetry writes,
- dashboard writes outside approved paths,
- unvalidated generated output.

## Promotion Requirements

Before any writer moves from concept to implementation:

1. The input owner must be known.
2. The output path must be allowed.
3. The protected file exclusion check must pass.
4. The preview must show exact created or changed files.
5. The validator chain must pass.
6. The operator must approve APPLY.
7. Errors must be visible in the report and, if needed, in the project error log.

## Fixture Doctrine

Fixtures are examples for validator behavior. They should remain obviously non-production and should not contain secrets, credentials, live trading fields, or environment-specific hidden state.

Required fixture intent:

- demonstrate PASS and FAIL behavior,
- validate required output fields,
- validate blocked values,
- support review of schema boundaries.

## Current Cleanup Status

Phase 99 redirected the writer promotion planning validator to this canonical concept document. Other active status validators still reference individual legacy writer drafts and must be retired before `docs/AI_OS/writers` can move safely.

