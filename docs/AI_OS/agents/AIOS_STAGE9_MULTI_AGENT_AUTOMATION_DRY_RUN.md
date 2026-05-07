# AIOS Stage 9 Multi-Agent Automation DRY_RUN

Status: Draft scaffold

## Purpose

Define how Codex, ChatGPT, Claude, and future agents may support AI_OS work while preserving human control.

## Agent Roles

- Codex: local repo implementation, dry-run reports, scaffold creation after approval.
- ChatGPT operator role: planning, review, prompting, and human-readable workflow support.
- Claude support role: optional secondary reasoning and documentation review.
- Human operator: final approval authority for protected actions.

## Blocked Agent Actions

- Delete, move, or rename files without explicit approval.
- Modify secrets or credentials.
- Connect brokers or place trades.
- Enable live trading.
- Push, merge, reset, or clean without approval.
- Modify protected root governance files unless explicitly required and reported.

## Audit Requirements

Every delegated action must produce a record of task, inspected files, changes, errors, unknowns, and next safe action.
