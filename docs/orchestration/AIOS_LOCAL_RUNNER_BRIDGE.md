# AIOS Local Runner Bridge

`aios_local_runner_bridge.py` converts a bounded executor handoff into a
PowerShell command preview for local human review.

The bridge emits `AIOS_LOCAL_RUNNER_BRIDGE.v1` with runner status, command
preview, working directory, validation commands, forbidden actions, approval
requirements, and safety flags. The working directory is the active repository
path: `C:\Dev\Ai.Os`.

This bridge is preview-only. It does not run commands, start background tasks,
activate a scheduler or daemon, launch workers, call Codex, or mutate any repo
state.
