# AIOS_FOREX_DEMO_REHEARSAL_EVIDENCE_BUNDLE_V1

## Executive Summary

This packet defines the required evidence bundle for a safe paper/demo rehearsal after the AIOS forex source chain reached full regression green.

The source chain is complete and closed out. PR #930 repaired live multi-trade expansion kill-switch evidence, PR #931 stabilized the full `forex_engine` regression suite, and PR #932 landed the source-chain closeout documentation.

Post-merge validation evidence:

```text
python -m pytest tests/forex_engine -q
1048 passed
git status: ## main...origin/main
```

This packet is documentation/report-only. It defines what evidence AIOS must collect before any future live micro-trade approval can even be considered. It does not authorize live trading, broker submission, credential usage, or any execution route.

## Preconditions

Required preconditions before a demo/paper rehearsal evidence bundle is generated:

- Source-chain closeout landed.
- Full `forex_engine` regression suite green: `1048 passed`.
- Repo `main` clean and synced.
- Live execution disabled.
- Broker submit disabled.
- Credential usage disabled.
- Human approval required for any future protected live step.

## Rehearsal Scope

The rehearsal is paper/demo-review only.

It may include:

- market snapshot normalization
- strategy candidate generation
- risk sizing
- order preview
- paper fill simulation
- trade lifecycle processing
- balance compounding
- evidence ledger creation
- session replay
- demo-readonly reconciliation review
- live-readiness review output
- first-live-micro-trade proof review output

It must not place live orders. It must not submit broker orders. It must not read credentials or account IDs.

## Evidence Bundle Required Artifacts

The evidence bundle must contain these required sections:

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

Each artifact must be traceable, deterministic, and reviewable without relying on broker state, live execution, credential reads, or dashboard-only claims.

## Safety Boundary

The demo rehearsal evidence-bundle plan preserves the following safety boundary:

- No broker calls.
- No network calls unless explicitly future-approved for a demo-readonly probe.
- No credential reads.
- No account ID reads.
- No live execution.
- No order submission.
- No scheduler, daemon, or webhook behavior.
- Dashboard displays truth only; dashboard does not create trading truth.

Live trading remains disabled. Broker submit remains disabled. Any future escalation must remain behind protected approval gates.

## Approval Gates

Before any future live micro-trade can be considered, these gates must be satisfied:

- regression suite green
- demo rehearsal evidence bundle complete
- risk limits present
- kill switch present
- rollback plan present
- broker boundary reviewed
- credential isolation reviewed
- human approval recorded
- single-live-micro-trade exception checklist completed

Passing these gates only permits review consideration. It does not itself authorize live trading or broker order submission.

## Pass/Fail Criteria

The rehearsal evidence bundle passes only if:

- rehearsal is paper/demo-review only
- no protected boundary is crossed
- every required artifact is present
- blockers are explicit
- next action is deterministic
- live trading remains false
- broker submit remains false

The bundle fails if any required artifact is missing, if blockers are hidden, if next action is ambiguous, or if any credential, broker, live execution, order submission, scheduler, daemon, webhook, or unauthorized network behavior appears.

## Current Non-Authority

AIOS is still not authorized to place real live trades.

AIOS cannot:

- submit broker orders
- use real credentials
- bypass human approval
- claim guaranteed profit
- guarantee 120% profit
- treat dashboard display state as trading authority

## Final Status Fields

```text
DEMO_REHEARSAL_EVIDENCE_BUNDLE_DEFINED = true
SOURCE_CHAIN_COMPLETE = true
FOREX_ENGINE_REGRESSION_GREEN = true
LIVE_TRADING_ALLOWED = false
BROKER_SUBMIT_ALLOWED = false
NEXT_ALLOWED_ACTION = Run paper/demo rehearsal evidence bundle generation packet
NEXT_FORBIDDEN_ACTION = Place live trade
```

