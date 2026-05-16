# AI_OS Window Identity Markers

Use these markers to make each AI_OS terminal or worker window obvious before running commands.

The marker script only changes the current terminal title and prints a banner. It does not create startup tasks, scheduled tasks, external apps, broker connections, API keys, secrets, trades, telemetry, or repo state.

## Paste in AI_OS MAIN CONTROL

From the repo root:

```powershell
cd C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "AI_OS MAIN CONTROL"
```

After the banner appears, use this terminal for the runtime spine:

```powershell
.\aios.ps1 -Mode runtime
```

Supervisor mode stays explicit:

```powershell
.\aios.ps1 -Mode supervisor
```

## Available Markers

| Marker | Color | Emoji | Role | Next command hint |
| --- | --- | --- | --- | --- |
| AI_OS MAIN CONTROL | Cyan | 🧭 | Primary operator terminal for runtime spine commands and final coordination. | `.\aios.ps1 -Mode runtime` |
| CODEX BUILD LANE | Yellow | 🛠️ | Focused build window for approved repo-scoped implementation work. | `git status --short --branch` |
| VALIDATOR WORKER | Green | ✅ | Validation-only window for checks, parser tests, and read-only verification. | `git diff --check` |
| PACKET QUEUE | Magenta | 📦 | Queue review window for workload packets, command packs, and next safe tasks. | `Get-ChildItem automation\packets` |
| APPROVAL INBOX | Blue | 📥 | Decision window for approvals, stop conditions, and user-controlled checkpoints. | `git status --short --branch` |
| RECOVERY HEALTH | Red | 🩺 | Recovery and health-check window for failures, mismatches, and blocked states. | `git status --short --branch` |
| STANDBY WORKER | DarkGray | ⏸️ | Idle worker window reserved for approved next tasks only. | `git status --short --branch` |

## Copy-Paste Commands

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "AI_OS MAIN CONTROL"
```

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "CODEX BUILD LANE"
```

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "VALIDATOR WORKER"
```

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "PACKET QUEUE"
```

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "APPROVAL INBOX"
```

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "RECOVERY HEALTH"
```

```powershell
powershell -ExecutionPolicy Bypass -File automation/window_identity/Set-AiOsWindowIdentity.ps1 -Marker "STANDBY WORKER"
```

## Safety Boundaries

- Repo-scoped only.
- No live trading.
- No broker connection.
- No OANDA integration.
- No API keys or secrets.
- No startup tasks or scheduled tasks.
- No destructive cleanup.
- No dashboard file changes.
- No Trading Lab file changes.
- No protected root governance file changes.
- No `git add .`.
