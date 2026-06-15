# AIOS Resume State

`aios_resume_state.py` converts an `AIOS_WAKE_CONTINUE.v1` report into a
sanitized `AIOS_RESUME_STATE.v1` record. It exists so AIOS can restart later and
know the last goal, decision, next build plan, bounded executor handoff,
validator summary, approval requirements, safety locks, and next safe action.

The resume state strips validator `stdout` and `stderr` bulk output and stores
only pass/fail/count summaries. Sensitive payload keys are redacted before
persistence.

Persistence is explicit only. Nothing is written unless a caller requests it.
The writer is bounded to `Reports/aios_resume/`, creates the directory when
needed, writes one timestamped file, and updates `AIOS_RESUME_STATE_latest.json`.
It does not delete files and does not overwrite timestamped files.

This bridge does not activate schedulers, daemons, workers, queues, approvals,
dashboard flows, broker calls, credentials, live trading, real orders, webhooks,
staging, commits, pushes, or merges.
