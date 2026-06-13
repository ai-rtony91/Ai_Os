# Forex Engine v1 Continuation Recommender Loop

## Purpose

This is a read-only supervision helper that helps AI_OS continue the Forex Engine lane without executing any build step.

`Get-AiOsForexNextBuildPacket.DRY_RUN.ps1` inspects repository evidence and emits a deterministic recommendation payload for the next safe Forex packet candidate.

## What It Does

- Detects whether Sprint 14 (paper readiness), Sprint 15 (paper signal intake ledger), Sprint 16 (paper risk decision router), and Sprint 17 (paper continuity review) are present.
- Reports repo state used for recommendation:
  - `repo_root`
  - `branch`
  - `dirty_or_untracked_count`
- Reports sprint completion signals:
  - `forex_readiness_gate_present`
  - `forex_signal_intake_ledger_present`
  - `latest_forex_sprint_detected`
- Emits the next recommended build packet when the preconditions are met.

## Why This Exists

AI_OS can currently scan state and run validators, but campaign stage selection returned `NO_READY_STAGE` when no campaign stage was marked `READY`.
This recommender adds a narrow, deterministic handoff that maps current Forex build evidence to the next safe packet candidate, with explicit human control.

## How It Differs From Unattended Autonomy

- DRY_RUN only (no writes, no protected actions).
- No worker launch, no packet mutation, no runtime mutation, no commit/push.
- Always ends with a human approval requirement for the next protected `APPLY` packet.

## Recommended Packet After Sprint 18

When Sprint 14, 15, 16, 17, and 18 are present:

- Packet ID: `AIOS-FOREX-PAPER-LEARNING-ACTION-ROUTER-APPLY-V1`
- Packet title: `feat(forex): add paper learning action router`
- Lane: `PAPER_LEARNING_ACTION_ROUTER`

Recommended files:

- `automation/forex_engine/paper_learning_action_router.py`
- `automation/forex_engine/run_paper_learning_action_router_demo.py`
- `tests/forex_engine/test_paper_learning_action_router.py`
- `docs/AI_OS/trading/FOREX_ENGINE_V1_PAPER_LEARNING_ACTION_ROUTER.md`

## Blocked Actions

This recommender stays in safe read-only mode and blocks:

- live trading
- broker APIs
- OANDA
- real orders
- webhooks
- real market data
- API keys/secrets
- scheduler/daemon actions
- worker launch
- runtime mutation
- telemetry mutation
- dashboard mutation
- Cloudflare
- backup sync
- push/PR/merge automation
