# Codex Result To Evidence Adapter Mapping

Packet: `CODEX_RESULT_TO_EVIDENCE_ADAPTER_MAPPING_001`
Mode: `DRY_RUN` report output
Lane: `CODEX_RESULT_ADAPTER_MAPPING`
Branch observed: `feature/full-operator-relief-closed-loop-v1`
Worktree observed: `C:\Dev\Ai.Os`

## Purpose

Define how a human-facing Codex final response becomes canonical machine-readable evidence for:

- Night Supervisor
- Morning Digest
- Dashboard display
- Approval Projection
- SOS classification

This mapping does not create code, scripts, schemas, queues, approvals, telemetry, or automation. It defines the future `CodexResultToEvidenceAdapter` contract only.

## Current Evidence Basis

Read-first evidence:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/vacation_candidate/VACATION_KILLER_BLOCKERS.md`
- `Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md`
- `Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_PROOF.md`

Observed current baseline:

```text
## feature/full-operator-relief-closed-loop-v1...origin/feature/full-operator-relief-closed-loop-v1 [ahead 3]
 M scripts/backup/Start-AiOsT9SnapshotBackup.ps1
?? Reports/backup/
?? Reports/bridge_audit/
?? Reports/cli_everything/
?? Reports/vacation_candidate/
?? automation/orchestration/adapters/chatgpt_to_orchestration/
?? tests/fixtures/
?? tests/orchestration/
```

Observed Codex final response pattern:

```text
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
```

Failure pattern from `AGENTS.md`:

```text
WHAT FAILED:
WHY IT FAILED:
WHAT NEEDS TO HAPPEN NEXT:
WHERE TO REFERENCE:
SAFE NEXT COMMAND OR PROMPT:
STATUS: BLOCKED or FAILED
```

DRY_RUN pattern from `AGENTS.md`:

```text
SUMMARY:
WHAT WAS TESTED:
FINDINGS:
RECOMMENDATION:
SAFE NEXT COMMAND:
STATUS: DRY_RUN COMPLETE, NO FILES CHANGED
```

## Adapter Boundary

`CodexResultToEvidenceAdapter` is an evidence normalizer.

It may later:

- parse Codex final text.
- classify status.
- extract files changed.
- extract validation commands and outcomes.
- extract dirty-state summary.
- extract commit/push state.
- classify approval need.
- classify protected action need.
- emit preview-only `AIOS_CLI_EVIDENCE.v1` compatible evidence.

It must not:

- approve work.
- execute work.
- write queues.
- write approval inbox entries.
- write telemetry in the first scaffold.
- launch Codex.
- call OpenAI.
- call MCP tools.
- run subprocess providers.
- stage, commit, push, merge, create PRs, reset, clean, or delete branches.
- touch live trading, broker, secret, or production paths.

Every output remains:

```text
executable=false
```

## 1. Codex Final Report Input Fields

| Input field | Required | Source | Mapping notes |
|---|---|---|---|
| `raw_result_text` | yes | Entire Codex final response | Preserved for hash/provenance, not copied into downstream display in full. |
| `packet_id` | recommended | Packet header, report body, or caller metadata | If absent, set `packet_id=UNKNOWN` and mark `status=PARTIAL`. |
| `lane` | recommended | Packet header, report body, or caller metadata | If absent, set `lane=UNKNOWN`; do not infer from path unless caller supplies path. |
| `mode` | recommended | Packet header, final text, or caller metadata | Values: `DRY_RUN`, `APPLY`, `UNKNOWN`. |
| `branch` | recommended | Report text or caller git preflight | If absent and repo state matters, status is `PARTIAL`. |
| `worktree` | recommended | Report text or caller git preflight | If absent and repo state matters, status is `PARTIAL`. |
| `summary_section` | yes for success/DRY_RUN | `SUMMARY:` heading | Captures human-readable result summary. |
| `what_changed_section` | conditional | `WHAT CHANGED:` heading | Required for successful APPLY. |
| `files_changed_section` | conditional | `FILES CHANGED:` heading | Required when files changed. |
| `validation_section` | yes | `VALIDATION:` or `WHAT WAS TESTED:` heading | Records validation evidence and whether command outcomes were explicit. |
| `remaining_dirty_files_section` | conditional | `REMAINING DIRTY FILES:` heading | Required for repo-mutating or repo-state tasks. |
| `safe_next_command_section` | yes | `SAFE NEXT COMMAND:` or `SAFE NEXT COMMAND OR PROMPT:` heading | Used for downstream next-action display. |
| `status_section` | yes | `STATUS:` heading | Primary input for status mapping. |
| `failure_sections` | conditional | `WHAT FAILED:` etc. | Required for blocked/failed result. |
| `commit_status_text` | conditional | `STATUS`, `VALIDATION`, or explicit `COMMIT STATUS` text | Must distinguish no commit from committed. |
| `push_status_text` | conditional | `STATUS`, `VALIDATION`, or explicit `PUSH STATUS` text | Must distinguish no push from pushed. |
| `source_message_id` | optional | Caller metadata | Useful for future conversation/evidence provenance. |
| `created_at_utc` | recommended | Caller timestamp | If absent, adapter uses parse time and marks freshness source as adapter-generated. |

## 2. Required Output Evidence Fields

The output must be compatible with `AIOS_CLI_EVIDENCE.v1` vocabulary.

| Output field | Required | Rule |
|---|---|---|
| `schema` | yes | `AIOS_CODEX_RESULT_EVIDENCE.v1` for adapter-specific object plus `AIOS_CLI_EVIDENCE.v1` compatibility fields. |
| `event_id` | yes | Stable generated ID, e.g. `codex_result_<timestamp>_<hash8>`. |
| `created_at_utc` | yes | Adapter emission time. |
| `source_party` | yes | `Codex CLI Worker`. |
| `source_command` | yes | `codex_final_response_parse` unless caller provides a more specific label. |
| `packet_id` | yes | Parsed or `UNKNOWN`. |
| `lane` | yes | Parsed or `UNKNOWN`. |
| `mode` | yes | Parsed or `UNKNOWN`. |
| `repo_root` | conditional | Required when repo state is present or expected. |
| `branch` | conditional | Required when repo state is present or expected. |
| `worktree` | conditional | Required when repo state is present or expected. |
| `status` | yes | `COMPLETE`, `DRY_RUN_COMPLETE`, `BLOCKED`, `FAILED`, `NEEDS_APPROVAL`, `PARTIAL`, or `UNKNOWN`. |
| `status_impact` | yes | `NO_ACTION_NEEDED`, `DISPLAY_ONLY`, `OPERATOR_REVIEW`, `APPROVAL_REQUIRED`, `BLOCKS_CONTINUATION`, or `UNSAFE_TO_CONTINUE`. |
| `blocked_reasons` | yes | Empty list when not blocked. |
| `risk_flags` | yes | Empty list when no risk flagged. |
| `files_changed` | yes | Empty list when none or no files changed. |
| `files_inspected` | recommended | Empty list if unknown. |
| `output_paths` | recommended | Reports or artifacts created. |
| `validation_results` | yes | Structured list of validation commands/statuses. |
| `git_status_short_branch` | conditional | Required when supplied by final report or caller. |
| `dirty_state` | yes | `CLEAN`, `DIRTY_KNOWN_CLASSIFIED`, `DIRTY_UNKNOWN`, `NOT_REPORTED`, or `NOT_APPLICABLE`. |
| `commit_status` | yes | `NO_COMMIT`, `COMMITTED`, `COMMIT_REQUESTED`, `UNKNOWN`, or `NOT_APPLICABLE`. |
| `push_status` | yes | `NO_PUSH`, `PUSHED`, `PUSH_REQUESTED`, `UNKNOWN`, or `NOT_APPLICABLE`. |
| `approval_required` | yes | Boolean. |
| `approval_status` | yes | `NOT_REQUIRED`, `REQUIRED`, `MISSING`, `PRESENT_AS_EVIDENCE_ONLY`, or `UNKNOWN`. |
| `protected_action_requested` | yes | Boolean. |
| `protected_actions` | yes | Empty list when none. |
| `display_alert` | yes | Boolean. |
| `sos_wake_required` | yes | Boolean. |
| `wake_class` | yes | `NONE`, `DISPLAY_ONLY`, `APPROVAL_REQUIRED`, `BLOCKED_CONTINUATION`, `SAFETY_RISK`, or `UNKNOWN`. |
| `freshness_status` | yes | `CURRENT`, `STALE`, `UNKNOWN`, or `ADAPTER_PARSE_TIME_ONLY`. |
| `freshness_timestamp_utc` | yes | Source timestamp if available, else adapter parse time. |
| `redaction_status` | yes | `NOT_REQUIRED`, `REDACTED`, `SECRET_RISK_BLOCKED`, or `UNKNOWN`. |
| `raw_input_hash` | yes | Hash of raw result text. |
| `raw_input_stored` | yes | Boolean; first scaffold should set `false` unless explicitly outputting a preview file. |
| `executable` | yes | Always `false`. |
| `next_safe_action` | yes | Parsed safe next command/prompt or generated safe review action. |
| `stop_point` | recommended | Parsed or synthesized from report completion. |

## 3. Success, Failure, And Block Status Mapping

| Codex final status evidence | Output `status` | Output `status_impact` | Display | SOS |
|---|---|---|---|---|
| `COMPLETE, NO COMMIT, NO PUSH` | `COMPLETE` | `DISPLAY_ONLY` | true | false |
| `DRY_RUN COMPLETE, NO FILES CHANGED` | `DRY_RUN_COMPLETE` | `DISPLAY_ONLY` | true | false |
| `COMPLETE` with no validation evidence | `PARTIAL` | `OPERATOR_REVIEW` | true | false |
| `COMPLETE` with files outside allowed scope | `BLOCKED` | `UNSAFE_TO_CONTINUE` | true | true |
| `BLOCKED` | `BLOCKED` | `BLOCKS_CONTINUATION` | true | true |
| `FAILED` | `FAILED` | `BLOCKS_CONTINUATION` | true | true only if continuation is blocked or safety risk exists |
| `NEEDS_APPROVAL` or approval missing | `NEEDS_APPROVAL` | `APPROVAL_REQUIRED` | true | true |
| Missing `STATUS:` | `PARTIAL` | `OPERATOR_REVIEW` | true | false |
| Ambiguous status | `UNKNOWN` | `OPERATOR_REVIEW` | true | false |

Validator PASS never maps to approval. Approval must be explicit, scoped, current-session, and protected-action specific where required.

## 4. Files Changed Mapping

The adapter should extract files from:

- `FILES CHANGED:` section.
- `WHAT CHANGED:` section when it clearly lists paths.
- `git status --short --branch` output in `REMAINING DIRTY FILES:`.
- Optional caller-provided changed-file metadata.

Mapping:

| Input evidence | Output field |
|---|---|
| No file changes stated | `files_changed=[]`, `changed_file_count=0` |
| One or more file paths changed | `files_changed=[...]`, `changed_file_count=n` |
| Directories only | `files_changed_directories=[...]`, `file_granularity=directory_only` |
| Untracked directory from git status | `dirty_paths=[{"state":"untracked","path":"..."}]` |
| Modified tracked file from git status | `dirty_paths=[{"state":"modified","path":"..."}]` |
| Path outside allowed boundary | `risk_flags += ["CHANGED_FILE_OUTSIDE_ALLOWED_PATHS"]`, `status=BLOCKED` |
| Protected file/path changed without scope | `risk_flags += ["PROTECTED_PATH_CHANGED"]`, `status=BLOCKED` |

First scaffold should avoid complex path inference. If a line is not confidently a path, store it under `unparsed_file_lines` and set `status=PARTIAL` when file proof matters.

## 5. Validation Result Mapping

Validation input is human text, so the adapter should classify conservatively.

| Validation text | Output mapping |
|---|---|
| Explicit command plus pass result | `validation_results[].status=PASS` |
| Explicit command plus fail result | `validation_results[].status=FAIL`, `status=FAILED` or `BLOCKED` |
| Explicit command plus warning only | `validation_results[].status=WARNING`, `display_alert=true` |
| Command was not run | `validation_results[].status=NOT_RUN`, `status=PARTIAL` when required |
| Validation says "not able to run" | `validation_results[].status=BLOCKED_OR_SKIPPED`, `blocked_reasons += ["VALIDATION_NOT_RUN"]` |
| `git diff --check` passed | `diff_check_status=PASS` |
| `git diff --check` failed | `diff_check_status=FAIL`, `status=FAILED`, `sos_wake_required=true` if continuation depends on it |
| Test suite passed | `test_status=PASS`, with command and count when parseable |
| Test suite failed | `test_status=FAIL`, `status=FAILED`, `display_alert=true` |

Validation PASS is evidence only. It must not set `approval_status=APPROVED`.

## 6. No Commit / No Push Mapping

Codex final text must distinguish "no commit/no push" from missing information.

| Text evidence | `commit_status` | `push_status` | Risk |
|---|---|---|---|
| `NO COMMIT, NO PUSH` | `NO_COMMIT` | `NO_PUSH` | none |
| `No commit. No push.` | `NO_COMMIT` | `NO_PUSH` | none |
| Commit hash present | `COMMITTED` | unchanged unless push stated | protected action evidence; require approval provenance |
| Push stated | unchanged unless commit stated | `PUSHED` | protected action evidence; require approval provenance |
| Commit requested but not done | `COMMIT_REQUESTED` | `NO_PUSH` or `UNKNOWN` | approval required |
| Push requested but not done | `UNKNOWN` or `NO_COMMIT` | `PUSH_REQUESTED` | approval required |
| Missing commit/push text | `UNKNOWN` | `UNKNOWN` | `status=PARTIAL` when repo mutation was possible |

If commit or push occurred and approval evidence is missing, output must set:

```text
status=PARTIAL
display_alert=true
sos_wake_required=true
wake_class=APPROVAL_REQUIRED
risk_flags += ["PROTECTED_ACTION_APPROVAL_EVIDENCE_MISSING"]
```

## 7. Approval-Needed Mapping

Approval is required when the final report or parsed evidence indicates:

- protected action requested.
- commit requested.
- push requested.
- merge requested.
- PR creation requested.
- branch deletion requested.
- reset/clean requested.
- protected path mutation outside explicit scope.
- queue write requested.
- approval inbox write requested.
- external API/private evidence transmission requested.
- secret/broker/live trading risk.
- blocked continuation needs Anthony decision.

Mapping:

| Condition | `approval_required` | `approval_status` | `status` | SOS |
|---|---:|---|---|---:|
| Report-only completion | false | `NOT_REQUIRED` | `COMPLETE` or `DRY_RUN_COMPLETE` | false |
| Protected action requested but not approved | true | `MISSING` | `NEEDS_APPROVAL` | true |
| Approval evidence mentioned but not validated | true | `PRESENT_AS_EVIDENCE_ONLY` | `NEEDS_APPROVAL` or `PARTIAL` | true |
| Current-session exact approval confirmed by caller metadata | true | `REQUIRED` until future approval validator confirms | false in first scaffold |
| Secret, broker, or live trading path | true | `MISSING` | `BLOCKED` | true |

First scaffold must not validate approvals as approved. It can only say approval is required, missing, not required, or present as evidence only.

## 8. Protected-Action Mapping

Protected actions include:

- `git add`
- `git commit`
- `git push`
- `gh pr create`
- `gh pr merge`
- `git merge`
- `git reset`
- `git clean`
- branch deletion

Additional protected categories for vacation readiness:

- edits to protected governance/source/runtime paths outside packet scope.
- queue writes.
- approval writes.
- telemetry writes in a non-telemetry packet.
- OpenAI/API/MCP calls without approval.
- broker/live trading/real order path.
- secret handling or secret display.

Mapping:

| Detection | Output |
|---|---|
| Action requested but not executed | `protected_action_requested=true`, `status=NEEDS_APPROVAL` |
| Action executed with explicit evidence | `protected_action_requested=true`, `status=PARTIAL` until approval provenance is validated |
| Action executed without approval evidence | `status=BLOCKED`, `sos_wake_required=true` |
| Action denied/stopped safely | `status=COMPLETE` or `BLOCKED` depending mission outcome, `protected_action_requested=true`, `approval_status=MISSING` |

## 9. Dirty-State Mapping

The adapter should convert dirty-state text into normalized fields.

| Input | `dirty_state` | Output behavior |
|---|---|---|
| Clean status | `CLEAN` | no dirty alert |
| Dirty state classified in report | `DIRTY_KNOWN_CLASSIFIED` | display-only unless blocker remains |
| Dirty state shown but unclassified | `DIRTY_UNKNOWN` | `display_alert=true`, `status=PARTIAL` |
| Dirty tracked source or protected script remains | `DIRTY_KNOWN_CLASSIFIED` plus risk flag | display alert; SOS if it blocks continuation |
| Dirty state omitted | `NOT_REPORTED` | partial when repo state matters |
| Task not involving repo state | `NOT_APPLICABLE` | no dirty alert |

Current vacation baseline maps to:

```text
dirty_state=DIRTY_KNOWN_CLASSIFIED
risk_flags=["TRACKED_BACKUP_SCRIPT_PATCH_REMAINS","UNTRACKED_ADAPTER_SOURCE_REMAINS"]
display_alert=true
sos_wake_required=false
```

SOS stays false because the state is classified and no immediate execution is requested. It becomes true if a worker attempts to proceed into a vacation trial or protected action without resolving the blocker.

## 10. Evidence Freshness Fields

Freshness is required so Night Supervisor and Morning Digest do not treat old final reports as current blockers.

Required fields:

| Field | Meaning |
|---|---|
| `source_created_at_utc` | Timestamp from report/caller metadata if known. |
| `adapter_parsed_at_utc` | Time the adapter parsed the result. |
| `freshness_timestamp_utc` | Timestamp used for downstream freshness decisions. |
| `freshness_basis` | `SOURCE_TIMESTAMP`, `ADAPTER_PARSE_TIME`, or `CALLER_METADATA`. |
| `freshness_status` | `CURRENT`, `STALE`, `UNKNOWN`, or `ADAPTER_PARSE_TIME_ONLY`. |
| `stale_after_minutes` | Recommended downstream threshold, supplied by caller or default policy. |
| `source_evidence_path` | File path or conversation reference if stored. |
| `source_hash` | Hash of raw final report input. |

Rules:

- If the adapter only has raw pasted text and no source timestamp, set `freshness_status=ADAPTER_PARSE_TIME_ONLY`.
- If the report references historical files or stale state, set `freshness_status=UNKNOWN` unless caller confirms current context.
- Night Supervisor should not wake Anthony from stale evidence unless a current scan confirms the blocker.

## 11. SOS And Display-Alert Fields

Display alert and SOS must remain separate.

| Condition | `display_alert` | `sos_wake_required` | `wake_class` |
|---|---:|---:|---|
| Successful report-only completion | true | false | `DISPLAY_ONLY` |
| Successful source change with validation | true | false | `DISPLAY_ONLY` |
| Dirty state remains but classified | true | false | `DISPLAY_ONLY` |
| Dirty state unknown and continuation depends on it | true | true | `BLOCKED_CONTINUATION` |
| Validator failure blocks mission | true | true | `BLOCKED_CONTINUATION` |
| Protected action approval needed | true | true | `APPROVAL_REQUIRED` |
| Secret/broker/live trading risk | true | true | `SAFETY_RISK` |
| Missing required final report sections | true | false | `UNKNOWN` |
| Routine DRY_RUN completion | true | false | `DISPLAY_ONLY` |

The first scaffold should default to display-only for complete results and reserve SOS for blocked continuation, protected approval need, or safety risk.

## 12. Acceptance Tests Needed

Minimum test suite before Adapter V1:

| Test ID | Input | Expected |
|---|---|---|
| `CODEX_RESULT_SUCCESS_REPORT_001` | Complete final report with `COMPLETE, NO COMMIT, NO PUSH` | `status=COMPLETE`, `commit_status=NO_COMMIT`, `push_status=NO_PUSH`, `executable=false`. |
| `CODEX_RESULT_DRY_RUN_001` | DRY_RUN final report with no files changed | `status=DRY_RUN_COMPLETE`, no changed files, display alert only. |
| `CODEX_RESULT_FAILURE_001` | Failure format with command failure | `status=FAILED`, blocked reason captured. |
| `CODEX_RESULT_BLOCKED_001` | Blocked format with missing required field | `status=BLOCKED`, `sos_wake_required=true` if continuation blocked. |
| `CODEX_RESULT_NEEDS_APPROVAL_COMMIT_001` | Final text asks for commit approval | `approval_required=true`, `status=NEEDS_APPROVAL`, `protected_actions=["git commit"]`. |
| `CODEX_RESULT_PROTECTED_PUSH_001` | Final text asks for push | `approval_required=true`, `protected_actions=["git push"]`, SOS true. |
| `CODEX_RESULT_VALIDATION_PASS_001` | `git diff --check` pass and tests pass | validation results normalized; approval remains not required unless protected action requested. |
| `CODEX_RESULT_VALIDATION_FAIL_001` | `git diff --check` failure | `status=FAILED`, display alert true, SOS true when continuation blocked. |
| `CODEX_RESULT_FILES_CHANGED_001` | Files changed section lists report file | `files_changed` contains path and allowed-path classification. |
| `CODEX_RESULT_OUT_OF_SCOPE_FILE_001` | Files changed section lists protected source file outside scope | `status=BLOCKED`, risk flag set. |
| `CODEX_RESULT_DIRTY_CLASSIFIED_001` | Remaining dirty files are classified | `dirty_state=DIRTY_KNOWN_CLASSIFIED`, display alert true, SOS false. |
| `CODEX_RESULT_DIRTY_UNKNOWN_001` | Dirty files remain but no classification | `dirty_state=DIRTY_UNKNOWN`, `status=PARTIAL`. |
| `CODEX_RESULT_MISSING_STATUS_001` | Final report lacks `STATUS:` | `status=PARTIAL`, display alert true, SOS false. |
| `CODEX_RESULT_SECRET_RISK_001` | Final report includes credential or secret-like risk | `status=BLOCKED`, `redaction_status=SECRET_RISK_BLOCKED`, SOS true. |
| `CODEX_RESULT_LIVE_TRADING_001` | Final report references broker/live order path | `status=BLOCKED`, risk flag set, SOS true. |
| `CODEX_RESULT_FRESHNESS_SOURCE_001` | Caller supplies source timestamp | freshness uses source timestamp. |
| `CODEX_RESULT_FRESHNESS_PARSE_ONLY_001` | No source timestamp | freshness basis is adapter parse time only. |
| `CODEX_RESULT_EXEC_FALSE_001` | Any input | output always has `executable=false`. |
| `CODEX_RESULT_NO_QUEUE_WRITE_001` | Any input | no queue file is written. |
| `CODEX_RESULT_NO_APPROVAL_WRITE_001` | Any input | no approval file is written. |
| `CODEX_RESULT_NO_TELEMETRY_WRITE_001` | First scaffold input | no telemetry file is written. |

Minimum acceptance threshold:

- All status mapping tests pass.
- All protected-action tests pass.
- All validation mapping tests pass.
- All dirty-state tests pass.
- All freshness tests pass.
- All outputs preserve `executable=false`.
- No source, queue, approval, telemetry, schema, OpenAI, MCP, subprocess, broker, or live trading behavior exists in the first scaffold.

## 13. Exact Next APPLY Packet For Scaffold

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
Anthony / AI_OS Owner

PACKET ID:
CODEX_RESULT_TO_EVIDENCE_ADAPTER_SCAFFOLD_APPLY_001

LANE:
CODEX_RESULT_ADAPTER_SCAFFOLD

ZONE:
AI_OS Vacation Candidate / Codex Evidence Loop

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
Reports/bridge_audit/CODEX_RESULT_TO_EVIDENCE_ADAPTER_MAPPING.md
Reports/vacation_candidate/VACATION_BASELINE_CLASSIFICATION.md

ALLOWED PATHS:
automation/orchestration/adapters/codex_result_to_evidence/
tests/orchestration/adapters/
tests/fixtures/codex_result_to_evidence/

PROTECTED PATHS:
AGENTS.md
README.md
WHITEPAPER.md
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
tools/
scripts/
src/
config/
control/
Relay/
.github/
schemas/
telemetry/

MISSION:
Create the first preview-only CodexResultToEvidenceAdapter scaffold that parses Codex final report text and emits machine-readable evidence with executable=false.

TASK:
Create only a local adapter scaffold and tests for parser, status mapping, file mapping, validation mapping, dirty-state mapping, protected-action mapping, approval-needed mapping, freshness fields, SOS/display-alert fields, and evidence output.

STRICT RULES:
- Preview-only adapter.
- executable=false on every output.
- No queue writes.
- No approval writes.
- No telemetry writes.
- No schema creation.
- No OpenAI calls.
- No MCP calls.
- No Codex launch.
- No subprocess/provider dispatch.
- No commits.
- No pushes.
- No live trading paths.
- No broker paths.
- No secrets.

VALIDATOR CHAIN:
1. Read AGENTS.md.
2. Read README.md.
3. Read WHITEPAPER.md.
4. Read Reports/bridge_audit/CODEX_RESULT_TO_EVIDENCE_ADAPTER_MAPPING.md.
5. Confirm branch/worktree state.
6. Create only approved adapter source, tests, and fixtures.
7. Run python -m py_compile on adapter source files.
8. Run adapter pytest suite.
9. Run git diff --check.
10. Run git status --short --branch.

STOP POINT:
Stop after scaffold creation, validation, tests, diff check, and status report. No commit. No push.

FINAL RESPONSE FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
```

## Recommendation

Recommendation: `BUILD + VALIDATE`, but only as a preview-only local scaffold after this mapping is accepted.

This adapter is the fastest way to convert Codex final text into evidence that Night Supervisor, Morning Digest, Dashboard, Approval Projection, and SOS classification can consume. It should be built before Relay, Night Supervisor, or dashboard expansion because those systems need normalized result evidence first.

## Stop Point

Report only. No source files edited. No scripts created. No schemas created. No queue files written. No approval files written. No telemetry files written. No commit. No push.
