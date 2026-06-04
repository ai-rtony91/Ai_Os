# Phase 18.4 Latency Validation Report 001

Purpose:
Record the DRY_RUN validation target for AI_OS latency optimization doctrine.

## Required Principles

1. Process tokens faster.
2. Generate fewer tokens.
3. Use fewer input tokens.
4. Make fewer requests.
5. Parallelize.
6. Make your users wait less.
7. Don’t default to an LLM.

## Safety Result

- Trading Lab latency remains priority #1.
- Live trading remains blocked.
- Deterministic scripts come before LLMs for mechanical checks.
- Smaller models are only for low-risk bounded tasks.
- Stronger models are for safety, judge, planner, and profitability reasoning.
- Parallelization is limited to read-only or DRY_RUN work with non-overlapping files.
- APPLY remains one-at-a-time.
- User-facing progress must show current lane, blocker, and next safe action.
- Priority processing is future-only for high-value user-facing latency-sensitive requests.
- Priority processing is blocked for evals, batch jobs, ETL, nightly reports, telemetry bulk work, and routine background processing.
- Priority processing must not bypass approvals, validators, Trading Lab paper-only rules, broker/OANDA blocks, live-trading blocks, Pi GPIO/motor blocks, or clean-state checks.

## Blocked

No OpenAI call, API key, `.env`, package install, network call, broker, OANDA, live trading, Pi GPIO/motor, Night Supervisor runtime modification, commit, or push is approved by this pack.

