# AI_OS OpenAI CLI Bridge Boundary

Purpose:
Define how the OpenAI CLI may later support repeatable terminal API work for AI_OS without bypassing Codex, AI_OS safety gates, or human approval.

## Role Split

OpenAI CLI:

- repeatable terminal API work
- future connectivity smoke tests
- controlled Responses API calls
- local JSON/report output after approval

Codex:

- repo execution
- code and docs changes
- judgment-heavy diffs
- validation
- commit and PR lanes after explicit approval

## Current Boundary

This Phase 18.2 pack does not call OpenAI, ask for an API key, create `.env`, install packages, use Admin APIs, create service accounts, or touch secrets.

The CLI readiness wrapper may check:

- whether the `openai` command exists
- whether `OPENAI_API_KEY` exists as an environment variable
- whether forbidden repo secret files exist

The wrapper must never print API key values.

## Blocked

- Admin APIs are blocked.
- Service account creation is blocked.
- `.env` creation is blocked.
- API keys must never be printed or committed.
- Service-account JSON files must never be created or committed.
- Broker, OANDA, live trading, and Pi GPIO/motor paths remain blocked.

## Future Use

Future OpenAI CLI work must be separately approved. The first live step must be a tiny Responses API smoke test for connectivity only, with timeout, redaction, no repo mutation, no autonomy, and no Night Supervisor dispatch.

