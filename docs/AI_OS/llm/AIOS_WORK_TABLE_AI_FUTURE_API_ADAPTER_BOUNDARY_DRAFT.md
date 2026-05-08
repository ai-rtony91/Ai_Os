# AI_OS Work Table AI Future API Adapter Boundary Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.19 - Work Table AI Foundation

## Purpose

Define the future boundary for connecting Work Table AI to an AI provider after separate approval.

## Current Stage

Stage 12.19 uses planning docs and local mock fixtures only. No OpenAI, Azure OpenAI, Claude, or live AI provider is connected.

## Future Adapter Requirements

A future adapter must:

- require separate DRY_RUN and APPLY approval
- keep API keys and secrets outside browser code
- return suggestions only
- avoid autonomous execution
- avoid broker, trading, database, deployment, and destructive paths
- mark provider failures as UNKNOWN or ERROR

## Blocked

- Browser-stored API keys
- Unapproved provider calls
- Secret logging
- Automatic APPLY
- Automatic commit or push
- Trading or broker execution
- Direct database connection from browser code

