# Forex Supervised Demo Order Execution V1

## Purpose

This packet creates the first owner-run supervised demo order execution path.
It gates owner-approved execution of a single OANDA practice demo order.

## Scope

- Packet purpose: first owner-run supervised demo order execution stage.
- Scope boundary: this packet supports **one demo order execution** at runtime.
- Default mode: `dry_run` validation.
- Runtime mode requires explicit `--owner-approved-supervised-demo-order`.

## Validation Rules

- Default validation does not place orders.
- Default validation does not call broker APIs.
- Default validation does not call Bitwarden CLI.
- Default validation does not read credentials.
- Default validation does not read `.env`.
- No broker calls, no credentials read, and no money movement in validation mode.

## Runtime Rules

- Runtime mode requires explicit owner flag `--owner-approved-supervised-demo-order`.
- This is OANDA practice only.
- Runtime mode reads Bitwarden only for `AIOS / OANDA / Practice Demo / Broker Runtime`.
- Runtime mode may read only:
  - `broker_api_token`
  - `broker_account_id`
  - `endpoint`
  - `environment`
  - `allowed_mode`
- Runtime mode requires:
  - OANDA practice endpoint only (`https://api-fxpractice.oanda.com`)
  - `practice_demo` environment
  - one of `read_only_until_owner_demo_approval` or `supervised_demo_only`
- Runtime mode may place at most one market order.
- Units default to `1`.
- Order payload includes stop-loss and take-profit contract fields.
- Runtime mode uses only the practice demo order endpoint.

## Safety Gates

- This packet does not authorize live trading.
- This packet does not start scheduler/daemon/webhook runtime.
- This packet does not authorize 22hr/day 6day/week autonomous execution.
- This packet does not start 22h/6d runtime scheduling in this stage.

## Stage Transition

- Success moves to supervised_demo_evidence_review.
- Final target remains live 22hr/day, 6day/week autonomous execution after later supervised gates.
