# Phase 18.13-18.18 Night Supervisor Runway

This runway moves AI_OS from the passed Phase 18.12 dispatcher validation toward a future full overnight candidate without starting Night Supervisor, resuming Paper SOS, calling OpenAI, or touching runtime state.

AI_OS priority remains `TRUSTED_PROVEN_PROFITABILITY`.

## Stage Summary

- Phase 18.13: Dispatcher routes work to `NIGHT_SUPERVISOR_PREVIEW` only. Runtime start is blocked.
- Phase 18.14: Corrected Paper SOS / Night Supervisor resume packet is DRAFT_ONLY and fails closed unless cwd, Python cwd, git root, profile, locks, and dirty tree checks pass.
- Phase 18.15: Future short controlled run boundary only. One cycle or maximum 10 minutes, report-only, not 12h.
- Phase 18.16: Controlled run report plus red-team and failure review template.
- Phase 18.17: Future 1-2 hour supervised run only after 18.15 and 18.16 pass.
- Phase 18.18: Full overnight candidate criteria only after every previous gate passes.

## Hard Blocks

- No Night Supervisor runtime start.
- No Paper SOS resume.
- No OpenAI/API call.
- No telemetry/control/approval inbox write.
- No broker/OANDA/live trading.
- No Pi GPIO/motor action.
- No secrets printed and no `.env`, `project.json`, or `service-account.json`.
- No commit or push.

## Runway Principle

Every stage must prove context, stop controls, clean-state behavior, and profitability priority before longer autonomy is considered.

