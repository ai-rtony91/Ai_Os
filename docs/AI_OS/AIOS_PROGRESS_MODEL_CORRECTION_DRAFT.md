# AI_OS Progress Model Correction Draft

## Purpose

This draft defines separate progress fields for AI_OS and future trading work. It does not implement telemetry migration, edit reports, edit dashboard code, run scripts, or connect trading systems.

## Core Framing

AI_OS is the tooling, infrastructure, documentation, verification, approval, telemetry, dashboard, and agent-operation layer used to build the future trading system.

AI_OS is not the trading bot itself.

Trading bot and trading engine development begins only after AI_OS operating controls are mature enough.

## Corrected Progress Fields

| Field | Meaning |
|---|---|
| `foundation_progress_percent` | Progress of AI_OS foundation docs, policies, folder roles, architecture, safety rules, and planning artifacts. |
| `operational_aios_progress_percent` | Progress of AI_OS as an operating system with agents, helper scripts, telemetry automation, dashboard visibility, approval gates, and tested dry-run execution. |
| `trading_engine_progress_percent` | Progress of the future trading engine or trading bot. This remains separate from AI_OS foundation/tooling progress. |

## What Counts Toward Operational AI_OS Progress

- Documented agent roles.
- Agent handoff rules.
- Approval gates.
- Draft work orders.
- Dashboard visibility.
- Helper scripts.
- Telemetry automation.
- Tested dry-run execution.

## What Does Not Count Toward Trading Engine Progress

- AI_OS documentation alone.
- Folder-purpose notes.
- Dashboard planning.
- Agent architecture planning.
- Screen-recording readiness.
- Telemetry planning.

These items support the future trading system but are not trading-engine implementation.

## Current Status

- `foundation_progress_percent`: planning estimate exists, formula not fully approved.
- `operational_aios_progress_percent`: formula is not approved yet.
- `trading_engine_progress_percent`: NOT_STARTED unless a separate trading-engine plan says otherwise.

## Known Unresolved Items

- Agent runtime implementation design remains UNKNOWN.
- LLM API/provider selection remains UNKNOWN.
- Dashboard-to-agent integration path remains UNKNOWN.
- `operational_aios_progress_percent` formula is not approved yet.
- Trading Mode safety boundaries require later review.
- Credential/key handling policy is not implemented.
- Current directory display mismatch was observed in Codex and was verified by PowerShell before APPLY.
