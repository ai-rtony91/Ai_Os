# ATM Milestone Contract

Date: 2026-07-01
Packet: AIOS-P26A

The ATM Milestone is a demo-only tipping-bucket milestone: realized demo profit fills `profit_bucket`; when the configured threshold is reached, AIOS produces an owner SOS instruction that tells Anthony what to do next. The milestone ends at the alert. No money moves, no bank action occurs, no broker action occurs, and no live trade is authorized by this milestone contract.

## Invariant

Milestone completion means the SOS alert was produced for owner review. It does not mean a transfer, withdrawal, deposit, broker action, live order, webhook, credential use, or bank action happened.

## Owner Input Surface

The owner-editable input surface is `control/forex/atm_milestone_config.json`.

Config keys:

- `baseline_equity_usd`: demo baseline equity used as the countdown starting number.
- `target_return_band_low_pct`: lower bound of the target return band.
- `target_return_band_high_pct`: upper bound of the target return band.
- `min_profit_to_sweep_usd`: tipping-bucket threshold for owner SOS review.
- `money_movement_allowed`: must remain `false`.
- `bank_access_allowed`: must remain `false`.

## Countdown Closure

S1 island `flow1_target_countdown_bridge` is CLOSED-BY-26A when the countdown receipt shows `profit_return_countdown_status` off `BASELINE_EQUITY_REQUIRED` after baseline equity is supplied.

## SOS Contract (26B)

Lane 26B adds the owner-facing SOS message and milestone response options.

Owner replies are instruction-only:

- `APPROVE`: AIOS logs an owner-reviewed withdrawal proposal. It does not execute a transfer.
- `HOLD`: AIOS keeps compounding in-account under demo/paper evidence. It does not execute a transfer.
- `ADJUST <number>`: AIOS records a proposed new tip threshold in USD for owner review. It does not execute a transfer.

Closure proof for the SOS island is the gate transition `REQUIRED_GATE_PENDING -> SOS_CONTRACT_READY_FOR_FLOW2`.

`APPROVE` queues a proposal only. It does not execute a broker, bank, withdrawal, deposit, transfer, order, webhook, credential, or live-trading action.
