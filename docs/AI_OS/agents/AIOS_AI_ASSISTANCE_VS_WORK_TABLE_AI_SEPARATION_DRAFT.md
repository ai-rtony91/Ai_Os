# AI_OS AI Assistance vs Work Table AI Separation Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.18 - AI Assistance Core Foundation

## Purpose

Document the separation between AI Assistance and Work Table AI.

## AI Assistance

AI Assistance is an operator helper layer.

Allowed scope:

- explain project status
- explain next safe action
- summarize checkpoints
- summarize validator results
- explain commands
- remind about safety rules
- explain blocked actions

AI Assistance does not execute actions.

## Work Table AI

Work Table AI is a later-stage intelligence layer for the work table.

Excluded from Stage 12.18:

- task scoring
- card or row intelligence
- status interpretation for sorting
- filtering recommendations
- prioritization logic
- work table-specific recommendation logic

## Boundary Rule

If a feature changes how work table rows or cards are scored, sorted, filtered, or recommended, it belongs to Work Table AI and must be planned in a later stage.

