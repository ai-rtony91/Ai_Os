# Base44 Forex Paper Trading Lab Reference 001

## Status

- External prototype reference only.
- Not AI_OS authority.
- Not imported code.
- Not live trading.
- Not a dashboard redesign.
- Not a theme migration.

## Purpose

This document captures the Base44 prototype handoff for a separate prototype called "AIOS Lab - Forex Paper Trading Lab" as an external design and workflow reference artifact.

The purpose is to preserve useful workflow mapping, entity ideas, and safety-gap observations without importing Base44 code, styling, component behavior, external service assumptions, or visual identity into AI_OS.

## Base44 Gives the Map, AIOS Lab Paints the Map Later

"Base44 is useful for workflow discovery, page mapping, schema ideas, safety-gap discovery, and prototype comparison. AIOS Lab must preserve its own visual identity, product taste, safety model, and repo-governed implementation."

Base44 gives us the map. AIOS Lab paints the map later.

The Base44 artifact may help identify screens, flow, entities, gaps, and workflow structure. It must not define AIOS Lab's visual identity, theme, color taste, typography, app shell, layout style, component style, icons, or branding language.

## What Base44 Created

The Base44 prototype described seven pages:

- Dashboard
- Signal Intake
- Safety Check
- Trade Ledger
- Latency Tracker
- Strategy Studio
- Reports

The Base44 prototype described five component categories:

- AppShell
- LabBadge
- StatCard
- Layout/sidebar support
- Reusable page badges

The Base44 prototype described four entities:

- PaperSignal
- PaperTrade
- Strategy
- LatencyLog

## Useful Workflow Ideas

The prototype workflow was:

```text
Signal Intake -> Safety Check -> Paper Trade Ledger -> Latency Tracker -> Strategy Studio -> Reports
```

Useful workflow ideas for later AI_OS rebuild consideration:

- Separate signal capture from trade logging.
- Route signal review through an explicit safety check before conversion into a paper trade.
- Track latency between signal creation, safety review, and paper-trade entry.
- Keep strategy definitions connected to signal and paper-trade records.
- Produce reports from the paper-only ledger, latency records, and strategy references.
- Use visible paper-mode and simulation-only state throughout the lab workflow.

## Entity / Schema Reference

Reference-only entity notes from the Base44 prototype:

- `PaperSignal`: candidate signal intake record for a paper-only trading lab.
- `PaperTrade`: paper ledger entry created after safety review and conversion.
- `Strategy`: reusable strategy profile or classification record.
- `LatencyLog`: timing record for tracking signal-to-review and review-to-ledger delay.

These names are not authority for AI_OS schema. They are reference terms for future comparison when AI_OS designs its own governed paper-trading laboratory data model.

## Safety Protections Observed

Base44 included these paper-trading safety protections:

- Paper mode labels.
- Live execution blocked badge.
- Simulation-only badges.
- No broker APIs.
- No external services.
- No secrets.
- No real orders.
- No live trading.

## Safety Gaps / Rebuild Requirements

The Base44 handoff identified these safety gaps:

- Safety check is bypassable because ledger entries can be created directly.
- Signal IDs are soft/free-text links.
- Strategy ID is not fully wired.
- Duplicate signal prevention is missing.
- Confirmation before conversion to paper trade is missing.
- Input validation gaps remain.

AI_OS rebuild requirements:

- Make the safety check non-bypassable for paper-trade conversion.
- Use stable internal IDs instead of free-text signal links.
- Wire strategy references through validated identifiers.
- Add duplicate signal detection before paper-trade conversion.
- Require explicit confirmation before creating a paper-trade ledger entry.
- Validate required fields, numeric ranges, timestamps, and allowed enumerations.
- Move critical safety checks out of client-only UI logic into a safer service/backend layer when the system matures.

Known bug captured from the handoff:

- `LatencyTracker` JSX parsing error was fixed by changing `calcDelay(...) > 300` to `(calcDelay(...) ?? 0) > 300`.

Latency and reporting notes:

- Stale signal threshold is 300 seconds / 5 minutes.
- P/L stays in R-multiples, not real money.

## Visual Identity Boundary

AI_OS must not copy Base44's appearance.

Do not copy:

- Base44 colors.
- Base44 CSS.
- Base44 app shell.
- Base44 page layout.
- Base44 typography.
- Base44 icons.
- Base44 components.
- Base44 branding language.

Do not let Base44 overwrite AIOS Lab's dark gamer/studio/lab flavor.

AIOS Lab may later use the workflow map, but must repaint it in its own brand language. Any rebuild must preserve AI_OS visual identity and product taste.

## AI_OS Rebuild Notes

Treat Base44 as a sketchpad/reference only.

AI_OS should rebuild only the useful workflow ideas in its own repo, style, and governed safety system. The rebuild should be scoped, validated, and paper-only.

Future AI_OS implementation should:

- Preserve the AIOS Lab dark gamer/studio/lab flavor.
- Keep paper mode visible across the workflow.
- Keep live trading blocked.
- Keep broker integration out of scope.
- Keep P/L in R-multiples.
- Treat the 300-second latency threshold as an initial stale-signal reference.
- Design service-side safety validation before any mature workflow depends on safety decisions.

## Trading Safety Boundary

This reference does not authorize live trading, real orders, broker APIs, broker webhooks, live market data connections, API keys, secrets, or external trading services.

Blocked items remain blocked:

- OANDA
- Webull
- Alpaca
- TradingView webhooks
- Live broker execution
- Real orders
- Live trading
- Broker API keys or secrets

This document is reference-only and does not change AI_OS trading authority.

## Next Safe Action

Use this reference only as planning input for a future governed AIOS Lab paper-trading rebuild packet.

The next safe action is a DRY_RUN design pass that compares this workflow map against existing AI_OS Trading Lab documents, identifies the smallest useful paper-only workflow slice, and preserves AI_OS visual identity before any implementation work begins.
