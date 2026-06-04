# AI_OS Responses API Smoke Test Plan

Purpose:
Define the future human-approved first live Responses API smoke test for AI_OS.

## Status

Status: boundary only. No live API call is implemented here.

## Smoke Test Conditions

The future smoke test must:

- be separately human-approved
- make one tiny Responses API call
- prove connectivity only
- avoid repo mutation
- avoid file writes except an approved smoke-test report
- avoid printing API keys
- avoid `.env`
- avoid package install
- use environment variables only
- use timeout behavior
- redact sensitive values
- fail closed on uncertainty

## Blocked Outcomes

The smoke test must not:

- generate autonomy
- generate dispatch authority
- start Night Supervisor
- write telemetry
- write approval inbox state
- call broker, OANDA, or live trading systems
- touch Pi GPIO or motor control
- commit, push, merge, rebase, or force push

## Next Step After Smoke Test

If connectivity succeeds, the next packet may propose a no-write real adapter that asks the Responses API for a structured packet draft and stores only an approved report. Codex still owns repo execution.

