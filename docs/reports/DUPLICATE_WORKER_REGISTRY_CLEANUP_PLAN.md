# Duplicate Worker Registry Cleanup Plan

Packet: AIOS-DUPLICATE-CANONICAL-WORKER-REGISTRY-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Executive Finding

AI_OS has two files named `AIOS_WORKER_REGISTRY.json`, but they are not safe to treat as simple duplicates.

The canonical worker authority is:

```text
automation/orchestration/workers/AIOS_WORKER_REGISTRY.json
```

The second file is active runtime/window presentation support:

```text
automation/window_identity/AIOS_WORKER_REGISTRY.json
```

Deletion is not safe now. The safer path is to demote/rename the window identity file in a later APPLY lane after updating active consumers to a clearer name such as:

```text
automation/window_identity/AIOS_WINDOW_IDENTITY_REGISTRY.json
```

Final recommendation: DEMOTE.

## Authority Finding

Repository authority names the orchestration worker registry as canonical:

- `automation/orchestration/README.md` lists `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` as the worker registry canonical path.
- `docs/audits/active-system-map.md` classifies `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` as canonical per orchestration README and `KEEP ACTIVE`.
- `docs/audits/active-system-map.md` classifies `automation/window_identity/AIOS_WORKER_REGISTRY.json` as a window identity worker registry with `NEEDS USER DECISION`.
- `automation/orchestration/workers/Get-AiOsWorkerStateOwnership.ps1` reports: orchestration registry is canonical for worker identity; window identity registry is terminal presentation.
- `automation/orchestration/recommendations/Resolve-AiOsSourceOfTruth.ps1` maps worker registry authority to `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` and explicitly avoids `automation/window_identity/AIOS_WORKER_REGISTRY.json` as window presentation only.

## Canonical Registry Recommendation

Keep this file as the canonical logical worker registry:

```text
automation/orchestration/workers/AIOS_WORKER_REGISTRY.json
```

Reason:

- It is referenced by orchestration routing, worker launch previews, worker inbox helpers, status displays, validators, runtime state bundle generation, source-of-truth resolution, and schema validation.
- It contains logical worker IDs, worker types, purposes, allowed actions, blocked actions, and window markers.
- Repo authority already names it as the active canonical worker registry.

## Duplicate Registry Recommendation

Do not delete this file now:

```text
automation/window_identity/AIOS_WORKER_REGISTRY.json
```

Demote it later to a window/layout binding registry. Recommended future name:

```text
automation/window_identity/AIOS_WINDOW_IDENTITY_REGISTRY.json
```

Reason:

- It is actively read by `Set-AiOsWindowIdentity.ps1` and `Show-AiOsWorkerHud.DRY_RUN.ps1`.
- It contains unique terminal display metadata not present in the orchestration registry.
- It contains one unique window-only entry, `CLAUDE REVIEWER`.
- It supports window title, banner, color, theme, begin/end markers, enabled state, and next command hints.

## Comparison Table

| File | Current role | Authority status | Main data | Active consumers | Delete now? |
|---|---|---|---|---|---|
| `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | Logical worker registry | Canonical worker identity authority | `worker_id`, `window_marker`, `type`, `purpose`, `allowed_actions`, `blocked_actions` | Orchestration scripts, validators, status tools, worker router, worker inbox helpers | No |
| `automation/window_identity/AIOS_WORKER_REGISTRY.json` | Terminal/window identity registry | Runtime/window presentation support, decision needed | `marker`, `title`, `color`, `theme`, `identityBanner`, markers, role, next command, enabled state | Window identity scripts, HUD scripts, address-book bridge | No |

## Unique Data Found

### Unique to orchestration registry

- Stable logical worker IDs:
  - `supervisor_loop`
  - `approval_processor`
  - `task_generator`
  - `runtime_daemon`
  - `pr_gate`
  - `health_monitor`
  - `validator_worker`
- Worker `type`.
- Worker `purpose`.
- Machine-friendly `allowed_actions`.
- Machine-friendly `blocked_actions`.
- `window_marker` bridge field.

### Unique to window identity registry

- UI/window markers and titles.
- Emoji code points and fallback titles.
- Console colors and themes.
- Identity banners.
- Begin and end markers.
- Marker fill and width.
- Operator-facing role descriptions.
- Human-facing allowed/blocked action phrasing.
- `nextCommand` hints.
- `enabled` flags.
- Unique window-only worker:
  - `CLAUDE REVIEWER`

### Unique to worker profiles

The cleanup should not ignore:

```text
automation/orchestration/workers/AIOS_WORKER_PROFILES.json
```

This file contains deeper routing/capability data:

- default path
- default branch
- owned paths
- blocked paths
- parallel compatibility
- overlap exclusions
- launch policy
- Codex policy
- guard policy
- save policy

It should remain a separate canonical capability/profile source unless a future schema consolidation explicitly absorbs it.

## Bridge Validation Evidence

`automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1 -QuietJson` returned:

```text
status: WARN
orchestration_workers: 7
window_workers: 8
matched_workers: 7
matched_by_window_marker: 7
orchestration_only: 0
window_only: 1
drift_items: 28
missing_layout_markers: 0
blockers: 0
```

Interpretation:

- All orchestration workers have matching window markers.
- The window registry has one extra window-only support worker: `CLAUDE REVIEWER`.
- There are no bridge blockers.
- There is role/action drift because the two registries express different concerns, not because one file is safely removable.

`automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1 -QuietJson` returned:

```text
status: WARN
primary_visible_workers: 4
primary_visible_mapped: 4
registered_support_workers: 4
total_entries: 8
blockers: 0
warnings: 7
```

Interpretation:

- The address book intentionally reads both registries.
- Four primary visible workers are mapped.
- Support drift remains, especially for `STANDBY WORKER`, `PACKET QUEUE`, `RECOVERY HEALTH`, and window-only `CLAUDE REVIEWER`.

## Scripts Referencing Orchestration Registry

Observed active references include:

- `scripts/workers/Get-AiOsWorkerLanes.ps1`
- `automation/orchestration/worker_runtime_bootstrap.py`
- `automation/orchestration/sync-worker-registry.ps1`
- `automation/orchestration/telemetry_viewer/Show-AiOsTelemetryViewer.DRY_RUN.ps1`
- `automation/orchestration/supervisor/Get-AiOsOvernightSupervisorPlan.DRY_RUN.ps1`
- `automation/orchestration/show-worker-status.ps1`
- `automation/orchestration/worker_builder/New-AiOsWorker.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-AiOsOrchestrationSchemaContracts.DRY_RUN.ps1`
- `automation/orchestration/validators/Test-AiOsSourceOfTruthResolution.ps1`
- `automation/orchestration/workers/Test-AiOsWorkerSelfAwareness.DRY_RUN.ps1`
- `automation/orchestration/router/Invoke-AiOsTaskRouter.DRY_RUN.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerRegistry.DRY_RUN.ps1`
- `automation/orchestration/workers/inbox/Add-AiOsWorkerInboxItem.DRY_RUN.ps1`
- `automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1`
- `automation/orchestration/runtime/Get-AiOsRuntimeStateBundle.DRY_RUN.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1`
- `automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerStateOwnership.ps1`

Conclusion: moving or deleting the orchestration registry would be high risk and directly contradict active authority.

## Scripts Referencing Window Identity Registry

Observed active references include:

- `automation/window_identity/Set-AiOsWindowIdentity.ps1`
- `automation/window_identity/Show-AiOsWorkerHud.DRY_RUN.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1`
- `automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerStateOwnership.ps1`

Related window/layout launch path:

- `automation/window_identity/Open-AiOsWorkerWindowLayout.ps1`
- `automation/window_identity/AIOS_WINDOW_LAYOUTS.json`
- `automation/windows_workstation/Launch-AiOsMorningWorkspace.ps1`

Conclusion: deleting the window identity registry would break worker window identity, HUD display, and the address-book bridge.

## Deletion Risk

### Delete orchestration registry

Risk: BLOCKED.

Expected breakage:

- worker registry schema validation
- worker inbox add helpers
- worker router
- worker launcher preview
- runtime state bundle
- overnight supervisor plan
- source-of-truth resolution
- worker state ownership report
- address-book bridge

Do not delete.

### Delete window identity registry

Risk: HIGH.

Expected breakage:

- `Set-AiOsWindowIdentity.ps1` cannot identify marker metadata.
- `Show-AiOsWorkerHud.DRY_RUN.ps1` cannot render HUD preview.
- `Get-AiOsWorkerAddressBook.ps1` loses display/title/next command information.
- `Test-AiOsWorkerRegistryBridge.ps1` will fail or report missing window registry.
- `Open-AiOsWorkerWindowLayout.ps1` launches marker windows that then call `Set-AiOsWindowIdentity.ps1`; the launched windows would fail identity setup.

Do not delete now.

## Demotion/Rename Risk

Recommended future rename:

```text
automation/window_identity/AIOS_WORKER_REGISTRY.json
-> automation/window_identity/AIOS_WINDOW_IDENTITY_REGISTRY.json
```

Risk: MEDIUM if done with exact-file updates and validators.

Files that must be updated in the same APPLY lane:

- `automation/window_identity/Set-AiOsWindowIdentity.ps1`
- `automation/window_identity/Show-AiOsWorkerHud.DRY_RUN.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1`
- `automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1`
- `automation/orchestration/workers/Get-AiOsWorkerStateOwnership.ps1`
- docs or examples that explicitly name `automation/window_identity/AIOS_WORKER_REGISTRY.json`

Potential docs to update after code passes:

- `docs/audits/active-system-map.md`
- `docs/governance/runtime-ownership-map.md`
- any architecture or workflow docs that call the window file a worker registry

Those docs are protected or outside this packet and require a separate approved APPLY lane.

## Safest APPLY Plan

### Phase 1: DRY_RUN consumer trace

Goal: produce exact current consumer list and expected update list.

Allowed output: report only.

Validation:

```powershell
rg -n "automation/window_identity/AIOS_WORKER_REGISTRY.json|AIOS_WORKER_REGISTRY.json" automation docs services schemas scripts
git status --short --branch
```

### Phase 2: Code-only demotion rename

Goal: rename only the window identity registry and update active code consumers.

Exact files to edit:

```text
automation/window_identity/Set-AiOsWindowIdentity.ps1
automation/window_identity/Show-AiOsWorkerHud.DRY_RUN.ps1
automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1
automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1
automation/orchestration/workers/Get-AiOsWorkerStateOwnership.ps1
```

Exact file to rename:

```text
automation/window_identity/AIOS_WORKER_REGISTRY.json
-> automation/window_identity/AIOS_WINDOW_IDENTITY_REGISTRY.json
```

Do not delete either registry in this phase.

### Phase 3: Documentation authority update

Goal: update protected maps only after code validators pass.

Potential docs:

```text
docs/audits/active-system-map.md
docs/governance/runtime-ownership-map.md
automation/orchestration/README.md
```

This phase requires explicit approval because it touches protected governance/workflow-adjacent authority.

## Exact Files To Delete/Archive In APPLY If Safe

Current recommendation: no deletion and no archive in the first APPLY.

After rename and validation, the old path should disappear only as part of the rename:

```text
automation/window_identity/AIOS_WORKER_REGISTRY.json
```

Do not archive a second copy unless Human Owner explicitly requests an archive. Keeping both names would preserve the ambiguity this cleanup is meant to remove.

## Validator Chain For APPLY

Run after any future APPLY rename/demotion:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1 -QuietJson
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/workers/Get-AiOsWorkerStateOwnership.ps1 -QuietJson
powershell -NoProfile -ExecutionPolicy Bypass -File automation/window_identity/Show-AiOsWorkerHud.DRY_RUN.ps1 -Worker ALL
powershell -NoProfile -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset compact
git diff --check
git status --short --branch
```

Expected proof:

- bridge validator has no blockers.
- address book still maps all primary visible workers.
- HUD preview reads the renamed window identity registry.
- layout preview still generates commands.
- no files outside approved APPLY scope changed.

## Rollback Plan

If the future APPLY rename breaks validation:

1. Restore the old filename:

```text
automation/window_identity/AIOS_WORKER_REGISTRY.json
```

2. Restore the registry path references in:

```text
automation/window_identity/Set-AiOsWindowIdentity.ps1
automation/window_identity/Show-AiOsWorkerHud.DRY_RUN.ps1
automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1
automation/orchestration/workers/Test-AiOsWorkerRegistryBridge.ps1
automation/orchestration/workers/Get-AiOsWorkerStateOwnership.ps1
```

3. Re-run the validator chain above.
4. Do not commit the failed rename.

## Answers To Packet Questions

1. Which file is canonical?
   - `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`.

2. Which scripts read orchestration worker registry?
   - Core orchestration scripts, validators, status tools, router, worker builder, inbox helper, runtime state bundle, and overnight supervisor planner. See the scripts list above.

3. Which scripts read window identity worker registry?
   - Window identity setup/HUD scripts plus address-book/bridge/ownership inspectors.

4. Does either registry contain unique data?
   - Yes. Orchestration has logical worker authority. Window identity has display/window metadata and `CLAUDE REVIEWER`.

5. Is one logical and the other window/layout binding?
   - Yes. That is the correct architecture. The problem is naming, not the existence of both concerns.

6. Would deleting either file break active scripts?
   - Yes. Deleting orchestration registry is blocked. Deleting window identity registry is high risk.

7. Should the duplicate be deleted now?
   - No. Demote/rename later.

8. What files need updates if one registry is renamed?
   - See exact files under "Demotion/Rename Risk."

9. What is the safest cleanup path?
   - Rename the window identity file to a non-canonical binding name and update exact consumers.

10. What validation proves cleanup worked?
   - Worker registry bridge, address book, state ownership, HUD preview, layout preview, diff check, and scoped git status.

## Final Recommendation

Final classification:

```text
automation/orchestration/workers/AIOS_WORKER_REGISTRY.json -> KEEP as canonical logical worker registry
automation/orchestration/workers/AIOS_WORKER_PROFILES.json -> KEEP as canonical capability/profile source
automation/window_identity/AIOS_WORKER_REGISTRY.json -> DEMOTE by rename to window identity binding registry
```

Decision: DEMOTE.

Do not delete. Do not archive first. Rename only through a separate approved APPLY lane with exact consumer updates and validator proof.
