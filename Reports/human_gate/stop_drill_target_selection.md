# AI_OS STOP Drill Target Selection

## Status

- status: `REVIEW_ONLY`
- selection_status: `TARGET_NOT_SELECTED`
- stop_drill_pass: `False`
- confirmation_phrase_used: `False`
- safe_to_use_confirmation_phrase: `False`

## Purpose

Before Anthony can confirm the STOP drill passed, AI_OS needs a specific manual STOP drill target.

Right now, the confirmation phrase must stay blocked because no explicit target has been selected and observed.

## Valid STOP Drill Targets

A valid target may be:

1. A manually started disposable dry-run preview process.
2. A non-production test command intentionally started by Anthony.
3. A documented simulated condition that can be stopped without touching runtime, queue, scheduler, SOS, broker, secrets, or live trading.

## Invalid STOP Drill Targets

Do not use any of these as STOP drill targets:

1. Production runtime.
2. Active queue.
3. Worker inbox.
4. Command queue.
5. Windows scheduler.
6. SOS channel.
7. Broker or OANDA path.
8. Webhook path.
9. Live trading process.
10. Credential or secret path.
11. Anything Codex kills automatically.

## Required Before Using the Confirmation Phrase

Anthony must first:

1. Select the exact manual STOP drill target.
2. Confirm the target is disposable or non-production.
3. Confirm no live trading, broker, SOS, scheduler, queue, inbox, command queue, secret, or credential path will be touched.
4. Perform or review the manual STOP drill.
5. Record the observed stop condition.
6. Record the recovery behavior.
7. Verify all dangerous flags remain false.

## Confirmation Phrase Still Blocked

Do not use:

`ANTHONY_CONFIRMS_STOP_DRILL_PASSED_FOR_DRY_RUN_RECOVERY_PROOF_ONLY`

until the target is selected, stopped manually, observed, and recorded.

## Safe Next Action

Anthony selects a specific manual STOP drill target, or declines the STOP drill and remains blocked.

## Stop Condition

Stop before claiming STOP drill pass, killing processes, launching runtime, executing runtime, mutating queues, sending SOS, registering scheduler, touching credentials, writing secrets, enabling live trading, or setting `vacation_mode_complete = true`.
