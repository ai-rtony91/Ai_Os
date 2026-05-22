# AI_OS Worker Window Layout

Use this launcher tomorrow from `AI_OS MAIN CONTROL` to open the worker terminal set without rebuilding the layout.

The launcher is DRY_RUN by default. It prints the Windows Terminal commands first. It launches windows only when `-Apply` is present.

## Tomorrow Launch Command

From the repo root:

```powershell
cd C:\Dev\Ai.Os
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset compact -Apply
```

## Preview First

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset compact
```

## Presets

| Preset | Behavior | Use |
| --- | --- | --- |
| compact | One Windows Terminal window with all worker tabs. | Safe default for one screen. |
| wide | One wider Windows Terminal window with all worker tabs. | Use on a large monitor. |
| dual-monitor | Two Windows Terminal windows split by role group. | Use when a second monitor is available. |

## Worker Titles

Each spawned worker changes into:

```text
C:\Dev\Ai.Os
```

Each worker runs:

```powershell
automation/window_identity/Set-AiOsWindowIdentity.ps1
```

with one matching marker:

| Title | Marker |
| --- | --- |
| 🧭 AI_OS MAIN CONTROL | `AI_OS MAIN CONTROL` |
| 🛠 CODEX BUILD LANE | `CODEX BUILD LANE` |
| ✅ VALIDATOR WORKER | `VALIDATOR WORKER` |
| 📦 PACKET QUEUE | `PACKET QUEUE` |
| 📥 APPROVAL INBOX | `APPROVAL INBOX` |
| 🩺 RECOVERY HEALTH | `RECOVERY HEALTH` |
| ⏸ STANDBY WORKER | `STANDBY WORKER` |

## Safety Boundaries

- Uses `wt.exe` only.
- No startup tasks.
- No scheduled tasks.
- No external apps except Windows Terminal.
- No dashboard edits.
- No Trading Lab edits.
- No protected root governance file edits.
- No `git add .`.
- No commit.
- No push.

## Exact Commands

Preview compact:

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset compact
```

Launch compact:

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset compact -Apply
```

Preview wide:

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset wide
```

Launch wide:

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset wide -Apply
```

Preview dual-monitor:

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset dual-monitor
```

Launch dual-monitor:

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Open-AiOsWorkerWindowLayout.ps1 -Preset dual-monitor -Apply
```
