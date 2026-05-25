# AI_OS Path Conflict Policy 001

Path ownership prevents worker collisions.

## Lock Naming

Lock IDs must use:

```text
LOCK_<ZONE>_<LANE>_<WORKER>
```

Examples:

```text
LOCK_EAST_ORCH_OCC01
LOCK_WEST_DOCS_OCC01
LOCK_VALIDATOR_GOV_01
```

Locks with missing, placeholder, or ambiguous identity fields are not sufficient for APPLY readiness.

West lock examples must use the same identity standard:

```text
LOCK_WEST_DOCS_OCC01
LOCK_WEST_ARCH_OCC01
LOCK_WEST_DASHBOARD_UI_OCC01
```

West locks may be proposed only by packet. They become active only when an approved APPLY packet names exact paths, lock owner, validator chain, approval authority, and release condition.

## Rules

- No dual ownership of the same file or folder path.
- Runtime paths have the highest priority because they can affect packet, lock, approval, validator, and recovery state.
- Documentation paths are lower priority but still need one owner when edited.
- Validator paths must stay isolated so validation behavior is not changed by unrelated worker packets.
- Overwrites are blocked unless the operator explicitly approves exact files.
- If ownership is unclear, mark the work `REVIEW_REQUIRED`.
- East and West workers must not edit the same file tree at the same time without explicit reassignment.
- Cross-zone work requires matching packet identity, lock identity, allowed paths, validator chain, and approval authority.
- West cannot claim shared canonical governance, workflow, security, schema, dashboard mock-data, or East/runtime paths as owned territory.

## Escalation

Escalate to human review when:

- two workers claim overlapping paths
- a lock has no worker ID
- a claim has no packet ID
- a lock is expired but still affects active work
- a worker needs to edit a path owned by another worker

Next safe action: resolve conflicts before APPLY, staging, commit, or push.
