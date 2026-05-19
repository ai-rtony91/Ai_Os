# AI_OS Dispatcher and Orchestration Concepts

Status: canonical concept summary extracted from legacy `docs/AI_OS/dispatcher` and `docs/AI_OS/orchestration`

## Purpose

This document summarizes dispatcher and orchestration concepts from legacy `docs/AI_OS`. It is a bridge document for human review, not an automation spec.

## Terminology

Current working interpretation:

- Orchestration is the broader control model.
- Dispatcher is a subsystem concept for packet routing and runtime state.
- Operator control remains above both.

This terminology is not fully settled. MAIN CONTROL should decide whether `dispatcher` remains an active subsystem name or becomes historical vocabulary.

## Core Concepts

The useful concepts are:

- work packets define units of work,
- queues/folders hold packet state,
- worker registry defines available worker roles,
- locks prevent overlapping file ownership,
- approval inbox records human-gated decisions,
- validators check safety before and after APPLY,
- commit packages recommend exact-file staging,
- summaries show status but should not own truth.

## What Became Canonical

Recent cleanup made these canonical in `automation/orchestration`:

- worker registry under `workers/`,
- work packets under `work_packets/`,
- command queue under `command_queue/`,
- approval inbox under `approval_inbox/`,
- validators under `validators/`,
- commit packages under `commit_packages/`,
- control and health summaries under dedicated subfolders.

Old root fallback examples were archived to `archive/orchestration_legacy/root_examples/`.

## Current Doctrine

Orchestration should:

- be display-first and approval-gated,
- keep worker boundaries clear,
- avoid overlapping edits,
- require validators before commit readiness,
- keep commit and push manual unless separately approved.

Orchestration should not:

- launch uncontrolled workers,
- run background loops without approval,
- hide state in generated reports,
- bypass human approval,
- touch broker/live trading paths.

## Planned/Future Ideas

- one front-door operator loop,
- clearer packet lifecycle,
- consolidated validator chain,
- archive of v1 examples after direct dependencies are removed,
- dashboard visibility into orchestration state.

## Human-Review Items

- Decide dispatcher vs orchestration vocabulary.
- Decide whether v1 examples are fixtures, canonical docs, or archive candidates.
- Decide how much state belongs in `automation/orchestration` versus reports.
- Decide which display scripts remain active operator commands.
