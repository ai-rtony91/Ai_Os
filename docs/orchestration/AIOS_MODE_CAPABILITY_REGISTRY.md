# AIOS Mode Capability Registry

Schema: `AIOS_MODE_CAPABILITY_REGISTRY.v1`

`automation/orchestration/aios_mode_capability_registry.py` defines the current AIOS build modes and the actions each mode may advertise to the continuation layer.

Current active proof target:

- mode: `forex`
- goal: `forex-paper-bot`
- allowed actions: `build_forex_risk_controls`, `build_forex_paper_execution_simulator`

Reserved or future modes are present so routing can remain generic without pretending those modes are implemented.

Every mode blocks:

- live broker execution
- real order submission
- credential use
- real webhook dispatch
- scheduler or daemon activation
- worker dispatch
- queue or approval mutation
- destructive cleanup

The registry is read-only. It does not execute commands, call APIs, write files, or mutate repo state.
