# ChatGPT To Orchestration Adapter Mapping

Packet: CHATGPT_TO_ORCHESTRATION_ADAPTER_MAPPING_001
Mode: APPLY report output
Lane: CHATGPT_ADAPTER_MAPPING
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os

## Purpose

Define exactly how a ChatGPT-generated packet becomes a canonical orchestration packet preview before it can enter the AI_OS Orchestration Harness.

This is a mapping contract only. It creates no adapter code, scripts, schemas, queues, approvals, automation, source changes, protected-file edits, broker paths, live trading paths, secrets, commits, or pushes.

## Source Authority Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md`
- `Reports/bridge_audit/CANONICAL_HARNESS_SELECTION.md`
- `Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md`
- `Reports/bridge_audit/FIRST_ADAPTER_SELECTION.md`
- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`

## Governing Boundary

The ChatGPT adapter is an intake adapter only.

It validates ChatGPT-generated packet text, classifies risk, builds a canonical envelope preview, and builds a canonical work packet preview. It must default to `executable=false`.

It must not:

- execute Codex.
- write to `automation/orchestration/work_packets/`.
- write to `automation/orchestration/approval_inbox/`.
- create queue files.
- create approvals.
- create adapter code.
- create scripts.
- call OpenAI APIs.
- call MCP tools.
- invoke provider CLIs.
- stage, commit, push, merge, or create PRs.
- touch live trading, broker/API, credential, or secret paths.

## 1. Packet Input Fields

The adapter accepts one raw ChatGPT-generated packet text block and optional current-state evidence collected outside the raw packet.

Required raw packet markers:

| Field | Required | Rule |
|---|---:|---|
| `CODEX-ONLY PROMPT` | yes | Must be the first line exactly for Codex-pasteable packets. |
| `AI_OS EXECUTION TOKEN` | yes | Required for any packet intended to become executable. |
| `AI_OS BOOTSTRAP REQUIRED` | yes | Required for AI_OS-governed work. |

Required packet metadata:

| Field | Required | Rule |
|---|---:|---|
| identity marker | yes | Must identify the artifact as an AI_OS executable packet or assigned worker packet. |
| supervisor identity | yes | Must identify owner/supervisor. |
| packet ID | yes | Must be stable, specific, and non-placeholder. |
| lane | yes | Must be named. |
| zone | yes | Must be named. |
| worker identity | yes | Must be named. |
| mode | yes | Must be `DRY_RUN` or `APPLY`. |
| branch | yes | Must be observed or explicitly resolved after preflight. |
| worktree | yes | Must be `C:\Dev\Ai.Os` unless explicitly approved otherwise. |
| approval authority | yes | Must name Anthony / AI_OS Owner or approved Human Owner authority. |
| allowed paths | yes | Must be exact paths, not placeholders. |
| forbidden paths | yes | Must be exact paths or protected path classes. |
| validator chain | yes | Must name read-first files and validation commands. |
| mission | yes | Must state one scoped mission. |
| preflight | yes | Must include or require path, branch, status, and remote checks when repo state matters. |
| stop point | yes | Must state where execution stops. |
| final report format | yes | Must name the required final response fields. |

Optional but recommended fields:

- read-first authority files.
- protected paths.
- strict rules.
- non-actions.
- expected output file.
- approval gate notes.
- validation evidence paths.
- safe next command.

## 2. Required Identity Fields

The adapter must map packet identity into a canonical identity block:

| Canonical Field | Source Field | Required Decision |
|---|---|---|
| `identity_marker` | `IDENTITY MARKER` | Fail if missing. |
| `supervisor_identity` | `SUPERVISOR IDENTITY` | Fail if missing. |
| `packet_id` | `PACKET ID` | Fail if missing, duplicate-looking, or placeholder. |
| `zone` | `ZONE` | Fail if missing. |
| `worker_identity` | `WORKER IDENTITY` | Fail if missing. |
| `lane` | `LANE` | Fail if missing. |
| `mode` | `MODE` | Fail unless `DRY_RUN` or `APPLY`. |
| `branch` | `BRANCH` | Validate against observed branch or require explicit resolve-after-preflight state. |
| `worktree` | `WORKTREE` | Fail if not active repo path unless explicitly approved. |
| `approval_authority` | `APPROVAL AUTHORITY` | Fail if missing. |
| `stop_point` | `STOP POINT` | Fail if missing. |

Identity mapping must not invent missing fields. Missing required identity produces a validation failure before any queue preview is considered acceptable.

## 3. Required Validation Fields

The adapter must verify the packet contains these validation controls:

| Validation Field | Required Check |
|---|---|
| `read_first_authority_files` | Must include `AGENTS.md` and `README.md`; include `WHITEPAPER.md` when repo identity/trading boundary/protected pointer matters. |
| `allowed_paths` | Must be exact, bounded, and compatible with the mission. |
| `forbidden_paths` | Must include protected authority and source paths when outside scope. |
| `validator_chain` | Must include read-first steps, state confirmation, task output validation, `git diff --check` after file changes, and final `git status --short --branch`. |
| `preflight` | Must check path, status, branch, and remote before branch-sensitive work. |
| `final_report_format` | Must match AI_OS completion, failure, or DRY_RUN report rules. |
| `stop_condition` | Must state no further action after the scoped output and validation. |
| `non_action_boundary` | Must block commit, push, merge, live trading, broker/API, secrets, and automation creation unless explicitly approved. |

## 4. Failure Classes

The adapter must classify failures before producing the canonical envelope preview.

| Failure Class | Trigger | Required Status |
|---|---|---|
| `MISSING_ROUTING_MARKER` | First line is not `CODEX-ONLY PROMPT` for a Codex-pasteable packet. | `BLOCKED` |
| `MISSING_EXECUTION_TOKEN` | Executable intent lacks `AI_OS EXECUTION TOKEN`. | `BLOCKED` |
| `MISSING_BOOTSTRAP` | Missing `AI_OS BOOTSTRAP REQUIRED`. | `BLOCKED` |
| `MISSING_IDENTITY_FIELD` | Any required identity field is missing. | `BLOCKED` |
| `MISSING_VALIDATION_FIELD` | Validator chain, preflight, final report, allowed paths, forbidden paths, or stop point is missing. | `BLOCKED` |
| `PLACEHOLDER_PRESENT` | Contains `@filename`, `path/to/file`, `[REAL-FILENAME]`, `{feature}`, `TODO`, `TBD`, or similar unresolved placeholder. | `BLOCKED` |
| `FORBIDDEN_PATH_TARGETED` | Packet asks to edit forbidden/protected paths outside approval scope. | `BLOCKED` or `HUMAN_APPROVAL_REQUIRED` |
| `DUPLICATE_AUTHORITY_RISK` | Packet creates duplicate governance, queue, approval, or bridge authority. | `BLOCKED` |
| `STATE_MISMATCH` | Assumed branch/worktree conflicts with observed state. | `BLOCKED` with `AIOS-PROMPT-AUTH-STATE-MISMATCH` label |
| `DIRTY_STATE_UNCLASSIFIED` | Dirty files exist and overlap mission or cannot be safely classified. | `BLOCKED` |
| `APPROVAL_MISSING` | Protected or high-risk action lacks Anthony approval. | `NEEDS_APPROVAL` or `BLOCKED` |
| `PROTECTED_ACTION_UNSCOPED` | Stage, commit, push, merge, reset, clean, branch delete, PR action, protected file edit, secret, broker/API, or live trading action lacks exact scope. | `BLOCKED` |
| `SECRET_OR_CREDENTIAL_RISK` | Packet requests secrets, credentials, API keys, or external transmission of private evidence without approval. | `BLOCKED` |
| `BROKER_OR_LIVE_TRADING_RISK` | Packet touches live broker/API, real order, real webhook, or live execution paths. | `BLOCKED` |
| `UNAUTHORIZED_AUTOMATION` | Packet creates schedulers, daemon behavior, queue runners, or autonomous loops without explicit approval. | `BLOCKED` |

## 5. Canonical Envelope Schema

This is a preview schema, not a created JSON schema file.

Every valid adapter output should be representable as:

```text
schema: AIOS_CHATGPT_TO_ORCHESTRATION_ENVELOPE.v1
event_id: unique adapter event id
created_at_utc: ISO-8601 timestamp
source_party: ChatGPT
adapter_name: ChatGptToOrchestrationAdapter
source_input_type: CHATGPT_PACKET_TEXT
source_hash: hash or stable fingerprint when available
packet_id: packet id from source packet
lane: lane from source packet
zone: zone from source packet
mode: DRY_RUN or APPLY
identity_marker: source identity marker
supervisor_identity: source supervisor identity
worker_identity: source worker identity
approval_authority: source approval authority
repo_root: C:\Dev\Ai.Os
worktree: packet worktree
branch_declared: packet branch
branch_observed: observed branch
git_status_short_branch: observed git status
dirty_state_class: CLEAN, REPORT_ONLY_UNTRACKED, DIRTY_TRACKED, DIRTY_UNTRACKED_UNSAFE, or UNKNOWN
allowed_paths: exact packet allowed paths
forbidden_paths: exact packet forbidden paths
read_first_authority_files: files required before action
validator_chain: packet validator chain
mission: packet mission
stop_point: packet stop point
final_report_format: required final fields
status: READY, PREVIEW, NEEDS_APPROVAL, BLOCKED, or FAILED
status_impact: CURRENT_ACTIVE, CURRENT_DETAIL_ONLY, HISTORICAL_DETAIL_ONLY, or NO_STATUS_IMPACT
blocked_reasons: list
risk_flags: list
missing_fields: list
placeholder_findings: list
branch_worktree_validation: PASS, FAIL, or UNKNOWN
approval_required: true or false
approval_status: NOT_REQUIRED, REQUIRED, PENDING, APPROVED, REJECTED, MALFORMED, MISMATCHED, or UNKNOWN
protected_action_requested: true or false
protected_action_type: protected action type or empty
redaction_status: NO_SECRETS_DETECTED, REDACTED, SECRET_RISK_BLOCKED, NOT_SCANNED, or UNKNOWN
paper_only: true or false when Trading Lab is in scope
executable: false by default
canonical_work_packet_preview: embedded preview object or empty when blocked
evidence_output: embedded evidence object
display_alert: true or false
sos_wake_required: true or false
wake_class: NONE, DISPLAY_ONLY, REVIEW_ONLY, or SOS
next_safe_action: one exact next safe action
```

Envelope rule:

```text
No envelope preview may set executable=true unless a future separately approved implementation defines and validates that transition.
```

## 6. Canonical Work Packet Preview Schema

This is a preview shape only. The mapping report does not write work packet files.

```text
work_packet_preview:
  schema: AIOS_CANONICAL_WORK_PACKET_PREVIEW.v1
  packet_id: source packet id
  origin: CHATGPT_GENERATED_PACKET
  adapter_name: ChatGptToOrchestrationAdapter
  canonical_harness_owner: AI_OS Orchestration Harness
  queue_owner: automation/orchestration/work_packets/
  approval_owner: automation/orchestration/approval_inbox/
  worker_owner: automation/orchestration/workers/
  validator_owner: automation/orchestration/validators/
  commit_package_owner: automation/orchestration/commit_packages/
  lane: source lane
  zone: source zone
  mode: source mode
  branch: observed or validated declared branch
  worktree: C:\Dev\Ai.Os
  allowed_paths: exact allowed paths
  forbidden_paths: exact forbidden paths
  read_first_authority_files: source read-first files
  validator_chain: source validator chain
  mission: source mission
  task_summary: concise task statement
  strict_rules: source strict rules and inherited AI_OS non-actions
  stop_point: source stop point
  approval_classification: SAFE_NO_APPROVAL_REQUIRED, HUMAN_APPROVAL_REQUIRED, PROTECTED_ACTION_GATE_REQUIRED, or BLOCKED
  protected_action_classification: NOT_REQUESTED, REQUESTED_WITH_SCOPE, REQUESTED_WITHOUT_SCOPE, or BLOCKED
  state_alignment: PASS, FAIL, or NEEDS_PREFLIGHT
  evidence_contract: AIOS_CLI_EVIDENCE.v1-compatible
  executable: false
  preview_only: true
```

Preview path convention for future implementation:

```text
automation/orchestration/work_packets/proposed/<packet_id>.work_packet.preview.json
```

This path is a future implementation boundary only. This report does not create it.

## 7. Approval Classification Logic

Approval classification must be deterministic.

| Classification | Conditions |
|---|---|
| `SAFE_NO_APPROVAL_REQUIRED` | Read-only or report-only preview; no protected action; allowed paths only; no queue/approval/source/protected mutation; no secret/API/broker/live trading; branch/worktree aligned. |
| `HUMAN_APPROVAL_REQUIRED` | APPLY writes are requested inside allowed paths but no protected action is requested; or canonical queue/approval writes are requested by a future implementation. |
| `PROTECTED_ACTION_GATE_REQUIRED` | Any protected action is requested, including staging, commit, push, merge, PR create/merge, reset, clean, branch deletion, protected file edit, secret/credential action, broker/API/live trading action, scheduler/service/daemon action, or production mutation. |
| `BLOCKED` | Missing required fields, placeholders, forbidden paths, duplicate authority, branch/worktree mismatch, unsafe dirty state, unscoped protected action, secret risk, broker/live trading risk, or unauthorized automation. |

Approval rules:

- Validator PASS is evidence only.
- Dashboard, telemetry, reports, Relay output, Operator Relief output, and Night Supervisor cards are evidence only.
- Approval for one action does not transfer to another action.
- `SAFE_TO_PRESENT` is not approval to execute.
- Protected actions require current-session Human Owner approval and protected-action gate evidence.

## 8. Protected-Action Classification Logic

The adapter must inspect packet text for protected action intent.

Protected action types:

| Type | Triggers |
|---|---|
| `GIT_ADD` | Any staging request. |
| `GIT_COMMIT` | Any commit request or commit message. |
| `GIT_PUSH` | Any push request or remote publication. |
| `GH_PR_CREATE` | Any PR creation request. |
| `GH_PR_MERGE` | Any PR merge request. |
| `GIT_MERGE` | Any branch merge request. |
| `GIT_RESET` | Any reset request. |
| `GIT_CLEAN` | Any clean/delete-untracked request. |
| `BRANCH_DELETE` | Any branch deletion request. |
| `PROTECTED_FILE_EDIT` | Any edit to `AGENTS.md`, `README.md`, `WHITEPAPER.md`, protected governance, source, config, automation, control, Relay, or GitHub workflow paths outside explicit approval scope. |
| `SECRET_OR_CREDENTIAL_ACTION` | Any key, token, credential, broker account, password, or secret handling. |
| `BROKER_API_OR_LIVE_TRADING_ACTION` | Any broker integration, OANDA, real order, real webhook, or live execution path. |
| `SCHEDULER_SERVICE_OR_DAEMON_ACTION` | Any persistent automation, service, daemon, scheduler, or autonomous loop. |

Decision outcomes:

| Decision | Meaning |
|---|---|
| `NOT_REQUESTED` | No protected action detected. |
| `HUMAN_APPROVAL_REQUIRED` | Protected action is scoped but lacks current-session approval evidence. |
| `BLOCKED` | Protected action is unscoped, forbidden, or unsafe. |
| `SAFE_TO_PRESENT` | It is safe to present the approval request to Anthony; not safe to execute. |
| `SAFE_TO_COMMIT` | Only a separate commit gate may produce this for an exact commit action. |
| `SAFE_TO_PUSH` | Only a separate push gate may produce this for an exact push action. |

The ChatGPT adapter itself must not produce `SAFE_TO_COMMIT` or `SAFE_TO_PUSH`.

## 9. Branch/Worktree Validation Rules

Required preflight evidence when repo state matters:

```powershell
pwd
git status --short --branch
git branch --show-current
git remote -v
```

Validation rules:

1. `worktree` must resolve to `C:\Dev\Ai.Os` unless a separate explicit approval names another active worktree.
2. The packet branch must match the observed branch, or the packet must say `branch: resolve after preflight`.
3. The adapter must not switch branches.
4. Dirty state must be classified before any APPLY packet preview is accepted.
5. Dirty files inside the adapter output path may be classified as current mission only when the packet allows that path.
6. Dirty files outside the mission must be preserved and reported, not reverted.
7. If the packet assumes `main` but observed branch is different, the adapter must fail with `AIOS-PROMPT-AUTH-STATE-MISMATCH` unless the packet includes a safe preservation plan.
8. If dirty files overlap the mission and cannot be safely classified, the packet is blocked.
9. Current observed state overrides packet assumptions.

For this report run:

| Field | Observed |
|---|---|
| worktree | `C:\Dev\Ai.Os` |
| branch | `feature/full-operator-relief-closed-loop-v1` |
| remote | `origin https://github.com/ai-rtony91/Ai_Os.git` |
| branch state | ahead of origin by 3 |
| pre-existing dirty state | tracked script modification and untracked report directories existed before this report |

## 10. Evidence Output Schema

Every adapter result should emit an evidence object compatible with `AIOS_CLI_EVIDENCE.v1`:

```text
evidence:
  schema: AIOS_CLI_EVIDENCE.v1
  event_id: unique event id
  created_at_utc: ISO-8601 timestamp
  source_party: ChatGPT
  source_command: ChatGptToOrchestrationAdapter validate packet
  packet_id: source packet id
  lane: source lane
  mode: source mode
  repo_root: C:\Dev\Ai.Os
  branch: observed branch
  worktree: observed worktree
  git_status_short_branch: observed status
  dirty_state_class: classified dirty state
  allowed_paths: source allowed paths
  forbidden_paths: source forbidden paths
  read_paths: authority and source files read
  write_paths: empty for preview-only adapter; populated only for report output when approved
  output_paths: report or preview evidence paths
  status: READY, PREVIEW, NEEDS_APPROVAL, BLOCKED, or FAILED
  status_impact: CURRENT_ACTIVE or CURRENT_DETAIL_ONLY
  blocked_reasons: list
  risk_flags: list
  validator_chain: packet validator chain
  validator_results: adapter validation results
  approval_required: boolean
  approval_status: approval vocabulary value
  approval_authority: source approval authority
  protected_action_requested: boolean
  protected_action_type: protected action type or empty
  display_alert: boolean
  sos_wake_required: boolean
  wake_class: NONE, DISPLAY_ONLY, REVIEW_ONLY, or SOS
  redaction_status: redaction vocabulary value
  secret_scan_status: NO_SECRETS_DETECTED, SECRET_RISK_BLOCKED, NOT_SCANNED, or UNKNOWN
  executable: false
  next_safe_action: one exact next action
  stop_point: source stop point or adapter stop condition
```

Evidence rule:

```text
Evidence supports decisions. Evidence never approves execution.
```

## 11. Adapter Acceptance Tests

These are report-level acceptance tests for a future implementation. They are not executable tests created by this packet.

| Test ID | Input | Expected Result |
|---|---|---|
| `CHATGPT_ADAPTER_PASS_001` | Complete tokenized packet, observed branch matches, allowed paths exact, no protected actions, report-only output. | `status=PREVIEW`, `executable=false`, work packet preview emitted. |
| `CHATGPT_ADAPTER_FAIL_MISSING_TOKEN_001` | Packet lacks `AI_OS EXECUTION TOKEN` but requests Codex execution. | `status=BLOCKED`, missing token listed. |
| `CHATGPT_ADAPTER_FAIL_MISSING_IDENTITY_001` | Packet lacks worker identity or approval authority. | `status=BLOCKED`, missing identity fields listed. |
| `CHATGPT_ADAPTER_FAIL_PLACEHOLDER_001` | Packet contains `@filename`, `TODO`, `TBD`, or `{feature}`. | `status=BLOCKED`, placeholder findings listed. |
| `CHATGPT_ADAPTER_FAIL_BRANCH_001` | Packet declares `main`; observed branch is `feature/full-operator-relief-closed-loop-v1`; no preservation plan. | `status=BLOCKED`, label `AIOS-PROMPT-AUTH-STATE-MISMATCH`. |
| `CHATGPT_ADAPTER_FAIL_FORBIDDEN_PATH_001` | Packet writes `automation/` while only `Reports/bridge_audit/` is allowed. | `status=BLOCKED`, forbidden path finding listed. |
| `CHATGPT_ADAPTER_APPROVAL_PROTECTED_001` | Packet requests `git add` or `git commit` with exact file list but no current approval. | `status=NEEDS_APPROVAL`, protected action gate required. |
| `CHATGPT_ADAPTER_FAIL_SECRET_001` | Packet asks to read or print API keys. | `status=BLOCKED`, `SECRET_OR_CREDENTIAL_ACTION`. |
| `CHATGPT_ADAPTER_FAIL_LIVE_TRADING_001` | Packet asks to connect broker or place real order. | `status=BLOCKED`, broker/live trading risk. |
| `CHATGPT_ADAPTER_FAIL_DUP_AUTH_001` | Packet creates new queue or approval authority instead of using existing orchestration owners. | `status=BLOCKED`, duplicate authority risk. |

## 12. Example PASS Packet

This example is illustrative and not an instruction to execute.

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
Anthony / AI_OS Owner

PACKET ID:
EXAMPLE_REPORT_ONLY_PACKET_001

LANE:
EXAMPLE_REPORT_LANE

ZONE:
AI_OS Report Only Zone

WORKER IDENTITY:
Codex CLI Worker

MODE:
APPLY

BRANCH:
feature/full-operator-relief-closed-loop-v1

WORKTREE:
C:\Dev\Ai.Os

APPROVAL AUTHORITY:
Anthony / AI_OS Owner

READ-FIRST AUTHORITY FILES:
AGENTS.md
README.md
WHITEPAPER.md

ALLOWED PATHS:
Reports/bridge_audit/

FORBIDDEN PATHS:
AGENTS.md
README.md
WHITEPAPER.md
automation/
tools/
scripts/
src/
config/
control/
Relay/
.github/

VALIDATOR CHAIN:
1. Read AGENTS.md.
2. Read README.md.
3. Read WHITEPAPER.md.
4. Confirm path, branch, status, and remote.
5. Create only Reports/bridge_audit/EXAMPLE_REPORT.md.
6. Run git diff --check.
7. Run git status --short --branch.

MISSION:
Create one report-only mapping note.

TASK:
Write a report under the allowed path only.

STRICT RULES:
- No code.
- No scripts.
- No queues.
- No approvals.
- No commit.
- No push.
- No broker paths.
- No live trading paths.
- No secrets.
- Do not switch branches.

STOP POINT:
Stop after report creation and validation.

FINAL RESPONSE FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
```

Expected adapter result:

```text
status: PREVIEW
approval_required: false
approval_status: NOT_REQUIRED
protected_action_requested: false
branch_worktree_validation: PASS
executable: false
canonical_work_packet_preview: present
next_safe_action: Review the preview and approve a separate implementation packet only if needed.
```

## 13. Example FAIL Packet

This example is illustrative and not an instruction to execute.

```text
CODEX-ONLY PROMPT

AI_OS BOOTSTRAP REQUIRED

PACKET ID:
TBD

MODE:
APPLY

BRANCH:
main

WORKTREE:
C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN

ALLOWED PATHS:
@filename

MISSION:
Create the adapter, script, schema, queue, approval, and commit it.

TASK:
Implement {feature}, edit automation/, run git add ., commit, push, and connect broker API.

STOP POINT:
Done.
```

Expected adapter result:

```text
status: BLOCKED
blocked_reasons:
  - MISSING_EXECUTION_TOKEN
  - MISSING_IDENTITY_FIELD
  - MISSING_VALIDATION_FIELD
  - PLACEHOLDER_PRESENT
  - STATE_MISMATCH
  - FORBIDDEN_PATH_TARGETED
  - DUPLICATE_AUTHORITY_RISK
  - PROTECTED_ACTION_UNSCOPED
  - SECRET_OR_CREDENTIAL_RISK or BROKER_OR_LIVE_TRADING_RISK
executable: false
canonical_work_packet_preview: empty
display_alert: true
sos_wake_required: true
wake_class: SOS
next_safe_action: Generate a complete tokenized packet with real paths, observed branch/worktree state, exact allowed and forbidden paths, validator chain, approval authority, and stop point.
```

## 14. Exact Future Implementation Boundary

Future implementation may build only after a separate approved APPLY packet names exact paths, validator chain, and stop point.

Allowed future implementation concept:

```text
ChatGPT packet text
-> local adapter validation
-> canonical envelope preview
-> canonical work packet preview
-> human review
-> separate approval before queue write or execution
```

Recommended future implementation owner:

```text
automation/orchestration/
```

Canonical owners remain:

```text
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
```

Future implementation must not:

- create another harness head.
- create another approval authority.
- create another queue authority.
- use `tools/bridge` as the first implementation base.
- write queue files without explicit approval.
- write approval files without explicit approval.
- call OpenAI APIs without separate API approval, redaction, and no-secret validation.
- expose secrets.
- invoke Codex recursively.
- create persistent automation.
- perform protected repo actions.
- touch live trading or broker paths.

First future implementation should be DRY_RUN-first and preview-only:

```text
read packet text
validate against AGENTS.md
classify risk and approval need
emit evidence envelope
emit work packet preview
stop
```

## Final Recommendation

Use this mapping as the contract for the first adapter implementation. The adapter should prevent malformed ChatGPT-generated packets from reaching Codex or canonical orchestration state, while preserving the current AI_OS rule that evidence, validators, dashboards, reports, and previews are not approval.

Next safe action:

```text
Create a separate DRY_RUN-first implementation packet for a preview-only ChatGptToOrchestrationAdapter, or stop here and review this mapping before building code.
```
