# Trading Lab 4 Codex Workload Board

Status: PAPER ONLY, LOCAL ONLY, LIVE EXECUTION BLOCKED

Purpose: Coordinate four Windows Codex workers so Trading Lab work can continue faster without file ownership collisions.

## Global Safety Rules

- No broker execution.
- No OANDA execution.
- No Webull execution.
- No API keys.
- No secrets.
- No real webhooks.
- No real orders.
- No live trading.
- No commits or pushes without explicit user approval.
- Only Codex #4 runs cross-phase validation.
- Only Phase 14.8 may touch dashboard JS/CSS.

## Codex #1 - Signal Logic Lane

Owns: Phase 14.4 SuperTrend MVP Signal Preview.

Allowed focus:
- Paper-only SuperTrend signal preview.
- Trend permission logic.
- Signal preview docs, fixtures, and validators for Phase 14.4.

Must not:
- Touch dashboard JS/CSS.
- Touch TradingView route mocks.
- Touch TradersPost route mocks.
- Treat SuperTrend as a buy/sell trigger.
- Enable broker, webhook, order, API, or live execution.

Safety interpretation: SuperTrend is a paper-only trend permission signal, not a trade command.

## Codex #2 - Payload + Route Mock Lane

Owns:
- Phase 14.5 TradingView Alert Payload Mock.
- Phase 14.6 TradersPost Route Preview Mock.

Allowed focus:
- Local paper TradingView alert payload examples.
- Local paper TradersPost route preview examples.
- Mock contract validation.
- Paper-only handoff fields.

Must not:
- Create real webhooks.
- Connect APIs.
- Touch broker logic.
- Touch OANDA logic.
- Touch order logic.
- Enable API keys, secrets, real orders, or live trading.

Safety interpretation: Payloads and route previews are local mock contracts only.

## Codex #3 - Outcome + Scorecard Lane

Owns: Phase 14.7 Paper Trade Outcome Loop.

Allowed focus:
- Simulated entry.
- Simulated exit.
- R-multiple.
- Win/loss.
- Drawdown.
- Paper-only scorecard metrics.

Must not:
- Touch dashboard UI unless separately approved.
- Add broker execution.
- Add real order placement.
- Add API keys or secrets.
- Enable live trading.

Safety interpretation: Outcomes are simulated paper review records only.

## Codex #4 - Windows Integration / QA Commander

Owns:
- Repo checkpoint.
- Validator runner.
- Conflict detection.
- Phase 14.3 mismatch report.
- Final handoff report.
- Safety verification.

Allowed focus:
- Cross-phase DRY_RUN validation.
- JSON parse checks.
- Git status snapshots.
- Workload handoff notes.
- Collision detection.
- Safety scan for forbidden live execution fields.

Must not:
- Build another feature unless assigned.
- Enable broker execution.
- Enable OANDA execution.
- Enable Webull execution.
- Enable real webhooks.
- Enable real orders.
- Enable live trading.

Safety interpretation: Codex #4 coordinates and verifies; it does not expand scope.

## Collision Rules

- Only Codex #4 runs cross-phase validation.
- Only Phase 14.8 may touch dashboard JS/CSS.
- No one touches Music Companion.
- No one touches SSO/Auth.
- No one touches Crypto Wallet.
- No one touches Social Trading.
- No one touches Voice Commands.
- No one commits or pushes without explicit approval.
- No one enables live execution.
- Workers must report file paths before editing.
- Workers must stop if their assigned lane overlaps another lane.

## Phase Ownership Summary

| Phase | Owner | Scope | Dashboard Access |
| --- | --- | --- | --- |
| 14.3 | Codex #4 | Mismatch checkpoint only | No |
| 14.4 | Codex #1 | SuperTrend paper signal preview | No |
| 14.5 | Codex #2 | TradingView payload mock | No |
| 14.6 | Codex #2 | TradersPost route preview mock | No |
| 14.7 | Codex #3 | Paper outcome and scorecard loop | No, unless separately approved |
| 14.8 | Unassigned until approved | Dashboard visibility | Yes, Phase 14.8 only |

## Current Next Move

Codex #4 should run the Windows control tower DRY_RUN validator, review its report, and then assign Codex #1 to Phase 14.4 only if the safety scan passes.
