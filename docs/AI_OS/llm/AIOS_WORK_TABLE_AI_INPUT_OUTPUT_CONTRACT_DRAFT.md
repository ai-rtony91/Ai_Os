# AI_OS Work Table AI Input Output Contract Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.19 - Work Table AI Foundation

## Purpose

Define safe inputs and outputs for Work Table AI planning.

## Allowed Inputs

- work card id
- work card label
- work card title
- work card description
- current status
- blocker text
- checkpoint evidence
- progress evidence
- validator evidence
- local mock Work Table AI fixture

## Blocked Inputs

- secrets
- API keys
- broker tokens
- private keys
- recovery keys
- live broker account data
- database credentials
- unapproved external API responses
- AI Assistance conversational state unless explicitly mapped later

## Allowed Outputs

- interpreted status
- confidence
- score
- priority tier
- recommended next review target
- reason
- human approval required flag

## Output Rules

- Recommendations are suggestions only.
- Human approval is required before action.
- UNKNOWN evidence must remain UNKNOWN.
- Scores must not imply permission to APPLY, commit, push, deploy, trade, or connect services.

