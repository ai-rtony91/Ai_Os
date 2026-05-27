# AI_OS Self-Build Preview Workflow

## Purpose

The AI_OS self-build preview workflow describes a safe preview-only path from a plain morning brief to a proposed governed packet and downstream orchestration previews.

This is not full autonomy. It is not a daemon. It is not API-driven yet. It does not execute Codex automatically.

## Flow

```text
morning brief
-> packet preview
-> loop preview
-> controller preview
-> human approval
```

The preview chain may summarize evidence, infer a packet draft, call existing DRY_RUN preview helpers, and show the next safe action. It must not execute the proposed packet.

## Autonomy Boundary

This workflow is limited to `docs/governance/AI_OS_AUTONOMY_LEVELS.md`:

- Level 1 - AUTO READ-ONLY
- Level 2 - AUTO REPORT / PREVIEW FILES

Level 3, Level 4, and Level 5 remain gated. Exact command preparation, approved execution, hard-gate actions, merge, secrets, credentials, API keys, broker integration, OANDA, live trading, real webhooks, real orders, destructive repo actions, branch protection changes, and governance authority changes do not become automatic through this workflow.

## Non-Goals

This workflow does not:

- create `automation/loop_engine.py`
- use API keys
- use `.env`
- call external model APIs
- call OpenAI APIs
- call Anthropic APIs
- run Codex as a subprocess
- launch workers
- mutate queues
- mutate approvals
- stage files
- commit
- push
- create PRs
- merge
- touch broker, OANDA, live trading, webhook, secrets, or dashboard scope

## Morning Brief Packet Preview

`automation/orchestration/control/Get-AiOsMorningBriefPacketPreview.DRY_RUN.ps1` reads an optional plain text morning brief as evidence only.

If no brief is supplied, the helper marks the brief state as `MISSING` and continues. If a brief is supplied, the helper uses local rule-based parsing only:

- inspect, review, reassess, or check -> `DRY_RUN`
- create, build, or add -> `APPLY_PREVIEW_REQUIRED`
- commit, push, or PR -> controller preview only
- API keys, `.env`, secrets, broker, OANDA, live trading, or webhook -> `HARD_GATE_REQUIRED`
- unclear text -> safer `DRY_RUN`

The helper never recommends live trading or broker action.

## Self-Build Preview

`automation/orchestration/control/Get-AiOsSelfBuildPreview.DRY_RUN.ps1` combines:

- morning brief packet preview
- loop-engine preview
- commit/push/PR controller preview

It emits `AIOS_SELF_BUILD_PREVIEW.v1` and stops. It does not write queue state, approval records, packet state, runtime state, reports, commits, pushes, PRs, or merge state.

## Human Approval

Human approval remains required before:

- APPLY
- staging
- commit
- push
- PR creation
- merge
- protected paths
- secrets or credentials
- API integration
- trading, broker, OANDA, live trading, real webhooks, or real orders
- worker launch
- runtime persistence
- scheduled/background automation
- governance authority changes

Approval markers remain separate:

- `APPROVE_COMMIT`
- `APPROVE_PUSH`
- `APPROVE_PR_CREATE`

Merge requires separate explicit approval and is not included in this preview workflow.

## API Integration

API integration comes later only after the preview layer is stable, reviewed, and separately approved. Future API integration must not use hidden credentials, `.env`, unchecked model calls, background loops, Codex subprocess execution, or protected actions without a dedicated approved packet.

## Trading Boundary

Trading remains blocked. This workflow must not route broker, OANDA, live trading, webhook, secret, credential, real order, or live execution work into automation.
