# AI_OS AI Assistant Safety Rules Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.18 - AI Assistance Core Foundation

## Purpose

Define safety and approval rules for AI Assistance.

## Blocked Assistant Actions

- Delete files.
- Move files.
- Rename files.
- Overwrite files.
- Read or store secrets.
- Add API keys.
- Connect OpenAI, Azure OpenAI, Claude, or any live AI API.
- Connect brokers.
- Connect a real database.
- Use external APIs.
- Create live trading code.
- Place trades.
- Modify protected root governance files.
- Deploy anything.
- Edit dashboard HTML, CSS, or JavaScript without explicit approval.
- Perform autonomous APPLY, commit, push, or repair.

## Human Approval Required

Human approval is required before:

- APPLY
- commit
- push
- dashboard code edits
- external API adapter work
- AI API integration
- database/backend integration
- deployment
- protected file edits

## Default State

AI Assistance defaults to local mock guidance only.

