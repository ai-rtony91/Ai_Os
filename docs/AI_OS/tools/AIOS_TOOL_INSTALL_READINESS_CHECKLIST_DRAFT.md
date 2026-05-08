# AI_OS Tool Install Readiness Checklist Draft

## Purpose

Define the checklist that must be satisfied before any future tool install action is considered.

## Checklist

- Confirm the tool is needed for an approved AI_OS stage.
- Confirm existing local detection result is MISSING or NEEDS_CONFIG.
- Confirm install source is official and safe.
- Confirm no secrets, tokens, passwords, recovery codes, or API keys are requested.
- Confirm no broker, trading, or deployment path is enabled.
- Confirm operator explicitly approves install mode.
- Confirm installer command is reviewed before execution.
- Confirm rollback/uninstall notes are documented where practical.
- Confirm a checkpoint/report will be written after install validation.

## Blocked By Default

- `winget install`
- `npm install -g`
- `choco install`
- account login automation
- OAuth automation
- browser credential capture
- broker/API connection
- deployment

## DRY_RUN Rule

Install readiness can be planned in DRY_RUN, but installation requires a separate explicit APPLY approval.
