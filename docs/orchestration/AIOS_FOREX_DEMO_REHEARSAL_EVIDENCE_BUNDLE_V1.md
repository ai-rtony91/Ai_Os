# AIOS_FOREX_DEMO_REHEARSAL_EVIDENCE_BUNDLE_V1

## What This Is

This is the operator-readable plan for the next safe forex milestone after the source-chain closeout.

It defines the evidence AIOS must produce in a paper/demo-review rehearsal before any future live micro-trade approval can even be considered.

## Why It Exists

The forex source chain is complete, and the full `forex_engine` suite is green:

```text
python -m pytest tests/forex_engine -q
1048 passed
git status: ## main...origin/main
```

Green tests do not authorize live trading. This evidence bundle creates the next review layer between working source files and any future protected live exception.

## Evidence That Must Be Produced

The rehearsal bundle must include:

- input market snapshot summary
- normalized market state
- strategy candidates generated
- rejected candidates and reasons
- selected candidate IDs
- risk sizing output
- order preview output
- paper fill output
- lifecycle transition log
- balance before/after
- realized/unrealized PnL fields if applicable
- evidence ledger summary
- session replay summary
- safety boundary report
- blocker list
- human review checklist
- next-action recommendation

## What Remains Blocked

AIOS still cannot:

- place live trades
- submit broker orders
- use real credentials
- read account IDs
- bypass human approval
- claim guaranteed profit
- guarantee 120% profit
- use dashboard display as trading authority

No broker calls, credential reads, live execution, order submission, scheduler, daemon, or webhook behavior is allowed.

Network calls remain blocked unless a future packet explicitly approves a demo-readonly probe.

## Approval Gates Before Future Live Review

Any future live micro-trade consideration requires:

- regression suite green
- demo rehearsal evidence bundle complete
- risk limits present
- kill switch present
- rollback plan present
- broker boundary reviewed
- credential isolation reviewed
- human approval recorded
- single-live-micro-trade exception checklist completed

## Next Safe Action

```text
Run paper/demo rehearsal evidence bundle generation packet
```

## Forbidden Next Action

```text
Place live trade
```

## Final Status

```text
DEMO_REHEARSAL_EVIDENCE_BUNDLE_DEFINED = true
SOURCE_CHAIN_COMPLETE = true
FOREX_ENGINE_REGRESSION_GREEN = true
LIVE_TRADING_ALLOWED = false
BROKER_SUBMIT_ALLOWED = false
NEXT_ALLOWED_ACTION = Run paper/demo rehearsal evidence bundle generation packet
NEXT_FORBIDDEN_ACTION = Place live trade
```

