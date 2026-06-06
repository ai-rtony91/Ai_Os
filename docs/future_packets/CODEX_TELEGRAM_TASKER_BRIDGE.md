# Telegram Tasker Control Surface Roadmap

Status: future packet design, docs-only

This document preserves the Telegram and Tasker vision for AI_OS, but it is not
an execution packet. It must not be used to enable Telegram live send, Telegram
polling, approval mutation, scheduler registration, worker launch, broker/OANDA
access, live trading, real orders, real webhooks, GPIO, motor control, secrets,
or production promotion.

Telegram and Tasker are interface surfaces only. AI_OS remains the router and
gatekeeper. Anthony remains approval authority. Codex and other workers execute
only exact approved packets and must stop at protected gates.

## Core Security Model

- Telegram and Tasker are not authority.
- AI_OS remains the gatekeeper for every command.
- Anthony remains approval authority.
- An identity gate is required before any inbound Telegram command is accepted.
- Command allowlist only.
- Unknown commands return help text only.
- Every command maps to one classification:
  - `READ_ONLY`
  - `PREPARE_ONLY`
  - `NEEDS_EXPLICIT_APPROVAL`
  - `BLOCKED_FOR_SAFETY`
- No bot token, chat ID, credential, `.env` value, or secret may be printed,
  logged, committed, pasted, or summarized.
- Replay protection is required for Telegram update offsets before inbound
  control is enabled.
- Approval decisions must be idempotent.
- Audit logs may record command metadata only. They must not record secrets.
- `#AIOS_SOS` is reserved only for wake-worthy SOS events.

## Phase 1 - SOS Wake Only

Purpose: wake Anthony only for true SOS conditions.

Allowed:

- Telegram sends `#AIOS_SOS` only for true SOS.
- Tasker watches Telegram notifications for `#AIOS_SOS`.
- Tasker wakes Anthony by alarm, vibration, TTS, or opening Telegram.
- Non-SOS messages do not wake Anthony.

Blocked:

- No inbound Telegram control.
- No approval mutation.
- No Telegram polling live run.
- No Tasker repo control.
- No scheduler, worker, trading, GPIO, or production action.

## Phase 2 - Read-Only Status

Purpose: let Anthony request sanitized status summaries.

Allowed commands:

- `/status`
- `/brief`
- `/pi5`
- `/openai`
- `/protected`
- `/forex`
- `/t9`
- `/queue`

Classification: `READ_ONLY`

Rules:

- Return sanitized summaries only.
- Do not expose secrets, token values, chat IDs, private raw evidence, or
  credential state beyond presence/missing by approved variable name.
- Do not mutate files, approvals, telemetry, workers, scheduler, trading, or
  production state.

## Phase 3 - Exact Approval-Card Decisions

Purpose: allow Anthony to decide exact existing approval cards without freeform
approval.

Allowed commands:

- `approve <approval_id>`
- `reject <approval_id>`
- `defer <approval_id>`

Classification: `NEEDS_EXPLICIT_APPROVAL`

Rules:

- `<approval_id>` must match an exact current approval artifact.
- Approval scope must match the current active approval card.
- No freeform approval is allowed.
- Duplicate approval replay must be idempotent.
- Unknown, stale, historical, sample, or completed approval IDs must not mutate
  approval state.
- Approval mutation requires a separately approved APPLY implementation and
  validator coverage before live use.

## Phase 4 - Packet Preparation Requests

Purpose: let Anthony request packet drafting without execution.

Allowed commands:

- `prepare packet <goal_id>`
- `prepare forex-paper packet`
- `prepare t9-check packet`
- `prepare pi5-health packet`

Classification: `PREPARE_ONLY`

Rules:

- Prepare candidate packets only.
- Do not execute packets.
- Do not create or edit files unless a separate APPLY packet authorizes the
  exact write boundary.
- Candidate packets must preserve allowed paths, forbidden paths, validator
  chain, approval authority, and stop point.

## Phase 5 - Protected Action Requests

Purpose: convert protected-action requests into readiness cards, not execution.

Allowed commands:

- `request commit <packet_id>`
- `request push <branch>`
- `request merge <pr>`
- `request worker-launch <packet_id>`
- `request scheduler <lane>`

Classification: `NEEDS_EXPLICIT_APPROVAL`

Rules:

- Never execute directly from Telegram.
- Generate or surface Protected Action Readiness classification only.
- Commit, push, merge, worker launch, scheduler registration, approval mutation,
  and production-adjacent actions require separate explicit Anthony approval.
- Validator PASS is evidence only. It is not approval.

## Phase 6 - Forex And Trading

Purpose: expose paper-only Forex status and reports without enabling execution.

Allowed commands:

- `/forex status`
- `/forex paper-report`
- `/forex paper-ledger`
- `/forex risk-summary`
- `request forex-paper build packet`

Classification:

- Status and reports: `READ_ONLY`
- Build packet request: `PREPARE_ONLY`

Blocked:

- broker/OANDA
- live market API
- API keys
- real orders
- real webhooks
- Telegram-triggered execution
- live market execution

Rules:

- Telegram must never trigger live orders.
- Telegram must never access broker, OANDA, API-key, or credential material.
- Future live-trading architecture, if ever approved, must be separate from this
  interface roadmap and must preserve protected gates.

## Phase 7 - Emergency Hold

Purpose: provide a controlled way to request a hold without inventing a process
killer.

Allowed commands:

- `/hold`
- `/stop-aios`
- `/pause-workers`

Classification: `NEEDS_EXPLICIT_APPROVAL`

Rules:

- Initially create a hold recommendation or protected-action card only.
- Show what would stop, why, current risk, and how to resume.
- Do not kill processes unless a separately approved stop controller exists.
- Do not stop scheduler, workers, trading, GPIO, or production paths directly
  from Telegram or Tasker.

## Tasker Role

Tasker is a phone-side wake and attention tool.

Allowed:

- Watch Telegram notifications for `#AIOS_SOS`.
- Wake Anthony through alarm, vibration, TTS, or opening Telegram.
- Future Tasker buttons may send allowlisted Telegram commands into the AI_OS
  gate.

Blocked:

- No direct repo control.
- No direct approval mutation.
- No direct worker launch or scheduler control.
- No direct trading, broker, GPIO, motor, or production control.

## Telegram Role

Telegram is a command and notification interface.

Allowed:

- Carry sanitized outbound status and SOS messages.
- Accept allowlisted inbound command text after identity-gate validation.

Blocked:

- No freeform execution.
- No authority transfer.
- No direct protected action.
- No secret output.
- No live send or polling until a separate approval packet authorizes the exact
  behavior and validation chain.

## Future Implementation Gates

Before any APPLY work expands beyond Phase 1, a complete packet must define:

- exact allowed paths and forbidden paths.
- identity gate implementation.
- command allowlist.
- command classification table.
- replay protection.
- idempotent approval handling.
- audit log metadata schema.
- secret-output prevention.
- Protected Action Readiness integration.
- validator chain.
- rollback or stop condition.

Any packet that attempts Telegram live send, Telegram polling, approval mutation,
scheduler activation, worker launch, OpenAI API calls, external API calls,
broker/OANDA access, live trading, real orders, real webhooks, GPIO, motor
control, production promotion, commit, push, or merge must stop for explicit
Anthony approval.
