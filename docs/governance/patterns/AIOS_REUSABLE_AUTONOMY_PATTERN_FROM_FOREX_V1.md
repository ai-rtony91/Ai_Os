# AIOS Reusable Autonomy Pattern From Forex V1

This document extracts the reusable autonomy skeleton proven in the Forex lane. It is a pattern document, not new governance authority.

## Identity Chain

Use the full chain for governed work:

Mission -> Program -> Epic -> Bucket -> Packet

The chain makes scope traceable and prevents a worker from turning one task into a broad controller.

## Preflight

Run preflight before edits:

- Confirm `pwd`.
- Confirm branch.
- Confirm clean worktree.
- Confirm no staged files.
- Confirm current head.
- List stash metadata without applying, popping, or dropping stash.

## Scope

Every APPLY packet needs exact allowed paths and exact forbidden paths. Allowed paths define where writes may occur. Forbidden paths preserve governance, secrets, runtime, broker, dashboard, and unrelated systems.

## Validators

Use validators scaled to the work:

- `python -m py_compile` for Python modules and runners.
- Focused `pytest` for new behavior.
- CLI generation commands for state/report/packet artifacts.
- `python -m json.tool` for generated JSON.
- Governance validator for generated Codex packets.
- `git diff --check` for whitespace and patch hygiene.
- `git status --short --branch` for final state.

## Output Pattern

Each reusable autonomy unit should produce:

- State JSON for deterministic machine-readable state.
- Human report for operator review.
- Next packet for the next bounded step.

The next packet must stay DRY_RUN unless a later owner-approved APPLY packet is provided.

## Protected Boundary Stop

Stop before protected boundaries:

- Broker/API contact.
- Credentials or `.env`.
- Account identifiers or account inspection.
- Orders.
- Demo/live execution.
- Scheduler, daemon, webhook, worker, watcher, listener, or background loop.

## Commit, PR, Merge Flow

Commit only when the packet explicitly authorizes commit, validators pass, exact staged paths match the allowed list, and cached diff has been reviewed. Push, PR creation, merge, and live/protected actions require separate approval.

## Failure Recovery

Fail closed on dirty preflight, staged files, branch mismatch, validator failure, unexpected paths, protected-action drift, or command errors. Report the exact blocker and the next safe action.

## Reuse

Future lanes can reuse this pattern by replacing Forex-specific source artifacts with their own state inputs while preserving the same boundary: identity chain, preflight, allowed paths, forbidden paths, validators, state JSON, report, next packet, protected stop, and one-commit discipline.
