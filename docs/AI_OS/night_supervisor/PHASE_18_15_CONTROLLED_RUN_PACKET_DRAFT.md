# Phase 18.15 Controlled Run Packet Draft

This is a future packet boundary only.

Recommended controlled proof:

- one cycle or maximum 10 minutes
- report-only
- local-only
- no APPLY
- no commit/push
- not 12h
- not overnight
- explicit stop point
- explicit kill/park command
- clean state check before and after

No broker/trading, secrets, Pi motor, runtime mutation beyond an approved report path, OpenAI call, telemetry/control write, or approval inbox write is allowed unless a future packet separately approves it.

