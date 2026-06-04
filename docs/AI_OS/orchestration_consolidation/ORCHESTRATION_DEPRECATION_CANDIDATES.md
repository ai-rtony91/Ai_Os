# Orchestration Deprecation Candidates

This list is a planning map only. It does not approve deprecation, moves, deletes, or edits.

| Path | Reason | Risk | Replacement/canonical path | Safe action |
|---|---|---:|---|---|
| `automation/orchestration/approval_inbox.v1.example.json` | Root approval example overlaps active approval inbox folder. | Medium | `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` | Mark deprecated later after reference scan. |
| `automation/orchestration/packet_queue_ledger.v1.example.json` | Root packet queue ledger overlaps `work_packets/` and queue folders. | High | `automation/orchestration/work_packets/` | Review manually before marking. |
| `automation/orchestration/worker_registry.v1.example.json` | Root worker registry overlaps `workers/AIOS_WORKER_REGISTRY.json`. | High | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | Review manually before marking. |
| `automation/orchestration/validator_routing_supervisor.v1.example.json` | Root validator routing snapshot overlaps validators and validator chain runner. | Medium | `automation/orchestration/validators/`, `automation/orchestration/validator_chain_runner/` | Mark deprecated later if no reader. |
| `automation/orchestration/session_continuity.v1.example.json` | Root continuity example overlaps session and terminal workstation state. | Medium | `automation/orchestration/session/`, `automation/orchestration/terminal_workstations/` | Keep until resume workflows are mapped. |
| `automation/orchestration/orchestration_spine_v1.example.json` | Old spine example can conflict with canonical authority docs. | Medium | `docs/AI_OS/orchestration_consolidation/ORCHESTRATION_CANONICAL_AUTHORITY_MAP.md` | Mark deprecated later. |
| `automation/orchestration/orchestration_control_state.v1.example.json` | Root control-state example overlaps control and runtime state bundle helpers. | High | `automation/orchestration/control/`, `automation/orchestration/runtime/` | Review manually; unsafe to delete now. |
| `automation/orchestration/persistent_worker_supervisor.v1.example.json` | Root supervisor example overlaps supervisor and runtime loops. | High | `automation/orchestration/supervisor/`, `automation/orchestration/runtime/` | Keep until runtime gates stabilize. |
| `automation/orchestration/launch_supervisor.v1.example.json` | Launch supervisor example can be mistaken for runtime launch authority. | High | `docs/AI_OS/night_supervisor/`, `automation/orchestration/night_supervisor/` | Mark warning later, no delete. |
| `automation/orchestration/show-*.ps1` | Root display helpers overlap subfolder tools and canonical status paths. | Low/Medium | Subfolder-specific `Get-*` and `Show-*` tools | Move/archive later only after user-facing shortcuts are checked. |
| `automation/orchestration/relay/` | Relay runner/worker may overlap worker packet and command runner paths. | Medium | `work_packets/`, `workers/`, `command_runner/` | Review manually. |
| `automation/orchestration/auto_loop/` | Auto-loop packet/validator/commit templates overlap newer protected route and PR lane doctrine. | High | Dispatch hardening + PR lane + protected action gate | Unsafe to touch until autonomy gates pass. |
| `automation/orchestration/runtime/` | Runtime/self-route/persistent supervisor scripts overlap Night Supervisor and autonomy runway. | Critical | Future runtime authority map | Do not touch until controlled-run gates pass. |
| `automation/orchestration/night_supervisor/` | Active preview/runtime candidate path. | Critical | `docs/AI_OS/night_supervisor/` plus future controlled-run packet | Do not touch in consolidation cleanup. |
| `automation/orchestration/approval_inbox/archive/` | Archive examples may overlap live approval evidence. | Medium | Approval retention policy | Keep until retention policy exists. |

## Unsafe To Touch Until Stable

- `automation/orchestration/night_supervisor/`
- `automation/orchestration/runtime/`
- `automation/orchestration/locks/`
- `automation/orchestration/memory/`
- `automation/orchestration/approval_inbox/`
- any Paper SOS runtime worktree or runtime script

