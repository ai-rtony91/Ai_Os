# AI_OS Work Packets

Work packets are small JSON files that make assignments persistent without adding services, databases, APIs, or background loops.

Root:

```text
automation/orchestration/work_packets/
```

Folders:

- `active/`
- `blocked/`
- `complete/`
- `templates/`

## Packet Fields

Each packet stays flat and compact:

```json
{
  "packet_id": "",
  "title": "",
  "intent": "",
  "owner_lane": "",
  "assigned_worker": "",
  "repo": "",
  "branch": "",
  "status": "active",
  "priority": "normal",
  "created_utc": "",
  "updated_utc": "",
  "validator": "",
  "next_action": "",
  "blocked_by": [],
  "related_files": [],
  "related_packets": [],
  "notes": []
}
```

## Rules

- Packets are small.
- Packets tie to repos and branches.
- One worker owns one active packet at a time by default.
- Supervisor routing stays preview-first.
- No automation loops.
- No background processes.
- No commits or pushes.
- CONTROL remains root lane.
- ROUTE lane is packet dispatcher.
- WATCH lane is packet state observer.
- Single-writer brainstem rule: only one Codex worker may edit overlapping orchestration/brainstem files at a time. If files under automation/orchestration/bootstrap, automation/orchestration/supervisor, automation/orchestration/operator, automation/orchestration/work_packets, or docs/AI_OS/orchestration overlap, stop extra Codex workers before continuing.

Packet filenames use:

```text
YYYYMMDD-HHMMSS-packet-id.json
```

## Commands

Create one active packet:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\work_packets\New-AiOsWorkPacket.ps1 -Intent "packet intent" -OwnerLane "route_dispatch" -AssignedWorker "codex_worker_1" -Repo "aios-worker-brainstem" -Branch "phase-brainstem-daily-start" -Validator "powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1" -NextAction "Preview routing."
```

Preview routing:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\work_packets\Route-AiOsWorkPacket.DRY_RUN.ps1
```

View packet state:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\work_packets\Get-AiOsWorkPacketState.ps1
```

## Next Safe Action

WHERE: visible tab/window `SAVE · git`

Path: repo root

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\bootstrap\Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1
```
