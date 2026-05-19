# AI_OS Orchestration Framework Draft

## Purpose

AI_OS orchestration will chain verified helpers into repeatable workflows. The framework is designed to make repo health checks, session evidence drafts, checkpoint drafts, daily metrics drafts, and mode selection predictable while keeping humans in control.

This is not autonomous execution.

## Current Stage

Stage 9F adds DRY_RUN-only mode selection scaffolding.

Stage 10A adds a DRY_RUN-only operational chain that can call existing helper scripts when they are present and warn when they are missing.

## Components

Current orchestration components are:

- Mode selection helper.
- Operational chain helper.
- Shared helper rules.
- Repo health helper.
- Session evidence helper.
- Checkpoint draft helper.
- Daily metrics row helper.

## Mode Selection

Mode selection labels the requested work posture before any action is considered. Initial mode names are:

- `WORK_MODE`
- `TRADING_MODE`
- `RETIRE_MODE`
- `RETURN_TO_WORK_MODE`
- `MORNING_BRIEF_MODE`

Mode selection does not launch apps, change startup settings, edit files, or approve APPLY work.

## Operational Chain

The operational chain runs approved DRY_RUN helpers in order when they exist:

1. Repo health chain.
2. Session evidence log draft.
3. Checkpoint draft.
4. Daily metrics row draft.

Missing helpers produce WARN output instead of stopping the entire chain.

## Shared Rules

All helpers must default to DRY_RUN, use exact path scoping, avoid destructive actions, protect root files, block trading/broker actions, block startup/launcher actions unless separately approved, report first, and wait for a human approval gate before APPLY work.

## Human Approval Gates

Humans approve APPLY. The approval must name the exact mode, files, paths, and action. Git staging, commits, and pushes require a separate explicit human instruction.

## Non-Scope

This framework does not approve:

- Autonomous execution.
- App launch.
- Browser launch.
- Startup setting changes.
- Task Scheduler changes.
- Registry, firewall, VPN, BIOS/UEFI, BitLocker, or browser policy changes.
- Credential, secret, token, private key, or recovery key handling.
- Broker orders.
- Trading execution.
- Live trading.

Trading, broker, and live execution remain blocked.

## Future Stage 10B

Stage 10B may add a text-only runbook or wrapper that explains how to run the chain, collect its output, and decide the next safe action. It should remain DRY_RUN-first and should not add autonomous behavior.
