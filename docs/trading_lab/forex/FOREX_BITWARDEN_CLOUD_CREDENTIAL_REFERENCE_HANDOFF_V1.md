# Forex Bitwarden Cloud Credential Reference Handoff V1

## Packet scope

- This packet uses the owner-created Bitwarden cloud item and the reference map.
- It stores item names and field names only.
- It stores no credential token values or account values.
- It does not call Bitwarden CLI.
- It does not read Bitwarden vault contents.
- It does not call broker APIs.
- It does not place trades.
- It does not authorize demo or live trading.

## Execution target

- supervised demo -> controlled micro-live exception -> 22hr/day, 6day/week autonomous execution.

## Handoff design

This packet records only non-secret references:

- `broker_runtime_item_ref`: `AIOS / OANDA / Practice Demo / Broker Runtime`
- `credential_reference_map_item_ref`: `AIOS / Bitwarden / Credential Reference Map`
- Field names only for:
  - `broker_api_token`
  - `broker_account_id`
  - `endpoint`
  - `environment`
  - `allowed_mode`

No raw credential data is ever stored in this packet.

## Next real packet

- Next real packet is broker runtime read-only auth probe.
