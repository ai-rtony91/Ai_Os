# Orchestration Consolidation Apply Sequence

This sequence defines future APPLY packets. It does not perform consolidation.

## Phase C1: Mark Canonical Authority Docs

Goal: add a short canonical authority note to approved docs only.

Allowed examples:

- `automation/orchestration/README.md`
- `docs/workflows/AI_OS_PR_LANE_RUNNER.md`
- `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
- `docs/AI_OS/dispatch/`
- `docs/AI_OS/night_supervisor/`

Stop point: no runtime files touched.

## Phase C2: Add Deprecation Headers To Obvious Legacy Docs Only

Goal: mark old examples or docs as compatibility evidence without moving them.

Rules:

- header only.
- no scripts edited.
- no JSON state edited unless explicitly approved.
- no approval inbox, lock, memory, runtime, Night Supervisor, or Paper SOS paths.

## Phase C3: Update References

Goal: update docs/scripts that point to old examples after canonical replacements are proven.

Validation:

- `rg` confirms old reference count decreases.
- no runtime behavior changes.
- no generated state writes.

## Phase C4: Move Or Archive Duplicate Examples

Goal: move only duplicate examples with zero active readers.

Rules:

- use a dedicated archive path.
- keep provenance.
- do not move active state or runtime evidence.
- do not move approval inbox, lock, memory, Night Supervisor runtime, or Paper SOS files.

## Phase C5: Remove Only Confirmed Dead Files

Goal: delete only files proven dead by reference scan, history review, and operator approval.

Required evidence:

- exact file list.
- replacement path.
- `rg` reference result.
- validator result.
- user approval for delete.

## Phase C6: Validate Night Supervisor And Paper SOS Unaffected

Goal: verify autonomy runway boundaries still hold.

Checks:

- Night Supervisor preview remains preview-only.
- no runtime start.
- Paper SOS expected worktree is explicit.
- `Path.cwd()` and git root checks remain documented.
- no telemetry/control/approval inbox writes.

## Phase C7: Clean-State Verifier

Goal: run final clean-state and PR-lane validation.

Checks:

- `git status --short --branch`.
- allowed-path scope.
- no forbidden files changed.
- no broker/OANDA/live trading.
- no Pi GPIO/motor.
- no secrets or API keys.

## Recommended Next Packet

Run Phase C1 only: mark canonical authority docs and add no deprecation headers yet.

