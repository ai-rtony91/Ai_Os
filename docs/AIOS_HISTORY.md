# AI_OS History

## 2026-05-18 — Spine Consolidation Cleanup

Canonical authority:
- `aios.ps1`

What changed:
- Routed morning operations through `aios.ps1`
- Removed legacy unmanaged launchers
- Removed duplicate build engine launchers
- Removed obsolete worker/operator wrappers
- Removed abandoned bootstrap display wrappers

Architecture decision:
- `aios.ps1` is the main orchestration spine.
- Other scripts must be direct modes, helpers, configs, validators, or docs.
- No duplicate startup/workspace/worker authority paths.

Key cleanup commits:
- `66c0c17` Route morning operations through aios spine
- `aee7715` Remove legacy morning boot launcher
- `0c40abf` Remove duplicate build engine lane launchers
- `c62ae5f` Remove legacy standalone worker launcher
- `0decec0` Remove legacy one command launcher
- `39cc555` Remove legacy unmanaged morning launcher
- `0a7b496` Remove obsolete operator day wrapper
- `d546455` Remove obsolete bootstrap display wrappers