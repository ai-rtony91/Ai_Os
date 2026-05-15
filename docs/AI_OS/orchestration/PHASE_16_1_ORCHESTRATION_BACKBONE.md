# Phase 16.1 Orchestration Backbone

## Purpose

Phase 16.1 adds a small, local-first orchestration backbone for AI_OS.

The backbone is designed to prevent workers from colliding, claiming the same packet, or touching unsafe paths.

## What This Adds

- `packet_queue.example.json` shows how packets can be listed before assignment.
- `assignment_locks.example.json` shows how a packet claim can record worker ownership, approved paths, blocked paths, approval requirements, validator requirements, and collision status.
- `clean_state_gate.ps1` checks whether the repo is in a clean enough state to make a launch decision.
- `automation/orchestration/README.md` explains the folder in beginner-readable language.

## Safety Boundary

This phase does not add live trading, broker access, OANDA access, API keys, real orders, webhooks, startup tasks, scheduled tasks, commits, or pushes.

The allowed scope is limited to:

- `automation/orchestration/`
- `docs/AI_OS/orchestration/`
- `Reports/checkpoints/`

Blocked paths remain blocked, including dashboard runtime files, broker folders, OANDA folders, webhook folders, live trading folders, secrets, `.env` files, `.git/`, and `.codex_backups/`.

## Why It Matters

AI_OS needs a predictable operator workflow before multiple workers can safely run in parallel.

The packet queue answers: what work exists?

The assignment lock answers: who owns the work?

The clean-state gate answers: is the repo safe enough to continue?

## What Remains Next

Next work should connect these examples to a DRY_RUN validator chain that can inspect real packet and lock files without creating claims or launching workers.

Next safe action: run the clean-state gate, review the blocked or allowed result, and only continue with human-approved APPLY work.
