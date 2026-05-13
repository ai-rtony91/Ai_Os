# AI_OS Phase 26 Workload Packet Generator Plan

## Phase 26 Foundation Pack Detail

The sections below supersede the earlier summary notes in this file.

## 1. Purpose

Phase 26 plans a local workload packet generator for Work Intelligence.

The future generator converts one Work Intelligence `work_queue` item into ready-to-paste Codex workload packet text.

Generated workload packets are instructions for operator review, not approval.

## 2. Input

Input is one `work_queue` item from Work Intelligence scanner output.

Required queue fields:

- `queue_rank`
- `task_id`
- `title`
- `source`
- `priority`
- `status`
- `recommended_action`
- `suggested_worker_lane`
- `evidence_strength`
- `route_reason`

## 3. Output

Output is plain text that the operator can review and paste into Codex.

The output should not be executed automatically. It should not approve work.

## 4. Queue Item Mapping

Mapping rules:

- `title` becomes the workload title.
- `recommended_action` becomes the objective draft.
- `suggested_worker_lane` becomes worker lane.
- `priority` informs urgency wording.
- `status` informs blocked/review wording.
- `source`, `evidence_strength`, and `route_reason` become evidence notes.
- Missing evidence becomes `UNKNOWN`.

## 5. Packet Sections

Each generated packet must include:

- objective
- worker lane
- allowed files
- blocked files
- planned files if known
- validation commands
- final report format
- safety rules
- commit/push reminder
- UNKNOWN fallback if evidence is weak

## 6. Unknown Fallback Rules

Use `UNKNOWN` when:

- queue evidence is weak
- files are not known
- phase number is not known
- worker lane is not known
- branch name is not known
- validation command is not known

The generator must not invent files, phase numbers, branch names, or approvals.

## 7. Safety Rules

The packet must not:

- approve APPLY automatically
- commit automatically
- push automatically
- use `git add .`
- invent files
- invent phase numbers
- invent branch names
- create live trading behavior
- touch broker, OANDA, API key, secret, or real order paths

## 8. Example Packet

```text
AI_OS WORKLOAD - WI-WORKER-FILE-CONFLICT

Objective:
Resolve worker file ownership conflict.

Worker lane:
Operator Orchestration

Queue evidence:
- queue_rank: UNKNOWN
- task_id: WI-WORKER-FILE-CONFLICT
- priority: HIGH
- status: BLOCKED
- source: UNKNOWN
- evidence_strength: UNKNOWN
- route_reason: UNKNOWN

Allowed files:
UNKNOWN

Blocked files:
- protected root files
- broker/OANDA/API/live execution files
- files outside assigned lane
- files not listed in the approved APPLY prompt

Planned files:
UNKNOWN

Safety rules:
- DRY_RUN first.
- Do not approve APPLY automatically.
- Do not commit automatically.
- Do not push automatically.
- Never use git add .
- Mark missing evidence as UNKNOWN.

Validation commands:
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch

Final report:
Task:
Files inspected:
Files created:
Files changed:
Dry-run/APPLY result:
Validation:
Errors:
Unknowns:
Commit performed: NO
Push performed: NO
Next safe action:
```

## 9. Validation

Future validation should check:

- packet contains required sections
- unknowns are labeled `UNKNOWN`
- no automatic approval language exists
- no `git add .`
- no commit or push approval is implied

## 10. Future Implementation Notes

Future implementation may generate text from local JSON only.

It must remain local-only, evidence-based, and operator-reviewed. It must not run shell commands, launch workers, edit files, stage files, commit, push, merge, or roll back.

## Purpose

This plan defines a future workload packet generator for Work Intelligence. It converts a selected `work_queue` item into a ready-to-paste Codex workload packet.

## Input

Input is one Work Intelligence `work_queue` item.

Expected evidence:

- task ID
- title
- source
- priority
- status
- suggested worker lane
- recommended action
- route reason

If evidence is weak or missing, the generator must use `UNKNOWN`.

## Output Packet

The generated packet should include:

- objective
- allowed files
- blocked files
- validation commands
- final report format
- commit/push reminder

## Behavior

The generator is planning-only in this phase.

It must not:

- run APPLY
- create branches
- launch workers
- stage files
- commit
- push
- merge
- rollback

## Example Packet Shape

```text
AI_OS WORKLOAD — <title>

Objective:
<objective or UNKNOWN>

Allowed files:
<paths or UNKNOWN>

Blocked files:
protected root files
broker/OANDA/API/live execution files
files outside assigned lane

Validation:
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
git diff --check
git status --short --branch

Final report:
Files changed:
Validation:
Errors:
Unknowns:
Commit performed: NO
Push performed: NO
Next safe action:
```

## Safety

Generated packets are operator prompts only. They do not approve APPLY, commit, push, merge, rollback, broker integration, API key use, or live execution.
