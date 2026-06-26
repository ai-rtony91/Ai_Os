# Validator Routing Rules

Validators are checks. They should inspect and report before a change is trusted.

Validator routes:

- UI-only: dashboard boundary check, readability check, mobile layout check.
- Logic-only: state consistency check, no hidden execution check.
- Mock-data-only: JSON parse check and fixture-only check.
- Trading-Lab-only: Trading Lab DRY_RUN validator, default paper/simulation boundary check, and broker-gate check.
- Connector/API-only: connector boundary check, API boundary check, secrets check.
- Mixed scope: change collision check.
- Orchestrator changes: orchestrator readiness check.

Dock player example:

If the dock player icon state is wrong, run a dashboard state consistency check. If the fix changes mock data, also run JSON parse. If the fix touches connector/API work, stop and route to connector/API boundary review.

Validators may recommend repair work, but they must not perform automatic repair unless a separate APPLY approval allows it.
