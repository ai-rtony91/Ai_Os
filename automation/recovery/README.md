# AI_OS Recovery

Recovery files define how AI_OS should inspect state after interruption, crash, reboot, or stale worker ownership.

Recovery is read-first and human-approved. It must not automatically resume APPLY, release locks, reassign packets, stage files, commit, push, create startup tasks, create scheduled tasks, or trigger live trading.

## Night-cycle crash recovery boundary

`automation/orchestration/Invoke-AiOsNightCycle.ps1` may resume an interrupted
cycle from `control/cycle/last_marker.json` only when the marker is safe to use.
Auto-resume fails closed when:

- the marker is corrupt or unreadable.
- the marker contains `WAITING_FOR_APPROVAL`, `WAITING_APPROVAL`,
  `awaiting_approval`, or `pending_approval`.
- the marker timestamp is missing, unparseable, or older than the configured
  `-RestartMarkerMaxAgeSeconds` threshold, default `172800` seconds.
- the next resume phase is approval-sensitive.

Safe crash recovery preserves the existing `cycle_id` from the marker and lets
the night cycle re-run its normal mode and approval gates. It does not grant
APPLY approval.

Any restart supervisor must be manually launched, default to DRY_RUN, require a
future explicit arming flag for actual restart, and honor
`control/self_continuation/STOP`. No scheduler, service, startup task, live send,
broker path, OANDA path, webhook, credential behavior, commit, push, or merge is
authorized here.
