# AIOS Forex OANDA Demo Micro Trade Owner Approval Evidence Capture V1

## Packet ID

AIOS-MERGE-1046-THEN-FOREX-DEMO-MICRO-TRADE-OWNER-APPROVAL-EVIDENCE-CAPTURE-V1

## Branch

feature/forex-demo-micro-trade-owner-approval-evidence-capture-v1

## Mission Outcome

Created the next Forex profitability execution layer for governed OANDA demo micro-trade owner review. The lane accepts only sanitized in-memory evidence, requires the prior profitability bridge to be ready for owner review, requires explicit owner acknowledgement fields, requires pre-trade evidence, and classifies post-trade realized P/L evidence as profit, loss, or breakeven.

## Why This Is The Next Profitability Milestone

PR #1046 created the structure gate for a profit-seeking OANDA demo micro-trade. This packet adds the owner approval and evidence capture gate that must exist before any separate runtime-only order ticket can be reviewed. It turns the proposed trade package into an auditable before/after evidence record without placing the trade.

## Why This Still Does Not Place A Trade

The evaluator has no broker import, no network path, no file read, no environment read, no credential access, no account identifier access, no persistence, no scheduler, no daemon, no webhook, and no order-placement logic. It returns a JSON-serializable readiness and evidence classification dictionary only.

## Owner Approval Gates

- `owner_review_required` must be true.
- `owner_approved_runtime_only_demo_review` must be true.
- `owner_approved_live_trading` must be false.
- `owner_approved_autonomous_execution` must be false.
- Anthony must acknowledge loss risk.
- Anthony must acknowledge there is no profit guarantee.
- Anthony must acknowledge stop loss is required.
- Anthony must acknowledge take profit is required.

## Pre-Trade Evidence Required

- candidate id
- instrument
- direction
- planned entry
- stop loss
- take profit
- position size units
- risk amount
- reward/risk ratio
- spread snapshot
- balance snapshot
- NAV snapshot
- margin available snapshot
- kill switch state
- daily stop state
- max loss gate state
- UTC timestamp
- `evidence_source == sanitized_runtime_input`

## Post-Trade Evidence Required

- realized P/L
- exit price
- close reason
- trade duration minutes
- post-trade balance
- post-trade NAV
- UTC timestamp
- `evidence_source == sanitized_runtime_input`

## Profit/Loss/Breakeven Outcome Handling

- `realized_pl > 0` returns `EVIDENCE_CAPTURE_COMPLETE_PROFIT`.
- `realized_pl < 0` returns `EVIDENCE_CAPTURE_COMPLETE_LOSS`.
- `realized_pl == 0` returns `EVIDENCE_CAPTURE_COMPLETE_BREAKEVEN`.
- Missing post-trade fields return `EVIDENCE_CAPTURE_AWAITING_POST_TRADE_RESULT` with deterministic blockers.

## Execution Authority Remains False

All execution authority fields remain false in every result:

- `execution_allowed`
- `demo_order_allowed`
- `live_order_allowed`
- `broker_write_allowed`
- `autonomous_order_allowed`
- `scheduler_allowed`
- `daemon_allowed`
- `webhook_allowed`

## Validation Results

- `python -m py_compile automation/forex_engine/oanda_demo_micro_trade_owner_approval_evidence_capture_v1.py tests/forex_engine/test_oanda_demo_micro_trade_owner_approval_evidence_capture_v1.py`: PASS
- `python -m pytest tests/forex_engine/test_oanda_demo_micro_trade_owner_approval_evidence_capture_v1.py -q`: PASS, 16 passed
- `python -m compileall automation/forex_engine tests/forex_engine`: PASS
- `git diff --check`: PASS

## Git Status

Expected local APPLY state before exact-file staging. `docs/legal/` remains outside lane and untouched.

## Next Safe Action

Run the scoped validator chain, stage only the three approved Forex evidence-capture files, commit, push, and open the PR into `main`. Do not merge, do not call broker, and do not place a trade.
