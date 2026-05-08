# AI_OS AI Assistant Future API Adapter Boundary Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.18 - AI Assistance Core Foundation

## Purpose

Define the future boundary for connecting AI Assistance to an AI provider after separate approval.

## Current Stage

No live AI API is connected in Stage 12.18. OpenAI, Azure OpenAI, Claude, and other live providers are out of scope.

## Future Adapter Requirements

A future AI API adapter must:

- require separate DRY_RUN and APPLY approval
- keep API keys and secrets outside browser code
- avoid direct dashboard-to-provider calls unless separately approved through a secure design
- return guidance and explanations only
- avoid autonomous execution
- avoid broker, trading, database, deployment, and destructive action paths
- expose clear unavailable, failed, and UNKNOWN states

## Blocked

- Browser-stored API keys
- Unapproved provider calls
- Secret logging
- Tool execution without approval
- Automatic file repair
- Trading or broker execution

