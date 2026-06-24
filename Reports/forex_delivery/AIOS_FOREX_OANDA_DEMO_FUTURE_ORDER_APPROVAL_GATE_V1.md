# AIOS Forex OANDA Demo Future Order Approval Gate V1

## 1. Gate Purpose

This report records the local approval gate for considering a future corrected OANDA demo order
attempt after the prior one-order cap was consumed and the SL/TP correction path was created.

The gate does not authorize order execution. It only classifies whether the evidence is complete
enough for a Human Owner manual decision.

## 2. Required Prior Evidence

The gate requires:

- corrected order command package ready: `CORRECTED_ORDER_COMMAND_PACKAGE_READY`
- SL/TP validation ready: `SLTP_VALIDATION_READY`
- prior cancel evidence captured
- prior order cap consumption acknowledged
- explicit new owner approval present

If any of those are missing, the gate blocks before any runtime command can be considered.

## 3. Prior Cancel State

Prior sanitized evidence remains:

- result bucket: `CANCELED_NOT_FILLED`
- cancel reason: `TAKE_PROFIT_ON_FILL_LOSS`
- order attempt count: `1`
- no `orderFillTransaction` observed
- no fill claimed
- no profit claimed
- second order allowed: `false`

## 4. Manual Owner Decision Boundary

Ready classification:

```text
OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION
```

This is not execution permission. It means the owner may manually decide whether a separately
approved future demo order attempt should be prepared. Codex must not run a broker command.

## 5. Block Classifications

The approval gate can block with:

```text
BLOCKED_BY_MISSING_CORRECTED_PACKAGE
BLOCKED_BY_MISSING_SLTP_VALIDATION
BLOCKED_BY_PRIOR_CANCEL_NOT_CAPTURED
BLOCKED_BY_ORDER_CAP_NOT_ACKNOWLEDGED
BLOCKED_BY_MISSING_OWNER_APPROVAL
BLOCKED_BY_LIVE_ENDPOINT
BLOCKED_BY_AUTONOMY_REQUEST
BLOCKED_BY_PROFIT_CLAIM
```

## 6. Demo Only And One Order Only

The gate requires demo-only, one-order-only, no-live-endpoint, no-autonomous-order, and
post-trade-evidence-required confirmations.

It creates no scheduler, daemon, webhook, retry loop, unattended path, live endpoint authority,
or automatic order authority.

## 7. No Broker Or Secret Access

This gate is local classification only. It does not call OANDA, place an order, read credentials,
read account IDs, read Windows Vault, read environment variables, read `.env`, write telemetry,
or persist secret material.

## 8. Exact Evaluation Template

```powershell
python scripts/forex_delivery/run_oanda_demo_future_order_approval_gate_v1.py --evaluate-future-order-approval --corrected-order-package-ready --sltp-validation-ready --prior-cancel-evidence-captured --prior-order-cap-consumed-acknowledged --explicit-new-owner-approval --demo-only --one-order-only --no-live-endpoint --no-autonomous-order --post-trade-evidence-required --no-profit-claim
```

The command returns sanitized JSON only. Even when it returns
`OWNER_APPROVAL_GATE_READY_FOR_MANUAL_DECISION`, the output must be treated as a manual decision
gate, not as permission for Codex to run a broker command.

## 9. Next Safe Action

Next safe action:

```text
owner_manual_decision_only_no_broker_command_by_codex
```

No future order command may be run unless a separate Human Owner-approved packet explicitly
authorizes that exact runtime action.
