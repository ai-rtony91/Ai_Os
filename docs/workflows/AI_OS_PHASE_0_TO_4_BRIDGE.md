# AI_OS Phase 0 To 4 Bridge

Status: subordinate workflow.

Run from `C:\Dev\Ai.Os`:

```powershell
python automation/bridge/aios_phase_bridge.py --mode DRY_RUN --repo-root .
```

What it writes:

- Phase reports under `Reports/phase_0_to_4_bridge/`
- Approval evidence under `telemetry/approval_inbox/`
- Validator registry evidence under `telemetry/validator_results/`

What it refuses:

- Commit
- Push
- Merge
- Protected root edits
- Live trading
- Broker execution
- Secret handling

What requires Anthony approval:

- Any protected action
- Any root authority edit
- Any commit, push, merge, or PR action
- Any production, broker, credential, or live trading change

Safe validation:

```powershell
python automation/validators/aios_governance_validator.py --sample-check
python automation/self_build/aios_self_build_inspector.py --mode DRY_RUN --repo-root .
git diff --check
```

