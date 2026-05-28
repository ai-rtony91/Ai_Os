# Invoke-AiOsRuntimeSelfRoute Gate Audit

Mode: APPLY mission audit

## Execution Paths Found

- `powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1 -QuietJson`
  - Source: local recommendation helper output.
  - Purpose: produces `recommended_command`.
  - Execution risk: helper invocation only; not the dynamic recommended command.

- `powershell -ExecutionPolicy Bypass -File automation/orchestration/validators/Test-AiOsRecommendedCommand.ps1 $recommendation.recommended_command`
  - Source: validator path plus generated recommendation command text.
  - Purpose: validates the recommended command before execution.
  - Execution risk: validator invocation only.

- `Invoke-Expression $recommendation.recommended_command`
  - Source: `recommended_command` from the recommendation helper.
  - Purpose: executes the selected runtime self-route action.
  - Risk: highest-risk dynamic command execution path in this script.

## Existing Checks Before This Change

- Approval check: no approval inbox check in this script.
- Validator check: `Test-AiOsRecommendedCommand.ps1` runs before `Invoke-Expression`.
- Gate check: not present before this mission.
- Hard stop check: not present before this mission.

## Gate Insertion Point

The narrow insertion point is immediately after validator success and immediately before:

```powershell
Invoke-Expression $recommendation.recommended_command
```

At that point the exact command text is known, validator output has been reviewed, and no dynamic command has executed yet.

## Wiring Added

The APPLY path now calls:

```powershell
automation/orchestration/gates/gate_runner.ps1
```

with:

- `Mode APPLY`
- exact `CommandText`
- `WorkerId RUNTIME_SELF_ROUTE`
- `TaskId Invoke-AiOsRuntimeSelfRoute`
- current repo root

If the gate is missing, fails, emits invalid JSON, or returns anything other than `AUTO_PROCEED`, the dynamic command is not executed.

## Deferred Paths

No broader runtime scripts, worker loops, queue processors, approval processors, validator chains, or command queues were wired in this pass.
