# Orchestration C2 Deprecation Header Plan 001

## Purpose

C2 defines where future deprecation headers may be applied to obvious legacy or prototype orchestration documentation. This is a planning artifact only. It does not edit legacy files, move files, delete files, rename files, rewrite references, or modify runtime automation.

## Definition: Obvious Legacy Or Prototype Doc

An obvious legacy or prototype doc is a documentation or example artifact that:

- is labeled `example`, `v1`, `legacy`, `prototype`, `draft`, `snapshot`, or compatibility evidence.
- overlaps a canonical authority already marked in C1.
- is not active runtime state, approval state, lock state, memory state, Night Supervisor runtime, Paper SOS runtime, or broker/trading/Pi control.
- can be marked as historical reference without changing behavior.

JSON state files, PowerShell scripts, Python runners, approval inbox records, lock records, memory records, and runtime configs are not safe C2 targets unless a later packet separately proves they are docs-only compatibility examples.

## Deprecation Header Text Template

Use the template in:

`docs/AI_OS/orchestration_consolidation/ORCHESTRATION_C2_DEPRECATION_HEADER_TEMPLATE.md`

The header must be added only by a later human-approved APPLY packet.

## Candidate Groups

### Safe To Mark Later

These are docs-only or example-oriented items that appear safest to mark later after a focused reference scan:

| Candidate | Reason | Required pre-APPLY check |
|---|---|---|
| `automation/orchestration/orchestration_spine_v1.example.json` | Old spine example overlaps C1 canonical authority decision. | Confirm no script treats it as active state. |
| `automation/orchestration/orchestration_gap_ledger.example.json` | Gap ledger example overlaps consolidation audit findings. | Confirm it is not consumed by a status script. |
| `automation/orchestration/orchestration_status_snapshot.example.json` | Snapshot-shaped example overlaps current status sources. | Confirm root show/status scripts do not require it. |
| `automation/orchestration/README_FOLDER_PURPOSE.txt` | Folder-purpose note may be superseded by `README.md` and C1 authority docs. | Confirm it is not a launcher/help target. |
| `automation/orchestration/adapters/LEGACY_PACKET_MAPPING.example.json` | Explicit legacy packet mapping example. | Confirm adapter tests use it as fixture only. |

### Needs Reference Update First

These candidates may be legacy but are likely referenced by scripts or docs:

| Candidate | Reason | Reference work needed |
|---|---|---|
| `automation/orchestration/approval_inbox.v1.example.json` | Root approval example overlaps active approval inbox. | Update references to `approval_inbox/APPROVAL_INBOX_001.json` or mark as compatibility evidence. |
| `automation/orchestration/packet_queue_ledger.v1.example.json` | Root packet queue ledger overlaps `work_packets/` and queue folders. | Resolve canonical packet queue path before marking. |
| `automation/orchestration/worker_registry.v1.example.json` | Root worker registry overlaps active worker registry. | Update readers to `workers/AIOS_WORKER_REGISTRY.json`. |
| `automation/orchestration/validator_routing_supervisor.v1.example.json` | Root validator routing snapshot overlaps validator chain authority. | Resolve validator router canonical path and update references. |
| `automation/orchestration/session_continuity.v1.example.json` | Continuity example overlaps session and terminal workstation state. | Confirm resume/session workflows before marking. |
| root `automation/orchestration/show-*.ps1` docs or help text | Root display helpers overlap subfolder tools. | Map user-facing shortcuts and terminal launchers first. |

### Unsafe To Touch

Do not add deprecation headers or edit these paths in C2:

- `automation/orchestration/night_supervisor/`
- `automation/orchestration/runtime/`
- `automation/orchestration/locks/`
- `automation/orchestration/memory/`
- `automation/orchestration/approval_inbox/`
- `automation/orchestration/approval_inbox/archive/`
- Paper SOS runtime worktree or scripts
- telemetry/control runtime state
- broker/OANDA/live trading paths
- Pi GPIO/motor paths

### Unknown Or Manual Review

These areas require manual reference and ownership review:

- `automation/orchestration/relay/`
- `automation/orchestration/auto_loop/`
- `automation/orchestration/supervisor/`
- `automation/orchestration/control/`
- `automation/orchestration/openai_api_bridge/`
- `.github` workflow references to orchestration scripts
- nontracked local shortcuts or launcher scripts on the operator machine

## No-Move And No-Delete Warning

C2 does not approve moving, deleting, renaming, archiving, or editing any file outside `docs/AI_OS/orchestration_consolidation/`.

No file is deleted or moved until:

1. references are mapped.
2. replacement authority is named.
3. validator confirms no active runtime dependency.
4. Human Owner approves APPLY.

## Exact Next APPLY Packet Recommendation

Recommended next packet: C3 reference update planning.

C3 should create a reference-update plan before any deprecation headers are applied outside consolidation docs. It should map readers for the safe-to-mark candidates, identify exact references that need updates, and stop before editing legacy files.

