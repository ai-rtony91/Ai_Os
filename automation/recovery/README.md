# AI_OS Recovery

Recovery files define how AI_OS should inspect state after interruption, crash, reboot, or stale worker ownership.

Recovery is read-first and human-approved. It must not automatically resume APPLY, release locks, reassign packets, stage files, commit, push, create startup tasks, create scheduled tasks, or trigger live trading.
