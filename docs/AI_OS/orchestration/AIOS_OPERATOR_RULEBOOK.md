# AI_OS Operator Rulebook

This rulebook preserves operator preferences and workflow rules across AI_OS sessions.

## Command Guidance

- Always say WHERE before commands.
- Always name the visible tab/window first.
- Always include the path before commands.
- Codex worker vs Git/PowerShell save tab must be distinct.
- Never assume the operator remembers lane names.
- Use simple wording when debugging.
- Prefer fixing scripts over explaining the same issue repeatedly.

## Copy Markers

Use these markers around text the operator should copy:

```text
COPY START
...
COPY END
```

## Lane Identity Rules

- CONTROL is permanent root.
- CONTROL is not a normal worker lane.
- CONTROL remains fixed root.
- Do not rename CONTROL dynamically.
- Worker lanes are temporary and restorable.
- Manual window or tab renaming is temporary only.
- Do not rely on manual tab or window renaming; it does not reliably stick.
- Repo scripts, registry files, and checkpoints must own persistent titles.
- Path + branch are the truth source.

## Launch And Save Rules

- No Codex auto-launch.
- Preview before launch.
- No commits/pushes without explicit command.
- No scheduled/startup tasks.
- No broker/API/live trading.

## Rulebook Lane Identity

```text
lane_id: rulebook_codex
display_title: RULEBOOK · codex
window_title: RULEBOOK · codex
tab_title: RULEBOOK · codex
role: Operator rules, workflow memory, and durable instruction capture.
path: C:\Users\mylab\OneDrive\GitHub\aios-worker-rulebook
branch: phase-operator-rulebook
truth_source: path_and_branch
```

## Next Safe Action

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1
```
