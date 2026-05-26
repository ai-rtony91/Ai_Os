# AI_OS Crew DRY_RUN Flow

## Flow

1. Task Intake receives a human goal.
2. Crew Dispatcher checks purpose, owner, priority, allowed paths, blocked paths, and stop point.
3. Packet Builder previews a work packet.
4. Worker Assignment recommends exactly one worker for one packet.
5. File Lock Manager checks path collision risk.
6. DRY_RUN Worker reports files to create, modify, or delete.
7. Approval Inbox Manager prepares an APPLY approval candidate.
8. Validator Runner recommends validators based on paths.
9. Commit Package Builder previews exact files for selective staging.

## Queue Status Flow

```text
PROPOSED -> QUEUED -> ASSIGNED -> DRY_RUN_COMPLETE -> APPROVED_FOR_APPLY -> APPLY_COMPLETE -> VALIDATED -> READY_FOR_COMMIT -> DONE
```

## Stop Conditions

Stop when:

- allowed paths are missing.
- blocked paths are unclear.
- two workers may touch the same path.
- lock status is unknown.
- approval is missing or stale.
- validator selection is missing.
- trading, broker, OANDA, API-key, webhook, real order, or live routing paths appear.
- a command would stage, commit, push, delete, reset, clean, or mutate outside approval.
