# AI_OS Path Registry

The AI_OS path registry lists the runtime spine paths that launchers, supervisors, validators, and packet tools depend on.

The goal is to prevent broken paths before they reach Anthony's worker windows or runtime loop. This is a registry and validator only. It does not restructure folders, rename folders, launch apps, create startup tasks, create scheduled tasks, edit dashboard files, edit Trading Lab files, commit, or push.

## Files

- `AIOS_PATH_REGISTRY.json` stores required path keys and relative paths.
- `Test-AiOsPathRegistry.ps1` reads the registry and checks each path from the repo root.

## Validate

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/runtime/path_registry/Test-AiOsPathRegistry.ps1
```

Expected result:

```text
SUMMARY: PASS
```

If any path is missing, the validator prints `FAIL` for that key and exits `1`.

## Registry Keys

- `repo_root`
- `aios_shortcut`
- `window_identity_script`
- `worker_window_launcher`
- `runtime_self_route`
- `persistent_runtime_supervisor`
- `runtime_state_writer`
- `runtime_packet_advancement`
- `work_packets_active`
- `orchestration_runtime_folder`
- `orchestration_health_folder`
- `orchestration_validators_folder`
- `orchestration_approval_processor_folder`
- `orchestration_task_generator_folder`
- `orchestration_recovery_folder`

## Safety

- DRY_RUN/read-only validator only.
- No file edits during validation.
- No startup tasks.
- No scheduled tasks.
- No dashboard edits.
- No Trading Lab edits.
- No `git add`.
- No commit.
- No push.
