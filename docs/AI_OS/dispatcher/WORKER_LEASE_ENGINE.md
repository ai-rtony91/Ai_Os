# Worker Lease Engine

AI_OS tracks worker ownership using leases and heartbeat expiration.

## Purpose

The Worker Lease Engine prevents abandoned workers from permanently holding packet assignments.

## Worker States

- `idle`
- `assigned`
- `running`
- `stale`
- `expired`

## Lease Rules

- Workers receive temporary leases
- Leases expire without heartbeat renewal
- Expired workers lose packet ownership
- Reclaimable packets may return to dispatcher scheduling

## Recovery Goals

The engine allows AI_OS to:

- detect stale workers
- detect expired workers
- reclaim abandoned packets
- support reassignment
- support runtime recovery

## Reclaimable Packets

Packets become reclaimable when:

- worker status becomes `expired`
- lease expiration time passes
- worker disappears during recovery

## Safety Rules

- Packet reclaim does not auto-apply work
- Approval state remains preserved
- Reassignment requires dispatcher validation
- Expired workers cannot resume ownership automatically

## Future Extensions

- lease renewal scheduler
- distributed worker pools
- retry budgets
- dead-letter queues
- automatic reassignment policies
