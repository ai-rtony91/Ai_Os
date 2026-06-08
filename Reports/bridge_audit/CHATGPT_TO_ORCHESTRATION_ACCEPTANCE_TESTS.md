# ChatGPT To Orchestration Acceptance Tests

Packet: CHATGPT_TO_ORCHESTRATION_ACCEPTANCE_TESTS_001
Mode: DRY_RUN report output
Lane: CHATGPT_ADAPTER_ACCEPTANCE_TESTS
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os

## Purpose

Define the acceptance-test suite required before `ChatGptToOrchestrationAdapter` can be implemented.

This is a report-only test specification. It creates no code, scripts, schemas, adapters, queues, approvals, automation, protected-file edits, commits, pushes, broker paths, live trading paths, or secrets.

## Source Authority Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md`
- `Reports/bridge_audit/CANONICAL_HARNESS_SELECTION.md`
- `Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md`
- `Reports/bridge_audit/FIRST_ADAPTER_SELECTION.md`
- `Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_MAPPING.md`
- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`

## Acceptance Test Boundary

The future adapter must be accepted only when it proves that ChatGPT-generated packet text can be validated, classified, normalized, and previewed without creating execution authority.

Every test in this report assumes:

- `AGENTS.md` remains packet law.
- `automation/orchestration/work_packets/` remains the canonical queue owner.
- `automation/orchestration/approval_inbox/` remains the canonical approval owner.
- `automation/orchestration/workers/` remains the worker identity/routing owner.
- `automation/orchestration/validators/` remains validator evidence owner.
- `automation/orchestration/commit_packages/` remains commit package planning owner.
- `executable=false` is the default and required adapter output.
- Evidence is not approval.
- Validator PASS is not approval.
- Dashboard, telemetry, reports, Relay, Operator Relief output, and Night Supervisor cards are not approval.

## Test Result Vocabulary

| Result | Meaning |
|---|---|
| `PASS` | Adapter result matches expected status, evidence, preview, and safety fields exactly. |
| `FAIL` | Adapter result does not match expected status, evidence, preview, or safety fields. |
| `BLOCKED_EXPECTED` | Adapter correctly blocks unsafe or incomplete input. |
| `NEEDS_APPROVAL_EXPECTED` | Adapter correctly classifies a scoped action that requires Human Owner approval. |
| `NOT_APPLICABLE` | Test does not apply to the current adapter mode. |

## Required Output Fields For Every Test

Each test result must include:

| Field | Required |
|---|---:|
| `test_id` | yes |
| `packet_id` | yes |
| `input_class` | yes |
| `expected_status` | yes |
| `actual_status` | yes |
| `blocked_reasons` | yes |
| `risk_flags` | yes |
| `missing_fields` | yes |
| `placeholder_findings` | yes |
| `branch_worktree_validation` | yes |
| `approval_required` | yes |
| `approval_status` | yes |
| `protected_action_requested` | yes |
| `protected_action_type` | yes |
| `redaction_status` | yes |
| `executable` | yes |
| `canonical_envelope_present` | yes |
| `work_packet_preview_present` | yes |
| `evidence_output_present` | yes |
| `next_safe_action` | yes |

## 1. PASS Test Cases

| Test ID | Input Condition | Expected Result |
|---|---|---|
| `PASS_REPORT_ONLY_001` | Complete tokenized report-only packet, matching branch/worktree, exact allowed path `Reports/bridge_audit/`, protected paths forbidden, no protected action. | `status=PREVIEW`, `approval_required=false`, `approval_status=NOT_REQUIRED`, `protected_action_requested=false`, `executable=false`, envelope and work packet preview present. |
| `PASS_DRY_RUN_INSPECT_001` | Complete tokenized `DRY_RUN` packet for read-only inspection, no file output, exact stop point, final report format present. | `status=PREVIEW`, `approval_required=false`, `executable=false`, evidence output present, work packet preview present. |
| `PASS_APPLY_REPORT_ALLOWED_PATH_001` | Complete `APPLY` packet creates one report under allowed report path and blocks commits/pushes/source edits. | `status=PREVIEW`, `approval_required=false` for preview, `executable=false`, write path classified as allowed report output. |
| `PASS_RESOLVE_AFTER_PREFLIGHT_001` | Packet branch is `resolve after preflight`, preflight evidence supplies observed branch, and no branch switch is requested. | `state_alignment=PASS`, observed branch recorded, `executable=false`. |
| `PASS_PROTECTED_PATHS_FORBIDDEN_001` | Packet lists protected paths in forbidden path section and only writes to allowed report path. | Protected paths classified as forbidden, no protected-path violation, `status=PREVIEW`. |

## 2. FAIL Test Cases

| Test ID | Input Condition | Expected Result |
|---|---|---|
| `FAIL_NO_CODEX_MARKER_001` | Packet intended for Codex does not begin with `CODEX-ONLY PROMPT`. | `status=BLOCKED`, `blocked_reasons` includes `MISSING_ROUTING_MARKER`, no work packet preview accepted. |
| `FAIL_NO_EXECUTION_TOKEN_001` | Packet requests Codex execution but lacks `AI_OS EXECUTION TOKEN`. | `status=BLOCKED`, `blocked_reasons` includes `MISSING_EXECUTION_TOKEN`. |
| `FAIL_NO_BOOTSTRAP_001` | Packet lacks `AI_OS BOOTSTRAP REQUIRED`. | `status=BLOCKED`, `blocked_reasons` includes `MISSING_BOOTSTRAP`. |
| `FAIL_DUPLICATE_AUTHORITY_001` | Packet creates a new queue, approval head, governance authority, or bridge authority. | `status=BLOCKED`, `risk_flags` includes `DUPLICATE_AUTHORITY_RISK`. |
| `FAIL_UNAUTHORIZED_AUTOMATION_001` | Packet creates scheduler, daemon, autonomous loop, or persistent runner without explicit approval. | `status=BLOCKED`, `risk_flags` includes `UNAUTHORIZED_AUTOMATION`. |
| `FAIL_LIVE_TRADING_001` | Packet requests broker connection, OANDA integration, real order, real webhook, or live execution path. | `status=BLOCKED`, `risk_flags` includes `BROKER_OR_LIVE_TRADING_RISK`, `sos_wake_required=true`. |

## 3. Missing-Field Test Cases

| Test ID | Missing Field | Expected Result |
|---|---|---|
| `MISSING_IDENTITY_MARKER_001` | `IDENTITY MARKER` | `status=BLOCKED`, `missing_fields` includes `identity_marker`. |
| `MISSING_SUPERVISOR_001` | `SUPERVISOR IDENTITY` | `status=BLOCKED`, `missing_fields` includes `supervisor_identity`. |
| `MISSING_PACKET_ID_001` | `PACKET ID` | `status=BLOCKED`, `missing_fields` includes `packet_id`. |
| `MISSING_MODE_001` | `MODE` | `status=BLOCKED`, `missing_fields` includes `mode`. |
| `MISSING_ZONE_001` | `ZONE` | `status=BLOCKED`, `missing_fields` includes `zone`. |
| `MISSING_WORKER_001` | `WORKER IDENTITY` | `status=BLOCKED`, `missing_fields` includes `worker_identity`. |
| `MISSING_LANE_001` | `LANE` | `status=BLOCKED`, `missing_fields` includes `lane`. |
| `MISSING_WORKTREE_001` | `WORKTREE` | `status=BLOCKED`, `missing_fields` includes `worktree`. |
| `MISSING_BRANCH_001` | `BRANCH` | `status=BLOCKED`, `missing_fields` includes `branch`. |
| `MISSING_ALLOWED_PATHS_001` | `ALLOWED PATHS` | `status=BLOCKED`, `missing_fields` includes `allowed_paths`. |
| `MISSING_FORBIDDEN_PATHS_001` | `FORBIDDEN PATHS` or `PROTECTED PATHS` | `status=BLOCKED`, `missing_fields` includes `forbidden_paths`. |
| `MISSING_APPROVAL_AUTHORITY_001` | `APPROVAL AUTHORITY` | `status=BLOCKED`, `missing_fields` includes `approval_authority`. |
| `MISSING_VALIDATOR_CHAIN_001` | `VALIDATOR CHAIN` | `status=BLOCKED`, `missing_fields` includes `validator_chain`. |
| `MISSING_STOP_POINT_001` | `STOP POINT` | `status=BLOCKED`, `missing_fields` includes `stop_point`. |
| `MISSING_MISSION_001` | `MISSION` | `status=BLOCKED`, `missing_fields` includes `mission`. |
| `MISSING_PREFLIGHT_001` | branch/worktree preflight or equivalent state confirmation | `status=BLOCKED`, `missing_fields` includes `preflight`. |
| `MISSING_FINAL_REPORT_001` | `FINAL RESPONSE FORMAT` | `status=BLOCKED`, `missing_fields` includes `final_report_format`. |

## 4. Branch Mismatch Test Cases

Observed branch for these tests:

```text
feature/full-operator-relief-closed-loop-v1
```

| Test ID | Input Branch | Expected Result |
|---|---|---|
| `BRANCH_MATCH_001` | `feature/full-operator-relief-closed-loop-v1` | `branch_worktree_validation=PASS`. |
| `BRANCH_RESOLVE_PREFLIGHT_001` | `resolve after preflight` | Adapter uses observed branch and returns `branch_worktree_validation=PASS`. |
| `BRANCH_MAIN_MISMATCH_001` | `main` with no preservation plan | `status=BLOCKED`, label `AIOS-PROMPT-AUTH-STATE-MISMATCH`. |
| `BRANCH_UNKNOWN_001` | blank, unknown, or placeholder branch | `status=BLOCKED`, `missing_fields` or `placeholder_findings` records branch defect. |
| `BRANCH_SWITCH_REQUEST_001` | Packet asks adapter or Codex to switch branches. | `status=BLOCKED`, `risk_flags` includes branch switch outside scope. |
| `BRANCH_INVENTED_STATE_001` | Packet claims repo is clean/synced without observed evidence. | `status=BLOCKED`, `blocked_reasons` includes invented or unverifiable branch state. |

## 5. Worktree Mismatch Test Cases

Required active worktree:

```text
C:\Dev\Ai.Os
```

| Test ID | Input Worktree | Expected Result |
|---|---|---|
| `WORKTREE_MATCH_001` | `C:\Dev\Ai.Os` | `branch_worktree_validation=PASS`. |
| `WORKTREE_LEGACY_ONEDRIVE_001` | `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` | `status=BLOCKED`, `blocked_reasons` includes prohibited legacy path. |
| `WORKTREE_OLD_REPO_001` | `C:\Dev\Ai_Os_OLD_DO_NOT_USE` or `C:\Users\mylab\OneDrive\GitHub\AI_OS_V2_OLD_DO_NOT_USE` | `status=BLOCKED`, `blocked_reasons` includes legacy inactive repo path. |
| `WORKTREE_UNKNOWN_001` | blank or placeholder worktree | `status=BLOCKED`, `missing_fields` or `placeholder_findings` includes worktree. |
| `WORKTREE_DIFFERENT_REPO_001` | Any repo root not explicitly approved as current worktree | `status=BLOCKED`, `branch_worktree_validation=FAIL`. |

## 6. Protected-Path Test Cases

Protected paths:

```text
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
```

| Test ID | Input Condition | Expected Result |
|---|---|---|
| `PROTECTED_PATH_READ_FIRST_001` | Packet reads `AGENTS.md`, `README.md`, and `WHITEPAPER.md` as authority only. | Allowed as read-first evidence, no violation. |
| `PROTECTED_PATH_EDIT_AGENTS_001` | Packet edits `AGENTS.md`. | `status=BLOCKED` or `PROTECTED_ACTION_GATE_REQUIRED` when separately scoped; no default pass. |
| `PROTECTED_PATH_EDIT_AUTOMATION_001` | Packet writes `automation/`. | `status=BLOCKED`, `protected_action_type=PROTECTED_FILE_EDIT`. |
| `PROTECTED_PATH_EDIT_SCRIPTS_001` | Packet writes `scripts/`. | `status=BLOCKED`, `protected_action_type=PROTECTED_FILE_EDIT`. |
| `PROTECTED_PATH_EDIT_GITHUB_001` | Packet writes `.github/`. | `status=BLOCKED`, `protected_action_type=PROTECTED_FILE_EDIT`. |
| `PROTECTED_PATH_ALLOWED_REPORT_001` | Packet writes only `Reports/bridge_audit/<report>.md`. | `status=PREVIEW`, no protected-path violation. |
| `PROTECTED_PATH_AMBIGUOUS_001` | Packet names broad path such as repo root or `.`. | `status=BLOCKED`, `blocked_reasons` includes unbounded path scope. |

## 7. Approval-Required Test Cases

| Test ID | Input Condition | Expected Result |
|---|---|---|
| `APPROVAL_NOT_REQUIRED_REPORT_001` | Report-only output inside allowed path, no protected action. | `approval_required=false`, `approval_status=NOT_REQUIRED`. |
| `APPROVAL_REQUIRED_QUEUE_WRITE_001` | Packet asks to write canonical work packet under `automation/orchestration/work_packets/`. | `approval_required=true`, `approval_status=REQUIRED`, no queue file written. |
| `APPROVAL_REQUIRED_APPROVAL_WRITE_001` | Packet asks to write to `automation/orchestration/approval_inbox/`. | `approval_required=true`, `approval_status=REQUIRED`, no approval file written. |
| `APPROVAL_REQUIRED_GIT_ADD_001` | Packet asks to stage exact files. | `protected_action_requested=true`, `protected_action_type=GIT_ADD`, `approval_status=REQUIRED`. |
| `APPROVAL_REQUIRED_COMMIT_001` | Packet asks to commit exact files and provides message. | `protected_action_requested=true`, `protected_action_type=GIT_COMMIT`, commit gate required; adapter must not approve. |
| `APPROVAL_REQUIRED_PUSH_001` | Packet asks to push. | `protected_action_requested=true`, `protected_action_type=GIT_PUSH`, push gate required; adapter must not approve. |
| `APPROVAL_BLOCKED_GIT_ADD_DOT_001` | Packet asks to run `git add .`. | `status=BLOCKED` unless separately approved after cached diff review; adapter must not pass. |

## 8. Validator-Chain Test Cases

| Test ID | Input Condition | Expected Result |
|---|---|---|
| `VALIDATOR_CHAIN_COMPLETE_001` | Validator chain includes authority reads, state confirmation, exact output creation, `git diff --check`, and final `git status --short --branch`. | `validator_status=PASSED` for completeness check. |
| `VALIDATOR_CHAIN_NO_AUTHORITY_READ_001` | Missing `AGENTS.md` or `README.md` read step. | `status=BLOCKED`, `missing_fields` includes required authority read. |
| `VALIDATOR_CHAIN_NO_STATE_001` | Missing branch/worktree state confirmation. | `status=BLOCKED`, `missing_fields` includes preflight/state confirmation. |
| `VALIDATOR_CHAIN_NO_DIFF_CHECK_001` | File-writing packet lacks `git diff --check`. | `status=BLOCKED`, `missing_fields` includes whitespace diff validation. |
| `VALIDATOR_CHAIN_NO_FINAL_STATUS_001` | Missing final `git status --short --branch`. | `status=BLOCKED`, `missing_fields` includes final status validation. |
| `VALIDATOR_CHAIN_IRRELEVANT_VALIDATOR_001` | Validator chain lists broad or unrelated validators instead of scoped validation. | `status=BLOCKED` or `validator_status=PARTIAL`; missing scoped validator evidence recorded. |
| `VALIDATOR_CHAIN_PASS_NOT_APPROVAL_001` | Validator chain passes but packet requests commit. | `status=NEEDS_APPROVAL`, validator PASS remains evidence only. |

## 9. Placeholder Detection Test Cases

| Test ID | Placeholder Input | Expected Result |
|---|---|---|
| `PLACEHOLDER_AT_FILENAME_001` | `@filename` | `status=BLOCKED`, placeholder finding recorded. |
| `PLACEHOLDER_PATH_TO_FILE_001` | `path/to/file` | `status=BLOCKED`, placeholder finding recorded. |
| `PLACEHOLDER_REAL_FILENAME_001` | `[REAL-FILENAME]` | `status=BLOCKED`, placeholder finding recorded. |
| `PLACEHOLDER_BRACED_FEATURE_001` | `{feature}` | `status=BLOCKED`, placeholder finding recorded. |
| `PLACEHOLDER_TODO_001` | `TODO` | `status=BLOCKED`, placeholder finding recorded. |
| `PLACEHOLDER_TBD_001` | `TBD` | `status=BLOCKED`, placeholder finding recorded. |
| `PLACEHOLDER_EXAMPLE_PATH_001` | example path used as real target | `status=BLOCKED`, placeholder or unresolved path finding recorded. |
| `PLACEHOLDER_IN_PACKET_ID_001` | packet ID contains placeholder or generic value | `status=BLOCKED`, missing/placeholder packet ID finding recorded. |

## 10. Secret/Redaction Test Cases

| Test ID | Input Condition | Expected Result |
|---|---|---|
| `SECRET_PRINT_KEY_001` | Packet asks to print API key, token, password, private key, seed phrase, or broker credential. | `status=BLOCKED`, `redaction_status=SECRET_RISK_BLOCKED`. |
| `SECRET_CHECK_PRESENCE_001` | Packet asks only to report whether a credential exists without printing value. | Allowed only if separately scoped; output must redact values and set presence-only evidence. |
| `SECRET_EXTERNAL_TRANSMISSION_001` | Packet sends private repo evidence or secrets to external API. | `status=BLOCKED` unless separately approved with redaction; `external_transmission=true`. |
| `SECRET_ENV_DUMP_001` | Packet asks to dump environment variables. | `status=BLOCKED`, secret risk. |
| `SECRET_BROKER_ACCOUNT_001` | Packet references broker account credentials or live trading API keys. | `status=BLOCKED`, broker/API and secret risk. |
| `SECRET_REDACTED_EVIDENCE_001` | Input contains known placeholder secret value already redacted. | `redaction_status=REDACTED`, no plaintext secret exposure, still verify no execution risk. |

## 11. Executable=False Verification Tests

| Test ID | Input Condition | Expected Result |
|---|---|---|
| `EXEC_FALSE_PASS_001` | Valid packet preview. | `executable=false`. |
| `EXEC_FALSE_FAIL_001` | Invalid packet. | `executable=false`; no work packet preview accepted. |
| `EXEC_FALSE_APPROVAL_001` | Packet requires approval. | `executable=false`; `approval_required=true`. |
| `EXEC_FALSE_VALIDATOR_PASS_001` | Validator completeness check passes. | `executable=false`; validator PASS does not enable execution. |
| `EXEC_FALSE_QUEUE_PREVIEW_001` | Work packet preview generated. | `executable=false`; `preview_only=true`; no queue write. |
| `EXEC_FALSE_NO_OVERRIDE_001` | Input packet says adapter may execute automatically. | `status=BLOCKED` or `risk_flags` includes unauthorized execution; output remains `executable=false`. |

## 12. Canonical Envelope Verification Tests

| Test ID | Required Envelope Verification | Expected Result |
|---|---|---|
| `ENVELOPE_REQUIRED_FIELDS_001` | Envelope contains schema, event ID, UTC timestamp, source party, adapter name, packet ID, lane, mode, repo root, branch, worktree, status, approval, protected action, redaction, executable, and next safe action fields. | Pass only if all fields present. |
| `ENVELOPE_STATUS_VOCAB_001` | Status uses approved vocabulary from mapping and evidence contract. | Pass only for approved status values. |
| `ENVELOPE_BLOCKED_REASONS_001` | Blocked packet includes non-empty blocked reasons. | Pass only when blocked reasons explain the stop. |
| `ENVELOPE_RISK_FLAGS_001` | Risky packet includes relevant risk flags. | Pass only when risk flags match the input. |
| `ENVELOPE_SOURCE_PROVENANCE_001` | Envelope records source party and packet identity. | Pass only when provenance is preserved. |
| `ENVELOPE_NO_AUTHORITY_CREATION_001` | Envelope identifies canonical owners without creating new authority. | Pass only when queue/approval/workers/validators/commit owners are existing orchestration owners. |
| `ENVELOPE_EXECUTABLE_FALSE_001` | Envelope always includes `executable=false`. | Pass only when false for PASS, FAIL, and approval-needed cases. |

## 13. Work Packet Preview Verification Tests

| Test ID | Required Preview Verification | Expected Result |
|---|---|---|
| `PREVIEW_PRESENT_FOR_VALID_001` | Valid packet emits work packet preview. | Preview present and marked `preview_only=true`. |
| `PREVIEW_ABSENT_FOR_BLOCKED_001` | Blocked packet does not emit accepted work packet preview. | Preview absent or explicitly invalid. |
| `PREVIEW_CANONICAL_OWNERS_001` | Preview names existing canonical orchestration owners. | Queue owner is `automation/orchestration/work_packets/`; approval owner is `automation/orchestration/approval_inbox/`. |
| `PREVIEW_ALLOWED_PATHS_001` | Preview preserves exact allowed paths. | Allowed paths match input and are bounded. |
| `PREVIEW_FORBIDDEN_PATHS_001` | Preview preserves exact forbidden/protected paths. | Protected paths remain forbidden unless separately scoped and approved. |
| `PREVIEW_VALIDATOR_CHAIN_001` | Preview preserves validator chain. | Validator chain present and scoped. |
| `PREVIEW_STOP_POINT_001` | Preview preserves stop point. | Stop point present and exact. |
| `PREVIEW_NO_QUEUE_WRITE_001` | Adapter preview does not create queue file. | No write to `automation/orchestration/work_packets/`. |

## 14. Evidence Output Verification Tests

| Test ID | Required Evidence Verification | Expected Result |
|---|---|---|
| `EVIDENCE_SCHEMA_001` | Evidence uses `AIOS_CLI_EVIDENCE.v1`-compatible fields. | Required evidence fields present. |
| `EVIDENCE_REPO_STATE_001` | Evidence includes repo root, branch, worktree, git status, and dirty state classification. | Current state recorded without inventing clean/synced state. |
| `EVIDENCE_READ_PATHS_001` | Evidence includes authority/report files read. | Read paths list required authority files. |
| `EVIDENCE_WRITE_PATHS_001` | Evidence includes output paths for report-only work or empty write paths for pure preview. | Output paths accurate; no protected writes. |
| `EVIDENCE_APPROVAL_001` | Evidence includes approval requirement and approval status. | Approval state matches test input. |
| `EVIDENCE_PROTECTED_ACTION_001` | Evidence includes protected action fields. | Protected action type and decision match input. |
| `EVIDENCE_REDACTION_001` | Evidence includes redaction and secret scan fields. | Secret-safe status recorded. |
| `EVIDENCE_ALERT_001` | Evidence distinguishes display alert from SOS wake. | `sos_wake_required=true` only for blocked continuation or protected approval. |
| `EVIDENCE_NEXT_ACTION_001` | Evidence includes one exact next safe action. | Next action is specific and safe. |

## 15. Minimum Acceptance Threshold

The adapter must not be implemented beyond preview-only behavior until these thresholds are met:

1. All required-output-field checks pass for every test case.
2. All PASS cases produce `status=PREVIEW`.
3. All valid previews produce `executable=false`.
4. All blocked cases produce `status=BLOCKED`.
5. All blocked cases include exact `blocked_reasons`.
6. All missing-field cases identify every missing required field.
7. All placeholder cases fail closed.
8. All branch/worktree mismatch cases fail closed with the correct mismatch label when applicable.
9. All protected-path cases fail closed unless separately scoped and approved.
10. All protected-action cases require approval and do not self-approve.
11. All validator-chain cases preserve the rule that validator PASS is evidence only.
12. All secret/redaction cases block plaintext secret exposure.
13. All envelope tests prove required canonical envelope fields are present.
14. All work packet preview tests prove preview-only output and no queue writes.
15. All evidence tests prove `AIOS_CLI_EVIDENCE.v1` compatibility.
16. Zero tests may set `executable=true`.
17. Zero tests may create files outside the approved report output during the test-spec phase.
18. Zero tests may write queues, approvals, scripts, schemas, adapters, source files, broker paths, live trading paths, or secrets.

Minimum implementation gate:

```text
Implementation may begin only after a future DRY_RUN validation pass shows 100% pass rate for required PASS tests, 100% expected-block behavior for FAIL tests, and zero executable=true outputs.
```

## Future Implementation Boundary

Future acceptance tests may be converted into executable tests only by a separate approved APPLY packet that names exact implementation paths, test paths, validators, allowed paths, forbidden paths, and stop point.

Future executable tests must remain:

- local-only.
- preview-only by default.
- no queue writes unless explicitly approved.
- no approval writes unless explicitly approved.
- no protected actions.
- no OpenAI API calls.
- no MCP writes.
- no Codex recursive execution.
- no broker/API paths.
- no live trading paths.
- no secrets.

## Final Recommendation

Use this acceptance-test suite as the required proof gate before any `ChatGptToOrchestrationAdapter` implementation begins. The first implementation should prove packet validation, failure classification, canonical envelope output, work packet preview output, evidence output, and `executable=false` behavior before touching any canonical queue or approval path.

Next safe action:

```text
Review this acceptance-test report, then create a separate preview-only implementation packet if the mapping and test suite are accepted.
```
