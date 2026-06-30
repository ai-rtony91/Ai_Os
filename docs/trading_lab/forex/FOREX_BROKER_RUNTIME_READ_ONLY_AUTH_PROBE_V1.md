# Forex Broker Runtime Read-Only Auth Probe V1

## Packet scope

- This packet is the first owner-run broker runtime auth bridge.
- It uses Bitwarden cloud references created and maintained by the owner.
- The required reference is:
  - `AIOS / OANDA / Practice Demo / Broker Runtime`
- Required fields are:
  - `broker_api_token`
  - `broker_account_id`
  - `endpoint`
  - `environment`
  - `allowed_mode`

## Hard boundaries

- This packet does not store raw secrets.
- This packet does not write raw secrets to state or reports.
- This packet does not print raw secrets.
- This packet does not read `.env`.
- Dry-run is the default execution mode.
- Runtime probe requires explicit `--owner-approved-read-only-probe`.
- Runtime probe requires `BW_SESSION` in process environment.
- Runtime mode may call `bw get item "AIOS / OANDA / Practice Demo / Broker Runtime"` only.
- Runtime mode may call only OANDA practice read-only account summary.
- Runtime mode enforces endpoint `https://api-fxpractice.oanda.com`.
- Runtime mode enforces environment `practice_demo`.
- Runtime mode enforces `allowed_mode=read_only_until_owner_demo_approval`.
- It cannot place orders.
- It cannot authorize demo trading.
- It cannot authorize live trading.
- It cannot call order create, replace, cancel, position close, trade open/close,
  account transfer, or any live endpoint.
- It does not read vault secrets from `.env` or environment files.

## Probe target behavior

- Success state moves to `execution_control_stack`.
- Current path remains:
  - supervised demo -> controlled micro-live exception -> 22hr/day, 6day/week autonomous execution.
