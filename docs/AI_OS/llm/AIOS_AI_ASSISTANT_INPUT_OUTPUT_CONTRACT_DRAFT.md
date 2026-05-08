# AI_OS AI Assistant Input Output Contract Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.18 - AI Assistance Core Foundation

## Purpose

Define the safe input and output contract for future AI Assistance behavior.

## Allowed Inputs

- latest checkpoint summary
- progress ledger row
- validator health summary
- safety status
- current stage and task name
- operator-entered question
- approved local mock assistant fixture
- approved local dashboard status fixture

## Blocked Inputs

- secrets
- API keys
- broker tokens
- private keys
- recovery keys
- live broker account data
- database credentials
- unapproved external API responses
- private browser or account session data

## Allowed Outputs

- explanation
- next safe action
- safety reminder
- checkpoint summary
- validator result summary
- command explanation
- blocked action warning

## Output Rules

- Output must label UNKNOWN facts as UNKNOWN.
- Output must not imply an action was performed.
- Output must not claim approval was granted unless evidence shows approval.
- Output must not issue live trading, broker, deployment, or destructive commands.

