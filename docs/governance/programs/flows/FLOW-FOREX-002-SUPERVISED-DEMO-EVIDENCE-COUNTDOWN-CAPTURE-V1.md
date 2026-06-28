# FLOW-FOREX-002: Supervised Demo Evidence Countdown Capture V1

## Anchor
Flow 1 PR #1194 is the current anchor.

## Scope
Flow 2 captures supervised demo evidence and countdown update inputs for repo-safe continuation.

## Required captures
- broker/demo snapshot
- TP/SL state
- realized P/L
- duplicate order status
- no runaway exposure status
- post-trade countdown update

## Flow boundary
Flow 2 is repo-safe in artifact construction and evidence schema.
Demo execution commands and live trade activity remain outside this packet boundary.

## Claims
- 100–120% is the target band and not a verified claim.
- 22h/6d is runtime objective, not active state.
- vacation mode is target state, not active state.
