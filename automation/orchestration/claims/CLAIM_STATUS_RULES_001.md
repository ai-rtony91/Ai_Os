# AI_OS Claim Status Rules 001

Worker claims reserve a packet and path set for one worker at a time.

## Status Values

- `claimed`: a worker has reserved the packet and assigned paths.
- `active`: the worker is currently working inside the claim boundary.
- `blocked`: the worker cannot proceed without operator review.
- `expired`: the claim is past its review window and must be checked before reuse.
- `completed`: the worker finished the packet and validation is ready for review.
- `abandoned`: the claim appears stale or disconnected from a live worker.
- `rejected`: the operator rejected the claim or the claim conflicts with safety rules.

## One Worker Per Path

Only one worker can own a path at a time because parallel edits to the same file group can create hidden conflicts, overwritten work, invalid validation, and unsafe commit packages.

If two workers need the same path, the second worker must stop and request human review.

Next safe action: check the claim registry before assigning new worker packets.
