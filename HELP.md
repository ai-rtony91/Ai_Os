# AI_OS Help / Operator Handoff

Prepared from `AI_OS_friend_handoff_2026-05-14.csv` on 2026-05-14.

This file is a repo-root starting point for a friend/operator picking up AI_OS. It is intentionally plain-language and safe: no passwords, API keys, secrets, tokens, or live trading credentials are included.

## Start Here

1. Read this file before editing.
2. Inspect repo state before making changes.
3. Work in DRY_RUN first, then apply only approved file changes.
4. Keep the product aligned to a guided workspace with human approval gates, reversible workflows, telemetry, and modular workspaces.
5. Treat Trading Lab as the first serious production vertical, but keep all trading work paper-only until validation, latency, and risk gates pass.

## Project Identity

- Project name: AI_OS / AIOS / AI-OS.
- Main product: a guided AI operating environment and orchestration layer.
- Primary MVP: AI_OS Core Platform first, Trading Lab as first completed vertical.
- Product philosophy: beginner-readable guided workspace, safe approval gates, reversible workflows, telemetry, orchestration, and modular workspaces.
- Avoid reframing this as full autonomous AGI or a full live trading bot.

## Repository Notes

- GitHub remote: `https://github.com/ai-rtony91/Ai_Os.git`
- Normal branch: `main`, tracking `origin/main`.
- Usual local working copy: `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN`
- OneDrive-backed repos can have sync timing/conflict issues. Avoid mass edits while sync is unstable.

Before work:

```powershell
git status --short --branch
```

Commit rules:

- Never assume clean state.
- Use selective `git add` with exact file paths only.
- Do not push broad unreviewed changes.
- End every work pack with current location and clean/dirty status.

## Protected / Sensitive Areas

Do not edit protected root governance files unless the user explicitly approves the exact change. If a protected change is needed, propose it in DRY_RUN first.

Known local-only / review-required item from the handoff:

- `Reports/security/AIOS_SECURITY_BASELINE_20260513_182335.txt`
- Do not commit this file or folder without approval.
- Do not delete it without approval.
- Consider an ignore/archive decision only after approval.

## Current Work Focus

Recommended next Big Pack:

1. Trading Lab Dashboard expansion.
2. Latency and evidence ledger.
3. Approval Inbox schema.
4. Dispatcher skeleton.
5. Clean-State Verifier.

Use fewer, larger, focused workload packs instead of many tiny prompts.

## Trading Lab Rules

- Paper-only until evidence, risk, and latency gates pass.
- Build visible, repeatable evidence loops before any live execution.
- Add latency ledger/dashboard before live integrations.
- Use a strategy registry plus market adapters.
- Apply adaptive-confidence freeze rules across market adapters.
- TradingView should be used for signal handoff and latency measurement planning.
- TradersPost can be a reference pattern for paper-route handoff.
- OANDA/live broker work stays deferred until gates pass.

Hard warning: do not enable live trading.

## Dashboard Direction

- Main dashboard path from handoff: `apps/dashboard`.
- Keep one primary Trading Lab/front-door action visible.
- Simplify first; expand advanced controls only behind clear advanced UI.
- Use plain labels and simple next-safe-action language.
- Use `localStorage` only for safe UI preference state.

## Automation Direction

- One worker = one clean objective.
- Use 5-10 worker windows only when each has isolated packet and file ownership.
- Build Lead Dispatcher skeleton and packet rules first.
- Create Approval Inbox schema and sample items.
- Wire Clean-State Verifier into dispatcher/commit package.
- Use packet queue and locks before scaling to many parallel windows.

## Telemetry / Reporting

Add or maintain daily metrics/work packet ledgers for:

- progress percent
- completion prediction / timer fields
- validation results
- current location
- next packet queue
- clean/dirty repo status

Verify each report file before committing.

## Tooling Notes

- PowerShell: use exact commands from the repo path.
- Git: selective add approved files only.
- OpenAI Codex CLI: DRY_RUN -> approval -> APPLY -> validation -> selective commit.
- Cloudflare/cloudflared: move toward named tunnel + Access hardening later.
- Windows Task Scheduler/startup automation: keep automation visible and reversible.
- ChatGPT: use for strategy and handoff, not direct live trading execution.

## Definition of Done for Work Packs

A work pack is done only when it reports:

- What changed.
- Exact files changed.
- Validation run and result.
- Remaining risks or blockers.
- Current branch/location.
- Clean or dirty repo status.
- Next recommended packet.
