# Runtime Packet And Lock Model

Packets define work.

Locks define ownership.

The packet and lock systems must stay separate but connected.

## Packet Lifecycle

Recommended packet states:

- `QUEUED`
- `ASSIGNED`
- `DRY_RUN_STARTED`
- `DRY_RUN_COMPLETE`
- `APPROVAL_REQUIRED`
- `APPLY_APPROVED`
- `APPLY_COMPLETE`
- `VALIDATED`
- `COMMIT_READY`
- `COMMITTED`
- `BLOCKED`
- `FAILED`
- `REVIEW_REQUIRED`

Packet source of truth:

`Reports/dispatcher/runtime/packets/packet_runtime_table.json`

## Lock Lifecycle

Recommended lock states:

- `REQUESTED`
- `ACTIVE`
- `RELEASED`
- `EXPIRED`
- `BLOCKED`
- `REVIEW_REQUIRED`

Lock source of truth:

`Reports/dispatcher/runtime/locks/lock_runtime_table.json`

## Lock Rules

A folder lock blocks file locks inside that folder.

A file lock blocks another worker from claiming the same file or its parent folder.

An expired lock does not automatically become safe to overwrite.

Expired locks become `REVIEW_REQUIRED`.

## Duplicate Concept Control

Packet queue is intake.

Packet runtime table is current packet truth.

Lock table is ownership truth.

Dispatcher status is a summary.

