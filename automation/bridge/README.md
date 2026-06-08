# AI_OS Phase Bridge

Status: subordinate implementation.

This folder contains local bridge utilities that read existing AI_OS governance, queue, approval, validator, telemetry, and self-build evidence. These files do not replace `AGENTS.md`, `README.md`, or the canonical governance/workflow docs.

Run from the repo root:

```powershell
python automation/bridge/aios_phase_bridge.py --mode DRY_RUN --repo-root .
```

Writes evidence under:

- `Reports/phase_0_to_4_bridge/`
- `telemetry/approval_inbox/`
- `telemetry/validator_results/`

Refuses commit, push, merge, live trading, broker execution, and secret handling.

