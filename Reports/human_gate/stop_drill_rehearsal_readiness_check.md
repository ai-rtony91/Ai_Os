# AI_OS STOP Drill Rehearsal Readiness Check

## Status

- status: `REVIEW_ONLY`
- check_type: `STOP_DRILL_REHEARSAL_READINESS`
- stop_drill_pass: `False`
- stop_drill_claimed_passed: `False`
- confirmation_phrase_used: `False`

## Purpose

This file prepares Anthony to decide whether a manual STOP drill can be performed safely.

This file does **not** perform the STOP drill.

This file does **not** claim the STOP drill passed.

This file does **not** authorize runtime execution, runtime launch, queue write, worker inbox mutation, command queue mutation, scheduler registration, SOS send, broker action, live trading, secret storage, or vacation mode completion.

## Preconditions

Before Anthony performs a real manual STOP drill:

1. `main` should be clean and synced to `origin/main`.
2. No broker or live trading connection should be active.
3. No secrets should be written to the repo.
4. No scheduler action is authorized.
5. No SOS action is authorized.
6. Codex must not execute STOP, kill processes, launch runtime, mutate queues, send SOS, or register scheduler tasks.

## What Anthony Should Observe During a Manual STOP Drill

If Anthony decides to run the manual STOP drill, he should observe and record:

1. What condition was intentionally stopped.
2. Whether the system stayed blocked instead of continuing.
3. Whether recovery behavior was visible and understandable.
4. Whether evidence remained available after the stop.
5. Whether no active queue, worker inbox, command queue, scheduler, SOS, broker, secret, or live-trading path changed.

## Pass Criteria

STOP drill evidence can only be considered passed for dry-run recovery proof if:

1. Anthony personally performed or reviewed the manual STOP drill.
2. The observed stop condition is documented.
3. The recovery behavior is documented.
4. No runtime execution by Codex occurred.
5. No queue mutation occurred.
6. No worker inbox mutation occurred.
7. No command queue mutation occurred.
8. No scheduler registration occurred.
9. No SOS send occurred.
10. No live trading occurred.
11. No secret was written.
12. Anthony decides the STOP drill evidence is sufficient for dry-run recovery proof only.

## Fail or Stop Criteria

Stop immediately and do not use the confirmation phrase if:

1. Any automation attempts to execute STOP for Anthony.
2. Codex kills a process.
3. Runtime launches or executes.
4. Active queue, worker inbox, or command queue changes.
5. Scheduler registration occurs.
6. SOS is sent.
7. Broker, OANDA, webhook, live-trading, `.env`, or secret paths are touched.
8. `vacation_mode_complete` becomes true.
9. Any report claims `stop_drill_pass = true` before Anthony confirms it.

## Required Exact Phrase

`ANTHONY_CONFIRMS_STOP_DRILL_PASSED_FOR_DRY_RUN_RECOVERY_PROOF_ONLY`

Use this phrase only after Anthony actually performs or reviews the manual STOP drill and records evidence.

This phrase only confirms STOP drill evidence for dry-run recovery proof.

It does not authorize runtime execution, scheduler registration, SOS send, queue write, broker action, live trading, secret storage, or vacation mode completion.

## Safe Next Action

Anthony reviews this readiness check.

If Anthony is not ready, AI_OS remains blocked.

If Anthony performs the manual STOP drill and records evidence, then prepare a separate confirmation packet using the exact phrase.

## Stop Condition

Stop before claiming STOP drill pass, executing STOP through Codex, killing processes, launching runtime, executing runtime, mutating queues, sending SOS, registering scheduler, touching credentials, writing secrets, enabling live trading, or setting `vacation_mode_complete = true`.
