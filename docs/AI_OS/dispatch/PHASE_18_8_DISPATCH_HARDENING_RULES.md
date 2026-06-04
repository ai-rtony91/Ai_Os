# Phase 18.8 Dispatch Hardening Rules

Phase 18.8 upgrades the Phase 18.6 dispatch preview into a stricter decision layer for future OpenAI-generated packets, Night Supervisor preview packets, Skills, red-team cases, and autonomy routes.

AI_OS priority remains `TRUSTED_PROVEN_PROFITABILITY`.

## Route Classes

- `BLOCKED`
- `READ_ONLY_RECON`
- `DOCS_ONLY`
- `FIXTURE_ONLY`
- `DRY_RUN_IMPLEMENTATION`
- `APPLY_HUMAN_APPROVED`
- `PR_VALIDATION`
- `MERGE_HUMAN_APPROVED`
- `NIGHT_SUPERVISOR_PREVIEW`
- `NIGHT_SUPERVISOR_RUNTIME_PENDING_APPROVAL`
- `OPENAI_SMOKE_TEST_PENDING_APPROVAL`
- `RESPONSES_PACKET_DRAFT_PENDING_APPROVAL`
- `PROMPTFOO_RED_TEAM_PENDING_APPROVAL`
- `COMPUTER_USE_PENDING_APPROVAL`
- `PI_CAR_VOICE_PREVIEW`
- `PI_CAR_MOTOR_BLOCKED`
- `LIVE_TRADING_BLOCKED`

## Required Decision Fields

Every dispatch hardening decision must include route confidence, risk score, readiness score, safety score, blocker classes, validators required, human approval requirement, allowed execution mode, fail-closed status, and stop point.

## Hard Blocks

Dispatch cannot start runtime, mutate the repo, touch Night Supervisor runtime, call OpenAI, install Promptfoo, run Promptfoo, execute computer-use actions, execute unreviewed Skills, touch broker/OANDA/live trading, touch Pi GPIO/motor, print secrets, or write telemetry/control/approval inbox state unless a later human-approved packet explicitly authorizes that action.

When uncertain, dispatch must fail closed.

