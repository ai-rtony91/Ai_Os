# ChatGPT To Orchestration Adapter Implementation Plan

Packet: CHATGPT_TO_ORCHESTRATION_ADAPTER_IMPLEMENTATION_PLAN_001
Mode: DRY_RUN report output
Lane: CHATGPT_ADAPTER_IMPLEMENTATION_PLAN
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os

## Purpose

Define the exact future implementation path for `ChatGptToOrchestrationAdapter` without creating code, scripts, schemas, tests, queues, approvals, automation, or a new bridge head.

This report is the final planning gate before a separately approved APPLY packet may scaffold the first preview-only adapter.

## Source Authority Read

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md`
- `Reports/bridge_audit/CANONICAL_HARNESS_SELECTION.md`
- `Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md`
- `Reports/bridge_audit/FIRST_ADAPTER_SELECTION.md`
- `Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_MAPPING.md`
- `Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ACCEPTANCE_TESTS.md`
- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`

## Implementation Decision

Build a preview-only Python adapter inside the existing canonical orchestration tree:

```text
automation/orchestration/adapters/chatgpt_to_orchestration/
```

This path is an adapter package under the existing AI_OS Orchestration Harness. It is not a new bridge, queue, approval authority, runtime, service, daemon, or execution head.

The first code scaffold must:

- parse one packet text file or stdin input.
- validate packet completeness against `AGENTS.md`-derived required fields.
- classify missing fields, placeholders, branch/worktree mismatch, protected actions, approval need, forbidden paths, secret risk, broker/live trading risk, and duplicate authority risk.
- emit a canonical envelope preview.
- emit a canonical work packet preview object.
- emit `AIOS_CLI_EVIDENCE.v1`-compatible evidence.
- set `executable=false` for every output.
- write output only to an approved report/evidence path when explicitly scoped.
- never write canonical queues or approvals in v1.

## 1. Exact Source Files To Create Later

Future APPLY may create these source files only after explicit approval:

```text
automation/orchestration/adapters/chatgpt_to_orchestration/__init__.py
automation/orchestration/adapters/chatgpt_to_orchestration/models.py
automation/orchestration/adapters/chatgpt_to_orchestration/parser.py
automation/orchestration/adapters/chatgpt_to_orchestration/validator.py
automation/orchestration/adapters/chatgpt_to_orchestration/classifier.py
automation/orchestration/adapters/chatgpt_to_orchestration/envelope.py
automation/orchestration/adapters/chatgpt_to_orchestration/work_packet_preview.py
automation/orchestration/adapters/chatgpt_to_orchestration/evidence.py
automation/orchestration/adapters/chatgpt_to_orchestration/cli.py
```

Do not create:

- `automation/orchestration/harness/chatgpt_codex/` as a new harness head.
- `tools/bridge/` implementation.
- background services.
- schedulers.
- queue writers.
- approval writers.
- OpenAI/API clients.
- MCP write tools.
- Codex launchers.

## 2. Exact Test Files To Create Later

Future APPLY may create these test files only after explicit approval:

```text
tests/orchestration/adapters/test_chatgpt_to_orchestration_parser.py
tests/orchestration/adapters/test_chatgpt_to_orchestration_validator.py
tests/orchestration/adapters/test_chatgpt_to_orchestration_classifier.py
tests/orchestration/adapters/test_chatgpt_to_orchestration_envelope.py
tests/orchestration/adapters/test_chatgpt_to_orchestration_work_packet_preview.py
tests/orchestration/adapters/test_chatgpt_to_orchestration_evidence.py
tests/orchestration/adapters/test_chatgpt_to_orchestration_cli.py
```

Test fixtures may be created later under:

```text
tests/fixtures/chatgpt_to_orchestration/pass_report_only_packet.txt
tests/fixtures/chatgpt_to_orchestration/fail_missing_token_packet.txt
tests/fixtures/chatgpt_to_orchestration/fail_branch_mismatch_packet.txt
tests/fixtures/chatgpt_to_orchestration/fail_placeholder_packet.txt
tests/fixtures/chatgpt_to_orchestration/fail_secret_risk_packet.txt
```

No executable test files or fixtures are created by this report.

## 3. Exact Schema Files If Needed Later

Schema files are optional for the first scaffold. The first implementation can use typed Python dictionaries/dataclasses and tests.

If schema files become necessary later, create only through a separate schema-scoped APPLY packet:

```text
schemas/aios/orchestration/chatgpt_to_orchestration_envelope.schema.json
schemas/aios/orchestration/chatgpt_to_orchestration_work_packet_preview.schema.json
schemas/aios/orchestration/chatgpt_to_orchestration_evidence.schema.json
```

Schema creation must not precede the first preview-only adapter unless the implementation packet explicitly justifies why runtime validation needs JSON schemas immediately.

## 4. Function And Module Responsibilities

| Module | Responsibility | Must Not Do |
|---|---|---|
| `models.py` | Define in-memory result structures for parsed packet, validation result, classification result, envelope preview, work packet preview, and evidence output. | No file writes, queue writes, approvals, subprocess calls, API calls. |
| `parser.py` | Parse packet text into sections and raw fields while preserving source text and line positions. | No validation authority beyond parse defects. |
| `validator.py` | Validate required markers, identity fields, validation fields, branch/worktree evidence, allowed/forbidden paths, stop point, and final report format. | No approval decisions, no filesystem mutation. |
| `classifier.py` | Classify failure classes, protected actions, approval requirement, dirty state, placeholder findings, duplicate authority risk, secret risk, and broker/live trading risk. | No protected action execution, no approval creation. |
| `envelope.py` | Build `AIOS_CHATGPT_TO_ORCHESTRATION_ENVELOPE.v1` preview object with `executable=false`. | No schema file creation, no queue writes. |
| `work_packet_preview.py` | Build `AIOS_CANONICAL_WORK_PACKET_PREVIEW.v1` preview object for valid packets; leave absent/invalid for blocked packets. | No write to `automation/orchestration/work_packets/`. |
| `evidence.py` | Build `AIOS_CLI_EVIDENCE.v1`-compatible evidence object. | No telemetry writes unless separately scoped. |
| `cli.py` | Provide local preview command entrypoint that reads packet text, optional observed state fields, and prints/writes preview output only to approved path. | No Codex launch, no OpenAI call, no queue write, no approval write, no commit/push. |

## 5. Input Packet Parser Design

Parser input:

```text
raw_packet_text: string
observed_repo_state: optional structured evidence
```

Parser output:

```text
ParsedPacket:
  raw_text
  first_line
  markers
  sections
  line_index
  parse_warnings
```

Parsing rules:

1. Preserve the exact first line.
2. Treat uppercase section headers ending in `:` as field names.
3. Preserve multi-line field values.
4. Keep raw text for placeholder, protected-action, and secret-risk scans.
5. Do not normalize away path spelling.
6. Do not infer missing fields.
7. Do not execute embedded commands.
8. Do not treat example packets as executable unless the adapter input is explicitly the packet under test.

Required parsed sections:

- `IDENTITY MARKER`
- `SUPERVISOR IDENTITY`
- `PACKET ID`
- `LANE`
- `ZONE`
- `WORKER IDENTITY`
- `MODE`
- `BRANCH`
- `WORKTREE`
- `APPROVAL AUTHORITY`
- `ALLOWED PATHS`
- `PROTECTED PATHS` or `FORBIDDEN PATHS`
- `VALIDATOR CHAIN`
- `MISSION`
- `STOP POINT`
- `FINAL RESPONSE FORMAT`

## 6. Validation Rule Design

Validation must be fail-closed.

Required marker validation:

| Rule | Failure |
|---|---|
| first line exactly `CODEX-ONLY PROMPT` | `MISSING_ROUTING_MARKER` |
| contains `AI_OS EXECUTION TOKEN` | `MISSING_EXECUTION_TOKEN` |
| contains `AI_OS BOOTSTRAP REQUIRED` | `MISSING_BOOTSTRAP` |

Required field validation:

| Field Group | Required Fields |
|---|---|
| identity | identity marker, supervisor identity, packet ID, lane, zone, worker identity |
| execution scope | mode, branch, worktree, approval authority |
| file scope | allowed paths, forbidden/protected paths |
| safety | validator chain, mission, stop point, final report format |
| state | observed path, branch, status, remote when repo work matters |

Path validation:

- allowed paths must be exact and bounded.
- forbidden/protected paths must be present for adapter work.
- `C:\Dev\Ai.Os` is the active worktree.
- legacy inactive paths fail.
- broad repo root writes fail.
- placeholders fail.

State validation:

- declared branch must match observed branch unless `resolve after preflight`.
- the adapter must not switch branches.
- dirty state must be reported, not fixed.
- overlapping dirty mission state blocks if unsafe to classify.

## 7. Canonical Envelope Preview Design

Envelope object:

```text
schema: AIOS_CHATGPT_TO_ORCHESTRATION_ENVELOPE.v1
event_id
created_at_utc
source_party: ChatGPT
adapter_name: ChatGptToOrchestrationAdapter
source_input_type: CHATGPT_PACKET_TEXT
source_hash
packet_id
lane
zone
mode
identity_marker
supervisor_identity
worker_identity
approval_authority
repo_root
worktree
branch_declared
branch_observed
git_status_short_branch
dirty_state_class
allowed_paths
forbidden_paths
read_first_authority_files
validator_chain
mission
stop_point
final_report_format
status
status_impact
blocked_reasons
risk_flags
missing_fields
placeholder_findings
branch_worktree_validation
approval_required
approval_status
protected_action_requested
protected_action_type
redaction_status
paper_only
executable: false
canonical_work_packet_preview
evidence_output
display_alert
sos_wake_required
wake_class
next_safe_action
```

Envelope status logic:

| Condition | Status |
|---|---|
| complete, safe preview | `PREVIEW` |
| missing field, placeholder, mismatch, forbidden path, duplicate authority, secret, broker/live risk | `BLOCKED` |
| scoped protected action or queue/approval write intent | `NEEDS_APPROVAL` unless unsafe, then `BLOCKED` |
| parser/tool failure | `FAILED` |

## 8. Work Packet Preview Design

Work packet preview object:

```text
schema: AIOS_CANONICAL_WORK_PACKET_PREVIEW.v1
packet_id
origin: CHATGPT_GENERATED_PACKET
adapter_name: ChatGptToOrchestrationAdapter
canonical_harness_owner: AI_OS Orchestration Harness
queue_owner: automation/orchestration/work_packets/
approval_owner: automation/orchestration/approval_inbox/
worker_owner: automation/orchestration/workers/
validator_owner: automation/orchestration/validators/
commit_package_owner: automation/orchestration/commit_packages/
lane
zone
mode
branch
worktree
allowed_paths
forbidden_paths
read_first_authority_files
validator_chain
mission
task_summary
strict_rules
stop_point
approval_classification
protected_action_classification
state_alignment
evidence_contract: AIOS_CLI_EVIDENCE.v1-compatible
executable: false
preview_only: true
```

Preview generation rules:

- present for valid `PREVIEW` and scoped `NEEDS_APPROVAL` outputs.
- absent or explicitly invalid for `BLOCKED` and `FAILED` outputs.
- never written to `automation/orchestration/work_packets/` in v1.
- preview path may be shown as a future convention only.

## 9. Evidence Output Design

Evidence object must follow `AIOS_CLI_EVIDENCE.v1` vocabulary:

```text
schema: AIOS_CLI_EVIDENCE.v1
event_id
created_at_utc
source_party: ChatGPT
source_command: ChatGptToOrchestrationAdapter validate packet
packet_id
lane
mode
repo_root
branch
worktree
git_status_short_branch
dirty_state_class
allowed_paths
forbidden_paths
read_paths
write_paths
output_paths
status
status_impact
blocked_reasons
risk_flags
validator_chain
validator_results
approval_required
approval_status
approval_authority
protected_action_requested
protected_action_type
display_alert
sos_wake_required
wake_class
redaction_status
secret_scan_status
executable: false
next_safe_action
stop_point
```

Evidence rules:

- evidence is not approval.
- validator PASS is evidence only.
- `NEEDS_APPROVAL` is not automatically SOS.
- `sos_wake_required=true` only when continuation is blocked or a protected approval is required.
- no plaintext secrets may appear in evidence.

## 10. Failure-Class Handling

| Failure Class | Handler Behavior |
|---|---|
| `MISSING_ROUTING_MARKER` | Block, record missing first-line marker, no accepted preview. |
| `MISSING_EXECUTION_TOKEN` | Block executable-intent packet, record token defect. |
| `MISSING_BOOTSTRAP` | Block AI_OS-governed packet. |
| `MISSING_IDENTITY_FIELD` | Block and list every missing identity field. |
| `MISSING_VALIDATION_FIELD` | Block and list validator/preflight/final report/scope defects. |
| `PLACEHOLDER_PRESENT` | Block and list exact placeholder findings. |
| `FORBIDDEN_PATH_TARGETED` | Block unless separately scoped and approval-gated; never self-approve. |
| `DUPLICATE_AUTHORITY_RISK` | Block queue, approval, governance, or bridge-head duplication. |
| `STATE_MISMATCH` | Block with `AIOS-PROMPT-AUTH-STATE-MISMATCH`; report assumed and observed state. |
| `DIRTY_STATE_UNCLASSIFIED` | Block if dirty files overlap mission and cannot be safely classified. |
| `APPROVAL_MISSING` | Return `NEEDS_APPROVAL` only if scoped; otherwise block. |
| `PROTECTED_ACTION_UNSCOPED` | Block unscoped protected actions. |
| `SECRET_OR_CREDENTIAL_RISK` | Block and redact. |
| `BROKER_OR_LIVE_TRADING_RISK` | Block and set SOS evidence. |
| `UNAUTHORIZED_AUTOMATION` | Block persistent runner, scheduler, daemon, or autonomous loop creation. |

## 11. Acceptance-Test Mapping

| Acceptance Area | Future Test File |
|---|---|
| PASS and FAIL packet handling | `tests/orchestration/adapters/test_chatgpt_to_orchestration_validator.py` |
| missing-field cases | `tests/orchestration/adapters/test_chatgpt_to_orchestration_validator.py` |
| branch/worktree mismatch | `tests/orchestration/adapters/test_chatgpt_to_orchestration_classifier.py` |
| protected-path cases | `tests/orchestration/adapters/test_chatgpt_to_orchestration_classifier.py` |
| approval-required cases | `tests/orchestration/adapters/test_chatgpt_to_orchestration_classifier.py` |
| validator-chain cases | `tests/orchestration/adapters/test_chatgpt_to_orchestration_validator.py` |
| placeholder detection | `tests/orchestration/adapters/test_chatgpt_to_orchestration_parser.py` and `classifier.py` tests |
| secret/redaction cases | `tests/orchestration/adapters/test_chatgpt_to_orchestration_classifier.py` and `evidence.py` tests |
| `executable=false` invariant | all adapter tests plus `test_chatgpt_to_orchestration_envelope.py` |
| canonical envelope verification | `tests/orchestration/adapters/test_chatgpt_to_orchestration_envelope.py` |
| work packet preview verification | `tests/orchestration/adapters/test_chatgpt_to_orchestration_work_packet_preview.py` |
| evidence output verification | `tests/orchestration/adapters/test_chatgpt_to_orchestration_evidence.py` |
| CLI command shape | `tests/orchestration/adapters/test_chatgpt_to_orchestration_cli.py` |

Minimum test gate:

```text
100% required PASS cases pass.
100% required FAIL cases fail closed as expected.
0 outputs set executable=true.
0 tests write queues or approvals.
0 tests call OpenAI, MCP, Codex, broker/API, or live trading paths.
```

## 12. CLI Command Shape For Future Use

Future command shape:

```powershell
python -m automation.orchestration.adapters.chatgpt_to_orchestration.cli `
  --input-packet <packet.txt> `
  --repo-root C:\Dev\Ai.Os `
  --branch <observed-branch> `
  --git-status-file <optional-status.txt> `
  --mode DRY_RUN `
  --output-json <approved-output-path>
```

Initial allowed output path for a scaffold packet should be under:

```text
Reports/bridge_audit/
```

Future telemetry output may be considered only by a separate approval packet:

```text
telemetry/chatgpt_to_orchestration/
```

CLI behavior:

- reads one packet.
- accepts observed state as explicit input or collects read-only state only when scoped.
- prints JSON preview to stdout by default.
- writes output only when `--output-json` is inside an approved allowed path.
- never writes queues or approvals.
- never launches Codex.
- never calls OpenAI.
- never performs protected repo actions.

## 13. No-Write DRY_RUN Behavior

Default DRY_RUN behavior:

```text
input packet text
-> parse
-> validate
-> classify
-> build envelope preview
-> build work packet preview when valid
-> build evidence output
-> print preview
-> stop
```

No-write guarantees:

- no queue files.
- no approval files.
- no schema files.
- no telemetry files unless separately approved.
- no source mutation.
- no shell command execution from packet body.
- no provider dispatch.
- no commit/push/merge/PR actions.
- no broker/API/live trading paths.
- no secrets.

## 14. Future APPLY Boundary

The first code APPLY packet may create only the source and test files named in this report.

First APPLY must not:

- write `automation/orchestration/work_packets/`.
- write `automation/orchestration/approval_inbox/`.
- write `automation/orchestration/workers/`.
- write `automation/orchestration/validators/` except tests may reference future validator concepts.
- write `automation/orchestration/commit_packages/`.
- create schema files unless separately approved.
- create telemetry output paths unless separately approved.
- create persistent automation.
- invoke Codex.
- call OpenAI.
- call MCP.
- stage, commit, push, merge, reset, clean, delete branches, or create PRs.

First APPLY validation should run:

```powershell
python -m pytest tests/orchestration/adapters/test_chatgpt_to_orchestration_parser.py tests/orchestration/adapters/test_chatgpt_to_orchestration_validator.py tests/orchestration/adapters/test_chatgpt_to_orchestration_classifier.py tests/orchestration/adapters/test_chatgpt_to_orchestration_envelope.py tests/orchestration/adapters/test_chatgpt_to_orchestration_work_packet_preview.py tests/orchestration/adapters/test_chatgpt_to_orchestration_evidence.py tests/orchestration/adapters/test_chatgpt_to_orchestration_cli.py
python -m py_compile automation/orchestration/adapters/chatgpt_to_orchestration/*.py
git diff --check
git status --short --branch
```

## 15. Risk Controls

| Risk | Control |
|---|---|
| duplicate harness head | Implement under `automation/orchestration/adapters/`, not a new harness or bridge path. |
| approval bypass | Always output approval evidence only; never write approval files or infer approval. |
| queue mutation | Preview only; no `automation/orchestration/work_packets/` writes in v1. |
| validator PASS misuse | Tests must prove validator PASS does not set `executable=true` or approve protected actions. |
| branch/worktree mismatch | Fail closed with `AIOS-PROMPT-AUTH-STATE-MISMATCH`. |
| dirty worktree confusion | Record observed dirty state; never revert or clean. |
| protected path edit | Block unless separately scoped and approval-gated. |
| placeholder execution | Fail closed on unresolved placeholders. |
| secret leakage | Redact or block; no environment dumps or plaintext secret output. |
| broker/live trading drift | Block live broker/API/real order paths. |
| recursive Codex launch | No subprocess/provider dispatch in adapter v1. |
| OpenAI/API sprawl | No external API calls in adapter v1. |
| report authority creep | Treat reports as planning/evidence, not source authority unless promoted later. |

## 16. Exact Next APPLY Packet For First Code Scaffold

Use this packet only if Anthony approves moving from report planning to code scaffold.

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
Anthony / AI_OS Owner

PACKET ID:
CHATGPT_TO_ORCHESTRATION_ADAPTER_SCAFFOLD_APPLY_001

LANE:
CHATGPT_ADAPTER_SCAFFOLD

ZONE:
AI_OS Adapter Implementation

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
Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_MAPPING.md
Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ACCEPTANCE_TESTS.md
Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_IMPLEMENTATION_PLAN.md
Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md

ALLOWED PATHS:
automation/orchestration/adapters/chatgpt_to_orchestration/
tests/orchestration/adapters/
tests/fixtures/chatgpt_to_orchestration/

FORBIDDEN PATHS:
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
Create the first preview-only ChatGptToOrchestrationAdapter scaffold and tests. The adapter must parse packet text, validate required fields, classify failures, produce a canonical envelope preview, produce a work packet preview, produce AIOS_CLI_EVIDENCE.v1-compatible evidence, and keep executable=false for every output.

TASK:
Create only the source and test files named in Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_IMPLEMENTATION_PLAN.md. Do not create schemas, queues, approvals, telemetry, scripts, services, bridge heads, or automation loops.

VALIDATOR CHAIN:
1. Read AGENTS.md.
2. Read README.md.
3. Read WHITEPAPER.md.
4. Read Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_MAPPING.md.
5. Read Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ACCEPTANCE_TESTS.md.
6. Read Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_IMPLEMENTATION_PLAN.md.
7. Confirm path, branch, status, and remote.
8. Create only approved source/test/fixture files.
9. Run python -m py_compile on adapter source files.
10. Run pytest for the adapter test files.
11. Run git diff --check.
12. Run git status --short --branch.

STRICT RULES:
- Preview-only adapter.
- executable=false for every output.
- No queue writes.
- No approval writes.
- No schema creation.
- No telemetry writes.
- No scripts.
- No OpenAI calls.
- No MCP calls.
- No Codex launch.
- No subprocess/provider dispatch.
- No commit.
- No push.
- No live trading paths.
- No broker paths.
- No secrets.
- Do not switch branches.

STOP POINT:
Stop after scaffold creation, tests, diff check, and status report. No commit. No push.

FINAL RESPONSE FORMAT:
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS:
```

## Final Recommendation

Proceed to code only with the scaffold packet above. The implementation should be deliberately narrow: a local preview-only adapter that validates ChatGPT packet text and emits structured previews/evidence, while leaving canonical queue writes, approval writes, schemas, telemetry, provider dispatch, OpenAI, MCP, Codex launch, and protected actions for later separately approved packets.

Next safe action:

```text
Review this implementation plan, then approve or revise the exact scaffold APPLY packet before any code is created.
```
