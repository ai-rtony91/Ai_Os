# AI_OS Self-Upgrading Boundary

Purpose:
State the hard boundary for AI_OS self-improvement.

AI_OS self-improvement is evidence-based. It is not uncontrolled self-modification.

## Allowed

- Read approved traces and reports.
- Summarize recurring failures.
- Generate eval cases.
- Rank improvement recommendations.
- Draft Codex handoff packets.
- Propose harness changes.
- Create docs, schemas, fixtures, and local-only preview reports in approved lanes.

## Blocked

- Automatic merge.
- Automatic push.
- Automatic commit without explicit approval.
- Automatic APPLY without explicit approval.
- Uncontrolled edits to `AGENTS.md` or governance docs.
- Live OpenAI API use.
- API key handling.
- `.env` creation or reading.
- Package installs.
- Network calls.
- Runtime telemetry writes.
- Real approval inbox writes.
- Night Supervisor modification.
- Broker, OANDA, live trading, or real orders.

## Human Approval

Human approval remains required for:

- APPLY packets
- commit
- push
- PR creation
- merge
- real OpenAI API adapter work
- any future runtime automation

Live trading remains blocked. The real API adapter remains separately gated.
