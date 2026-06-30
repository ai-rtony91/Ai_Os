# Forex Live Execution Program V1

This packet is the integrated live execution program lane.

## Target

- Goal: live Forex execution at `22hr/day, 6day/week` with staged owner approvals.
- This lane targets `live 22hr/day, 6day/week` execution runtime planning.
- This program builds the end-to-end execution path from broker auth proof through
  controlled demo, controlled micro-live exception, live lane, and autonomous runtime planning.

## Stage Gate Path

`broker_runtime_read_only_auth_proven` -> `execution_control_stack` ->
`supervised_demo` -> `micro-live exception` -> `live lane` ->
`autonomous 22hr/day 6day/week`.

## Validation-Only Boundaries

- This packet does not execute demo or live orders during validation.
- This packet does not call broker APIs during validation.
- This packet does not read Bitwarden during validation.
- This packet does not call Bitwarden CLI during validation.
- This packet does not read credentials during validation.
- This packet does not read `.env` during validation.
- This packet does not start schedulers, daemons, or webhooks.

## Approval Gates

- Requires supervised demo approval before demo order execution.
- Requires clean demo evidence before micro-live exception.
- Requires micro-live approval and clean micro-live evidence before live lane.
- Requires owner live trading approval before any live order.
- Requires separate owner approval before 22h/6d autonomous runtime.

## Current Runtime Contract

- `broker_runtime_read_only_auth_proven`: default true.
- `execution_control_stack_landed`: default true.
- `execution_control_stack_ready`: default false until owner-approved demo stage is confirmed.
- All protected action flags remain false by design in evaluator output.

## Current Next Stage

Current next stage is `owner_supervised_demo_approval`.
Current next stage is owner_supervised_demo_approval.
