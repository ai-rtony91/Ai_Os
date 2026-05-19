# Packet Queue Automation Model

## Purpose

Packet queue automation reduces manual prompt copy/paste by turning each worker task into a structured packet.

The packet gives the worker the objective, mode, allowed paths, blocked paths, validation steps, report requirements, and next safe action. The operator can assign a packet ID instead of repeatedly pasting a long prompt into each worker window.

## Scope

This model is docs and examples only.

It does not create executable assignment logic.

## Source Of Truth Separation

Packet queue files should not become one oversized control file.

- Packet queue: work waiting to be assigned.
- Packet assignment report: which worker should take which packet.
- Packet runtime table: current packet truth after assignment.
- Active worker table: worker truth and heartbeat.
- Approval ledger: human APPLY decisions.
- Queue health summary: operator-readable state.

## Basic Flow

1. A packet is created in `QUEUED` state.
2. Queue monitor checks allowed paths, blocked paths, worker availability, and repo safety.
3. A safe packet is recommended for one worker.
4. The worker accepts one packet.
5. The worker starts DRY_RUN.
6. The worker reports DRY_RUN completion.
7. APPLY remains blocked until explicit human approval.
8. Blocked or uncertain state becomes `REVIEW_REQUIRED`.

## Operator Benefit

The operator should only need to provide a packet ID and a short instruction such as:

`Worker 08: run packet PACKET-QUEUE-001 in DRY_RUN mode.`

The packet carries the full task details.

## Safety Rules

- No automatic APPLY.
- No automatic approval.
- No automatic staging.
- No automatic commit.
- No automatic push.
- No automatic cleanup.
- No changes outside `allowed_paths`.
- No broker, OANDA, API key, webhook, or live trading execution.

## Queue Health Connection

Queue monitoring should read packet queue state and report:

- queued packet count
- assigned packet count
- blocked packet count
- review-required packet count
- oldest packet age
- next recommended packet
- one beginner-readable next safe action

## Next Safe Action

Review `packet_queue.example.json`, then approve or reject a future implementation plan for a read-only packet queue validator.
