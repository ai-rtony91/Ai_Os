# AI_OS Operator Automation Roadmap

## Purpose

This roadmap defines the first operator workflow automation layer for AI_OS.

The layer reduces manual relay work by organizing DRY_RUN routing, APPLY routing, validator order, approval handoff, exact-file promotion, morning execution packets, and next safe action generation.

This is not autonomous execution.

## Operating Model

AI_OS remains:

- operator approved
- local-first
- DRY_RUN-first
- merge-blocked unless approved
- commit-blocked unless approved
- push-blocked unless approved

## Workflow Layers

The operator workflow layer is made of:

- Morning Execution Packet
- APPLY Routing Chain
- Validator Chain Routing
- Guided Action Queue
- Safe Session Resume
- Operator Fatigue Reduction

Each layer produces readable evidence for the operator. None of the layers execute merge, commit, push, broker, OANDA, API key, or live trading behavior.

## Human Approval Boundary

Human approval is required before:

- APPLY
- merge
- commit
- push
- protected file work
- broker, OANDA, API key, real order, or live trading work
- startup automation
- background automation

## Automation Boundary

Allowed future behavior:

- prepare packets
- group evidence
- show queue state
- show validator sequence
- show blocked actions
- show next safe action

Blocked behavior:

- autonomous coding loops
- auto-commit
- auto-push
- merge execution
- startup tasks
- background daemons
- installs
- internet calls
- broker execution
- OANDA
- API key handling

## Roadmap Stages

1. Define mock data contracts.
2. Define DRY_RUN validator checks.
3. Render display-only dashboard state in a later approved UI phase.
4. Add operator-reviewed packet generation in a later approved phase.
5. Keep APPLY, merge, commit, and push as explicit operator actions.

## Next Safe Action

Review the Phase 44 scaffold, validate JSON and DRY_RUN validator output, then decide whether the docs and mock-data should be committed as an exact-file package.
