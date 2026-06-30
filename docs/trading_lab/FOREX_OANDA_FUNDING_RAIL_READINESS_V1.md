# Forex OANDA Funding Rail Readiness V1

## Purpose

This document describes a read-only readiness evaluator for OANDA funding rail planning. It helps the owner review deposit, withdrawal, ACH, wire, same-name bank, withdrawal hierarchy, timing, fee-risk, and lump-sum readiness questions before any money movement decision.

This is not financial advice and does not recommend a deposit amount.

## OANDA Funding Methods

The evaluator encodes the current OANDA US funding methods as configurable facts:

- debit card
- bank wire transfer
- ACH bank transfer

The evaluator only classifies route constraints. It does not approve, initiate, or simulate a deposit.

## OANDA Withdrawal Hierarchy

The readiness output includes the withdrawal hierarchy:

- Withdrawal method generally follows the deposit method.
- If multiple methods were used, debit card deposit amounts must be exhausted first, then bank wire.
- Debit card withdrawals cannot exceed the total originally deposited using debit card.
- Remaining funds or profits may require an alternative method such as bank wire.
- Bank wire withdrawal requires a bank account in the same name as the OANDA trading account.
- Withdrawal amount must consider account balance minus margin used.
- The owner must keep sufficient funds to avoid margin calls on open trades.

## Processing Time Table

| Rail | Processing estimate |
|---|---|
| Debit card deposit | virtually instant |
| Debit card withdrawal | up to 3 business days |
| Domestic wire deposit | 1 to 3 business days |
| International wire deposit | up to 5 business days |
| ACH deposit | up to 6 days |
| US wire withdrawal | 1 to 2 business days |
| International wire withdrawal | up to 5 business days |

## Limits Table

| Limit | Value |
|---|---:|
| Debit card monthly deposit limit | 20000 USD per calendar month |
| ACH per-transaction deposit limit | 50000 USD |
| Wire deposit minimum | none stated by OANDA source |
| Wire deposit maximum | none stated by OANDA source |

## Lump-Sum Planning Behavior

If `intended_lump_sum_amount` is missing, the evaluator returns `PLANNING_ONLY`, adds `intended_lump_sum_amount` and `intended_funding_date` to `missing_information`, and instructs the owner to decide amount/date outside AIOS before rerunning readiness.

If `intended_lump_sum_amount` is present, the evaluator does not approve it, does not recommend it, and does not calculate suitability. It only classifies route constraints:

- debit card over 20000 USD flags `debit_card_monthly_limit_exceeded`
- ACH over 50000 USD flags `ach_transaction_limit_exceeded`
- domestic or international wire requires same-name proof and fee review
- wires have no stated OANDA minimum or maximum deposit limit in the encoded facts

## Safety Boundary

This feature is read-only. It is not a transfer tool, deposit tool, withdrawal tool, bank automation, broker API execution, live trading, or financial advice.

No money movement, no credentials, and no transfer initiation are allowed. The evaluator must not request, store, print, or echo routing numbers, account numbers, debit card numbers, card numbers, CVV values, passwords, API keys, tokens, secrets, credentials, OANDA credentials, or bank credentials.

Only Anthony, as Human Owner, can decide whether to deposit, withdraw, transfer, wire, or fund a lump sum.
