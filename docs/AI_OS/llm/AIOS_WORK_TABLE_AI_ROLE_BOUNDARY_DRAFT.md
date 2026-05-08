# AI_OS Work Table AI Role Boundary Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.19 - Work Table AI Foundation

## Purpose

Define Work Table AI as a separate intelligence layer for interpreting work table cards, rows, statuses, and priorities.

## Work Table AI Scope

Work Table AI may plan:

- work table card interpretation
- row or card status interpretation
- task scoring
- priority tiering
- sorting and filtering recommendations
- next review target recommendations
- mock explanations for work table state

## Non-Executor Boundary

Work Table AI must not:

- apply file changes
- commit or push
- deploy
- connect live AI APIs
- connect brokers
- place trades
- connect databases
- read secrets
- perform automatic repair
- edit dashboard code without explicit approval

## Separation From AI Assistance

AI Assistance is the operator helper layer. Work Table AI is the work table card and row intelligence layer. Stage 12.19 must not add general operator assistant behavior.

