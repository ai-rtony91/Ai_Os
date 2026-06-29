# Forex Live Execution Readiness Lane V1

## Target

- supervised demo -> controlled micro-live exception -> 22hr/day, 6day/week autonomous execution

## Current packet scope

- This packet is repo-safe.
- It does not place trades.
- It does not access the broker API.
- It does not read credentials.
- It does not read `.env`.
- It does not authorize demo or live trading.
- It defines the exact staged readiness path from proof to micro-live readiness.

## Lane contract

The lane currently accepts a typed input and returns a typed result with a strict stage status.

- Proof must be complete before execution readiness begins:
  - `forex_110_closed`
  - `persistent_profitability_ready`
  - `walkforward_oos_proven`
- If proof is present, the next step is broker read-only readout preparation.
- If read-only is prepared, the next step is owner handoff for runtime credentials persistence.
- If credentials and controls are ready, the lane requires owner demo approval.
- If demo approval is ready and micro-live exception is not approved, the lane returns controlled-demo execution readiness.
- If micro-live exception approval is ready, the lane returns controlled micro-live exception readiness.

## Current target state

- `lane_status`: `BROKER_READ_ONLY_PREP_REQUIRED` for the default current-state input.
- `current_stage`: `execution_readiness`
- `next_stage`: `broker_read_only_state_probe`

## Next real build target

1. broker read-only state probe
2. credential persistence owner handoff
3. execution control stack
4. supervised demo approval
