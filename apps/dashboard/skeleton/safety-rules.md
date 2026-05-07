# Dashboard Safety Rules Reference

## Purpose

This file records safety boundaries for dashboard UI work. It is reference-only and does not change the working dashboard.

## Required Boundaries

- No backend.
- No API calls.
- No credentials.
- No OpenAI key.
- No Codex connection.
- No persistence.
- No localStorage or sessionStorage persistence.
- No report writer activation.
- No telemetry writer activation.
- No dashboard writer activation.
- No startup task.
- No broker/trading automation.
- No live order path.
- No order placement.
- No webhook firing.
- No strategy activation.

## Assistant Mockup Rules

- ChatGPT lane is a visual mockup only.
- Codex lane is a visual mockup only.
- No assistant connection is active.
- No prompt, token, API key, credential, or private user data should be stored in the UI.

## Future APPLY Rule

Any future update to `apps/dashboard/AIOS_STATIC_PREVIEW.html` requires explicit approval, validation, and git status review.

Skeleton files do not grant approval to modify the working dashboard.
