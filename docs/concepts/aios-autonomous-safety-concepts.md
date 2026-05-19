# AIOS Autonomous Safety Concepts

Status: Canonical concept summary
Last reviewed: Phase 188A

## Purpose

This document preserves the useful safety doctrine from the legacy `docs/AI_OS/autonomous` planning drafts. It defines the approved boundaries for autonomous AI_OS behavior without depending on the legacy draft folder.

## Autonomy Boundary

AI_OS autonomy is limited to observe, plan, report, validate, and recommend. It may inspect repository state, detect gaps, identify stale reports, inventory validators, propose repair plans, and recommend rollback checkpoints. It must not apply repairs or make destructive changes without explicit operator approval.

Autonomous workflows must keep missing facts marked as `UNKNOWN`, conflicting evidence marked as `MISMATCH`, and unverified claims marked as `INVALID DATA`.

## Stop Conditions

AI_OS must stop and escalate when any of these conditions are present:

- Missing approval for a required gate.
- Protected action detected.
- Secret, credential, private key, or security setting risk.
- Broker, OANDA, webhook, live trading, or real order path detected.
- MISMATCH evidence.
- INVALID DATA.
- Unknown critical path fact.
- Dirty working tree outside the approved scope.
- Validator failure that affects the requested action.

Escalation must include the blocker, evidence, and exact next safe action.

## Approval Gates

Explicit human approval is required before:

- APPLY.
- Commit.
- Push.
- Merge.
- Delete, move, rename, overwrite, reset, clean, or force push.
- Secret, credential, broker, security, or trading changes.
- Protected root governance edits.

If approval is required and missing, the status is `BLOCKED`.

## Repair Planning

Autonomous repair planning may produce DRY_RUN reports only. A repair proposal should include:

- Detected issue.
- Evidence path.
- Affected files.
- Proposed action.
- Protected action flag.
- Approval requirement.
- Rollback or checkpoint reference.
- Next safe action.

Repair APPLY is blocked until the operator reviews the DRY_RUN, confirms the affected scope, and grants explicit approval.

## Destructive Action Block

AI_OS must not automatically delete, move, rename, overwrite, reset, clean, merge, push, force push, or change credentials/security settings. Destructive repair must be reported and escalated to the operator.

## Checkpoints And Ledgers

Major DRY_RUN and APPLY workflows should leave checkpoint evidence. Checkpoints and progress ledgers should capture stage, task ID, planned steps, completed steps, status, blocker, next action, checkpoint file, commit hash when available, and git status.

Missing checkpoint evidence is a blocker for autonomous continuation when a checkpoint is required by the workflow.

## Trading Safety

Autonomous workflows must not connect brokers, place trades, enable live trading, execute real webhooks, or introduce LLM decisioning into live order paths. Trading-related autonomy is limited to paper-only planning, reporting, telemetry, and validation when explicitly scoped.
