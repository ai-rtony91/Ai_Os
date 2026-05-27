# AI_OS Current State For Claude

## Current Identity

- System: AI_OS
- Repo: `ai-rtony91/Ai_Os`
- Branch: `main`
- Local path: `C:\Dev\Ai.Os`
- V2: historical/migration context only

## Current Live Capabilities

- Governance spine
- `RISK_POLICY.md` safety boundary
- Codex/Claude approval tiers
- Crew Core foundation
- Crew integration recommendation helper
- Crew startup/status recommendation display
- Strategic Campaign Registry
- Campaign next-task helper

## Current Next-Task Logic

Campaign Registry selects the next task.

Crew Core reads or will bridge campaign recommendation into operator flow.

Chat should not guess the next task when Campaign Registry exists. It should ask for or inspect the current Campaign Registry helper output.

## Current Trading Boundary

Trading Lab is paper-only.

Forex, OANDA, broker paths, live orders, API keys, secrets, and credentials remain blocked unless the Human Owner changes policy through governance.

## External Assistant Correction

If Claude Chat says "AI_OS V2 is current," "workers are missing," or "Signal Validator is first," it is likely stale.

It must re-check current repo context first:

- `AGENTS.md`
- `README.md`
- `RISK_POLICY.md`
- `automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json`
- `automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1`

## Required Response Style For Claude

- concise
- evidence-based
- packet-aware
- no broad rewrites
- no autonomous APPLY
- no unchecked cleanup

Claude should phrase current state as:

```text
AI_OS is the current system on repo ai-rtony91/Ai_Os, branch main. V2 is historical/migration context only. Campaign Registry is the current next-task source. Trading Lab remains paper-only, and Forex/OANDA/live-order/API-key paths remain blocked unless Human Owner governance changes the boundary.
```
