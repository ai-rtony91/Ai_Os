# AI_OS Worker to Subsystem Map

This map connects visible worker windows to the backend repo subsystems they help operate.

Visible worker windows are operator lanes. They are labels for Anthony and Codex to keep terminal work clear. They are not folder names, ownership claims, or a reason to move files.

Repo folders are backend subsystems. Their paths are part of the runtime spine and should stay stable until there is evidence that consolidation is needed.

Do not restructure yet. Use this mapping first. Consolidation can happen later only after repeated evidence shows that a path is confusing, unused, duplicated, or blocking runtime work.

This reduces errors without breaking paths because the terminal title tells the operator what kind of work belongs in the window, while the map points to the existing subsystem folders that should be checked. The repo keeps its current paths, existing scripts keep working, and worker lanes can become clearer without folder moves, renames, or risky cleanup.

## Worker Map

| Visible worker window | Runtime role | Repo subsystem paths |
| --- | --- | --- |
| AI_OS MAIN CONTROL | Primary operator lane for runtime and supervisor control. | `automation/orchestration/runtime`, `automation/orchestration/supervisor`, `automation/orchestration/mission_control`, `automation/runtime/state` |
| CODEX BUILD LANE | Temporary implementation lane for approved scoped edits. | Approved scoped repo edits only; no permanent subsystem ownership. |
| VALIDATOR WORKER | Validation lane for health checks, blockers, and pass/fail evidence. | `automation/orchestration/validators`, `automation/orchestration/health`, `automation/orchestration/blockers` |
| PACKET QUEUE | Queue lane for work packet review, task flow, and command queue visibility. | `automation/orchestration/queue`, `automation/orchestration/work_packets`, `automation/orchestration/task_generator`, `automation/orchestration/command_queue` |
| APPROVAL INBOX | Approval lane for user-controlled gates and approval processing. | `automation/orchestration/approvals`, `automation/orchestration/approval_inbox`, `automation/orchestration/approval_processor`, `automation/orchestration/approval_detection` |
| RECOVERY HEALTH | Recovery lane for self-heal, health review, and failed-state inspection. | `automation/orchestration/recovery`, `automation/orchestration/self_heal`, `automation/orchestration/health` |
| STANDBY WORKER | Idle lane waiting for assignment. | No active subsystem; can become validator, packet queue, or recovery lane later. |

## Operating Rules

- Do not move folders.
- Do not rename folders.
- Do not edit launchers from this map.
- Do not edit dashboard files.
- Do not edit Trading Lab files.
- Do not touch protected root governance files.
- Do not use this map as approval for broad cleanup.
- Use the mapping first; consolidate later only after evidence.

## Next Command Hints

| Visible worker window | Next command hint |
| --- | --- |
| AI_OS MAIN CONTROL | `.\aios.ps1 -Mode runtime` |
| CODEX BUILD LANE | `git status --short --branch` |
| VALIDATOR WORKER | `git diff --check` |
| PACKET QUEUE | `Get-ChildItem automation\orchestration\work_packets` |
| APPROVAL INBOX | `git status --short --branch` |
| RECOVERY HEALTH | `git status --short --branch` |
| STANDBY WORKER | `git status --short --branch` |
