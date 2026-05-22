# Branch Salvage Decision - 2026-05-22

## Authority
- Active repo path: C:\Dev\Ai.Os
- Active branch: main
- Remote authority: origin/main
- main is authoritative

## Branches Reviewed
- origin/phase-69-operator-loop-tools
- origin/feature/dashboard-readonly-polish

## Decision
- Do not merge either branch wholesale.
- Do not delete either branch yet.
- Preserve both branches temporarily as salvage references only.
- Delete only after the remaining salvage candidates are rejected or captured.

## phase-69 Finding
- 10 unique commits reviewed.
- 1669 diff entries:
  - 16 added
  - 227 modified
  - 272 deleted
  - 1154 renames
- Merge risk: HIGH.
- Delete risk: MEDIUM.
- Salvage value: LOW to MEDIUM.
- Most operator-loop content is already represented in main.
- Remaining candidate: automation/orchestration/work_packets/Sync-AiOsPacketMetadata.APPLY.ps1.
- Decision: requires human review; do not salvage directly; possible future APPLY-script lane only.

## dashboard-polish Finding
- 2 unique commits reviewed.
- 209 diff entries:
  - 3 added
  - 156 modified
  - 50 deleted
- Merge risk: HIGH.
- Delete risk: MEDIUM.
- Salvage value: LOW to MEDIUM.
- Telemetry scaffold and source-state behavior are mostly already represented in main.
- Remaining concept: SourcePill / unsupported-section UI polish.
- Decision: rewrite later from concept only; do not apply stale branch diff.

## Explicit Non-Actions
- No wholesale merge.
- No branch deletion yet.
- No cherry-pick.
- No checkout/switch required.
- No direct APPLY writer introduction.
- No stale dashboard dependency rollback.
- No runtime/startup/worker scripts.

## Future Deletion Gate
Branches may be deleted only after:
- Sync-AiOsPacketMetadata.APPLY.ps1 is rejected or captured as a reviewed future APPLY lane.
- Dashboard SourcePill / unsupported-section concept is rejected or captured as a future UI task.
- Human operator explicitly approves deletion.
- Deletion command is provided only in a separate deletion step after approval.

## Safety Rule Added
Remote branch deletion commands are armed/destructive.

Required sequence:
1. inspect
2. report
3. decide
4. explicit human approval
5. deletion command in a separate step
