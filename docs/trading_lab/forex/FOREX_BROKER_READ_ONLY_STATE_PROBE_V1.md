# Forex Broker Read-Only State Probe V1

## Execution target

- supervised demo -> controlled micro-live exception -> 22hr/day, 6day/week autonomous execution

## Current packet scope

- This packet is the first execution bridge after the live execution readiness lane.
- It creates a broker read-only probe contract and a nonsecret config template.
- This packet does **not** call the broker API.
- This packet does **not** access credentials or `.env`.
- This packet does **not** place trades.
- This packet does not authorize demo or live trading.
- Mutating capabilities remain blocked in this packet.

## Probe contract

The packet requires a nonsecret template and owner-owned runtime reference handoff before any read-only broker probe path can continue.

## Required next action

- After owner runtime config is present, the next real build target is:
  - credential persistence owner handoff
