# AI_OS Recovery Bootstrap Plan

Recovery bootstrap should run after crash, reboot, interrupted work, stale locks, or stale workers.

## Checks

- current branch
- current git status
- active packets
- active locks
- incomplete worker runs
- missing reports
- stale worker ownership
- dirty files not tied to a packet
- abandoned files
- validator results
- last safe checkpoint

## Safe Behavior

- read current state
- report stale or unknown state
- mark unclear work `REVIEW_REQUIRED`
- avoid committing abandoned files
- avoid overwriting user or friend work
- require human approval before APPLY, lock override, reassignment, staging, commit, or push
