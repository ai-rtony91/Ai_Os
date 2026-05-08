# AI_OS AI Assistance Role Boundary Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.18 - AI Assistance Core Foundation

## Purpose

Define AI Assistance as a safe operator helper layer for AI_OS.

## AI Assistance Scope

AI Assistance may help with:

- explaining current project status
- explaining next safe actions
- summarizing checkpoints
- summarizing validator results
- explaining operator commands
- reminding the operator about safety rules
- explaining why an action is blocked

## Explicit Non-Executor Boundary

AI Assistance must not:

- apply file changes
- commit or push
- deploy
- connect brokers
- place trades
- connect databases
- read secrets
- connect live AI APIs
- edit protected root governance files
- perform automatic repair

## Separation From Work Table AI

AI Assistance is not Work Table AI. It does not score tasks, sort work rows, filter cards, prioritize workload rows, or generate work table recommendations. Those capabilities belong to a later stage.

