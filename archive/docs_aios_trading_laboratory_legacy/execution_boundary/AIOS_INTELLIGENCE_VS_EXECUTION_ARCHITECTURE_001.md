# AI_OS Intelligence vs Execution Architecture 001

## Separation Rule

AI_OS separates intelligence from execution.

The intelligence layer can produce recommendations, paper simulations, rankings, scorecards, telemetry, and risk notes. It cannot place live orders.

The execution layer is not connected. It remains paper-only and blocked until a separate approval architecture exists.

## Intelligence Layer

Allowed:

- analyze
- rank
- score
- simulate
- recommend
- generate telemetry

Not allowed:

- live order placement
- broker API access
- webhook execution
- autonomous deployment
- self-modifying execution logic

## Execution Layer

Execution permissions are constrained to:

- PAPER_ALLOWED
- LIVE_BLOCKED
- SIMULATION_ALLOWED
- BROKER_DISCONNECTED

No direct LLM output is allowed in a live order path.

## Permanent Boundary

The execution isolation boundary is permanent. Future execution work must be designed as a separate, approved, audited system with telemetry, paper validation, and independent permission controls.
