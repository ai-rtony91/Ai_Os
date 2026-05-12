# AI_OS Local-Only Key Storage Plan

Status: APPLY scaffold
Mode: planning only

## Purpose

Define the future safety boundary for API keys and credentials without creating, storing, requesting, or exposing any real secret material.

## Current Rule

No API keys are used in this phase.

No secrets are created in this phase.

No Anthropic integration is enabled.

No OpenAI integration changes are made.

## Repository Boundary

Real keys must never be committed to this repository.

Real keys must not appear in:

- dashboard HTML
- dashboard CSS
- dashboard JavaScript
- dashboard mock data
- reports
- docs
- logs
- screenshots
- test fixtures

## Future Local-Only Options

The future approved storage option is UNKNOWN.

Possible future choices include:

- Windows Credential Manager
- user-level environment variables
- local untracked `.env` file outside committed scope

Any choice requires a separate DRY_RUN, user approval, and secret-handling checklist.

## Agent Boundary

ChatGPT may explain secret-handling rules.

Codex may create placeholder docs and validators only.

Claude may review documentation only.

No agent may receive, print, persist, validate, or transform real secrets.

## Redaction Rule

If suspected secret material is found, do not repeat it.

Use:

```text
REDACTED_SECRET_VALUE
```

Log the event with file path and context only after user approval.

## Next Safe Action

Keep all provider credentials blocked until a separate secrets-management DRY_RUN is approved.
