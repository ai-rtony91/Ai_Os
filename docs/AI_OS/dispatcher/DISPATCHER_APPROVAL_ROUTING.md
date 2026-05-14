# Dispatcher Approval Routing

The dispatcher must route risky or approval-required work packets into the Approval Inbox before execution.

## Flow

1. Work packet enters dispatcher.
2. Dispatcher checks risk and `requiresApproval`.
3. If approval is required, dispatcher creates an Approval Inbox request.
4. Packet status becomes `waiting_approval`.
5. Execution waits until an approval decision exists.
6. Approved packets may proceed to dry run/apply.
7. Rejected packets become blocked.

## Safety Rules

- High-risk packets always require approval.
- Trading actions must remain approval-gated.
- File deletes, commits, pushes, and system commands must remain approval-gated.
- Dispatcher must not directly execute risky actions.
- Approval records must include target files and rollback references.
