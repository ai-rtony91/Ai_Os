# AIOS Stage 8 Execution Boundary DRY_RUN

Status: Draft scaffold
Mode: Documentation only

## Purpose

Define the execution boundary before any broker adapter can be considered for sandbox or paper-trading workflows.

## Boundary Requirements

- Broker adapter interfaces must be documented before implementation.
- OANDA usage is sandbox-only unless a future explicit approval changes policy.
- Webhooks require validation, authentication design, replay protection, and audit logging before use.
- Order routing requires safety gates and kill-switch checks before any executable path exists.
- Paper-trade journals must remain separate from live broker order records.

## Blocked Actions

- Live OANDA execution.
- Live broker API connection.
- Real credentials.
- Broker order placement.
- Automated live trading.

## Human Approval

Any future APPLY work that creates executable broker code requires a separate DRY_RUN and explicit approval.
