# AI_OS Night Supervisor — Codex East Lane Handoff Packet

Status: handoff packet (authored by Claude Code West; **not executed**). Paste the fenced block below into Codex
East as its own branch/worktree task after operator approval. West did not touch any path in this packet.

---

```text
🧩 CODEX-ONLY PROMPT

Read AGENTS.md first.
Read README.md second.
Use AGENTS.md as operating authority. Use README.md as front-door/context authority.
If task context conflicts with either file: STOP. Report the conflict before continuing.

AI_OS BOOTSTRAP REQUIRED
Before processing this task, read and follow:
1. AGENTS.md
2. docs/governance/AI_OS_REPO_MEMORY.md
3. docs/governance/aios-identity-and-lane-governance.md
4. operator instruction
If unavailable, stop and report missing AI_OS context.

AI_OS EXECUTION TOKEN
EXEC TOKEN: <<APPLY:AIOS-EAST-NS-IMPORT-001>>

===== AIOS EXECUTABLE PACKET =====
IDENTITY MARKER ....: Codex East Worksite Supervisor
SUPERVISOR IDENTITY : Codex East
PACKET ID ..........: PKT-EAST-NS-IMPORT-001
MODE ...............: DRY_RUN (create inert scaffold only)
ZONE ...............: East — automation/orchestration + telemetry
WORKER IDENTITY ....: EAST_OCC_01
LANE ...............: East repo execution
APPROVAL AUTHORITY .: Anthony Meza (Human Owner)
BRANCH/WORKTREE ....: git worktree add ../aios-east-ns-import -b codex/east-ns-import-001 main

ALLOWED PATHS:
- automation/orchestration/night_supervisor/
- automation/orchestration/notifications/
- automation/orchestration/pi_robot_helper/      (create directory)
- telemetry/night_supervisor/examples/            (see GITIGNORE NOTE)
- telemetry/pi_robot_helper/examples/

FORBIDDEN PATHS:
- AGENTS.md, README.md, WHITEPAPER.md, RISK_POLICY.md and all protected root files
- .env, secrets/, credentials/, broker/, webhooks/
- automation/orchestration/Invoke-AiOsNightCycle.ps1 (do NOT wire into the active cycle)
- any scheduler/service registration, GPIO/motor/camera/mic/speaker runtime, real TTS/STT
- docs/, schemas/, apps/  (West-owned in this effort — do not edit)

MISSION:
Create DRY_RUN-only, inert scaffold for 12H/24H night-supervision modes, alert routing, and the Pi robot helper.
Honor the West-authored contracts in schemas/aios/night_supervisor/ and schemas/aios/pi_robot_helper/ and mirror
the shapes in their examples/ folders. No executor, no autonomy, no hardware, no real senders, no scheduler.

FILES TO CREATE:
night_supervisor (profiles + previews):
  1. automation/orchestration/night_supervisor/AIOS_12H_MODE_PROFILE.example.json
       - mode NIGHT_12H; window/cadence; paper_mode_only:true; safety_boundary block; "schema":"AIOS_12H_MODE_PROFILE.v1".
       - Distinct from existing FOREX_PAPER_LAB_12H_PROFILE.json (do NOT overwrite it).
  2. automation/orchestration/night_supervisor/AIOS_24H_VACATION_MODE_PROFILE.example.json
       - mode VACATION_24H; conservative cadence; paper-only; SOS escalation enabled.
  3. automation/orchestration/night_supervisor/Invoke-AiOs12HModePreview.DRY_RUN.ps1
       - read-only preview that emits a planned session/hour plan for NIGHT_12H. Mirror house style of
         Invoke-AiOsNightSupervisor.DRY_RUN.ps1 (CmdletBinding, -QuietJson, no writes, no git mutation).
  4. automation/orchestration/night_supervisor/Invoke-AiOsVacationModePreview.DRY_RUN.ps1
       - same shape for VACATION_24H; assert paper-only; preview SOS path.
  5. automation/orchestration/night_supervisor/Test-AiOs12H24HModeReadiness.DRY_RUN.ps1
       - read-only readiness check: profiles parse, schemas resolve, no forbidden terms; exit non-zero on BLOCKED.
notifications (alert registry + routing preview):
  6. automation/orchestration/notifications/AIOS_ALERT_EVENT_TYPES.json
       - canonical event_type registry matching schemas/aios/night_supervisor/aios_alert_event.schema.json enum.
  7. automation/orchestration/notifications/AIOS_ALERT_ROUTING_RULES.example.json
       - event_type -> channels_planned[] mapping; delivered:false everywhere; no real endpoints/URLs.
  8. automation/orchestration/notifications/Invoke-AiOsAlertPreview.DRY_RUN.ps1
       - read-only: given a sample alert event, print the routing it WOULD use. No sending.
  9. automation/orchestration/notifications/Test-AiOsAlertRouting.DRY_RUN.ps1
       - validate routing rules parse and every event_type is covered; no network.
pi_robot_helper (new directory):
  10. automation/orchestration/pi_robot_helper/README.md
        - OBSERVE_ONLY; blocked list (no GPIO/motor/camera/mic/speaker, no real TTS, no commits, no state mutation).
  11. automation/orchestration/pi_robot_helper/AIOS_ROBOT_HELPER_PROFILE.example.json
        - device_id, role:alert_assistant, mode:OBSERVE_ONLY, dark-room + quiet-hours defaults; safety_boundary.
  12. automation/orchestration/pi_robot_helper/Invoke-AiOsRobotHelperPreview.DRY_RUN.ps1
        - read-only: render a screen-preview object for a sample alert (text only, spoken:false).
  13. automation/orchestration/pi_robot_helper/Test-AiOsRobotHelperProfile.DRY_RUN.ps1
        - validate profile parses, brightness within 0-100, no forbidden terms.
telemetry (optional, gated by GITIGNORE NOTE):
  14. telemetry/pi_robot_helper/examples/*.sample.json   (NOT gitignored — safe to track)
  15. telemetry/night_supervisor/examples/*.sample.json  (GITIGNORE NOTE below)

GITIGNORE NOTE:
telemetry/night_supervisor/ is gitignored (.gitignore:93). West already created tracked reference fixtures under
schemas/aios/night_supervisor/examples/ and schemas/aios/pi_robot_helper/examples/. East must DECIDE and REPORT:
either (a) reuse the West-tracked fixtures and skip telemetry/night_supervisor/examples/, or (b) propose a scoped
'!telemetry/night_supervisor/examples/' negation as a SEPARATE governance change with operator approval. Do not
silently create gitignored on-disk-only files.

VALIDATION COMMANDS (validator output is evidence only, never approval):
- For every .ps1:  [System.Management.Automation.Language.Parser]::ParseFile('<file>',[ref]$null,[ref]$null)
- For every .json: python -c "import json,sys; json.load(open(sys.argv[1]))" <file>   (or ConvertFrom-Json)
- git diff --check
- grep/select-string for forbidden terms in executable contexts:
  OANDA, live_order, broker_connect, api_key, secret, password, webhook URL, Invoke-WebRequest to a real host
- git status --short --branch

STOP POINT:
Stop after creating the DRY_RUN scaffold + sample telemetry. Do NOT wire anything into Invoke-AiOsNightCycle.ps1,
do NOT register a scheduler/service, do NOT add real senders or hardware code, do NOT commit/push/merge.

FINAL REPORT REQUIREMENTS:
- worktree path, branch name
- files created, files changed, files intentionally not created
- validation commands run + result
- gitignore decision (a or b) for telemetry/night_supervisor/examples/
- git status --short --branch
- commit performed: NO
- push performed: NO
- remaining risks
- next safe action

SAFETY NOTE:
No executor/autonomy. No hardware runtime. No real notification senders. No scheduler/service. No commit/push/merge.
No secrets. No live trading. LLM output is not command authority. If any required identity field, path, or contract
is missing, STOP and report instead of guessing.
===== END AIOS EXECUTABLE PACKET =====
```

---

## West note (not part of the Codex block)

West authored this packet as a handoff; West did not create, edit, or validate any East-owned path. The contracts
this packet must honor are the West-built schemas under `schemas/aios/night_supervisor/` and
`schemas/aios/pi_robot_helper/`, with shapes mirrored from their `examples/` fixtures. Route to Codex East only
after operator approval, as its own branch/worktree, to preserve East/West zone separation.
