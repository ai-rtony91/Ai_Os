# AIOS Forex Broker Proof Runtime-Only Human Intake V1

## Objective
Define the sanitized runtime-only broker proof Anthony must supply before any future arming review. Codex does not call brokers, read credentials, read account IDs, or execute orders.

## Broker Proof Status
`BROKER_PROOF_REQUIRES_RUNTIME_ONLY_HUMAN_INTAKE`

## Required Sanitized Proof Fields
- `broker_alias`
- `environment`
- `proof_timestamp`
- `instrument_availability`
- `connection_proof_status`
- `order_placement_disabled_confirmation`
- `account_id_redacted_confirmation`
- `credential_not_pasted_confirmation`
- `credential_not_persisted_confirmation`
- `broker_ui_balance_redacted_confirmation`
- `human_operator_confirmation`

## Forbidden Fields
- `API keys`
- `passwords`
- `account IDs`
- `card/bank data`
- `account balances tied to account IDs`
- `raw broker secrets`
- `copied .env content`
- `live order commands`
- `auto-trading commands`

## Credential/Account ID Bans
- credentials must not be pasted, read, persisted, logged, or reported
- account IDs and broker order IDs must not be persisted, logged, or reported

## Runtime-Only Proof Doctrine
Broker proof must be supplied as sanitized human intake at arming time. Historical/demo proof and dashboard fixtures are not current broker proof.

## Codex Safety Statements
- no broker call performed
- no credential read
- no account ID read
- no order executed

## Next Safe Action
Produce sufficient paper/demo expectancy evidence with passing walk-forward proof before any arming candidate.
