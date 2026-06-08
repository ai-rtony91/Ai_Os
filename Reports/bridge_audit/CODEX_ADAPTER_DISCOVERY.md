# Codex Adapter Discovery

## Packet

- Packet ID: `CODEX_ADAPTER_DISCOVERY_001`
- Lane: `CODEX_ADAPTER_DISCOVERY`
- Mode: `DRY_RUN`
- Worktree: `C:\Dev\Ai.Os`
- Branch: `feature/full-operator-relief-closed-loop-v1`
- Report date: 2026-06-07

## Scope

This discovery determines how Codex should connect to the canonical AI_OS Orchestration Harness after `ChatGptToOrchestrationAdapter`.

Canonical harness spine remains:

```text
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
```

This report creates no code, tests, adapters, schemas, queues, approvals, automation, source edits, commits, pushes, broker paths, live trading paths, or secrets.

## Authority And Evidence Read

Required files read:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md`
- `Reports/bridge_audit/CANONICAL_HARNESS_SELECTION.md`
- `Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md`
- `Reports/bridge_audit/FIRST_ADAPTER_SELECTION.md`
- `Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_PROOF.md`

Additional targeted evidence read:

- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`
- `Reports/cli_everything/CLI_EVERYTHING_PARTY_BRIDGE_INVESTIGATION.md`
- `docs/workflows/WORKER_OUTPUT_INTERFACE_STANDARD.md`
- `docs/workflows/CODEX_OPENAI_CLI_PACKET_TEMPLATE.md`
- `docs/governance/operational-doctrine.md`
- `docs/governance/aios-identity-and-lane-governance.md`
- `automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1`
- `automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1`
- `automation/orchestration/validators/output/Test-AiOsWorkerOutput.DRY_RUN.ps1`
- `Relay/README.md`
- `Relay/LEGACY_CLI_RELAY_README.md`
- `Relay/outbox/example-codex-result.result.json`
- `automation/operator_relief/cli_bridge.py`
- `automation/operator_relief/dual_review_bridge.py`

## Current Branch And Worktree State

Observed branch:

```text
feature/full-operator-relief-closed-loop-v1
```

Observed worktree:

```text
C:\Dev\Ai.Os
```

Observed status before this report:

```text
## feature/full-operator-relief-closed-loop-v1...origin/feature/full-operator-relief-closed-loop-v1 [ahead 3]
 M scripts/backup/Start-AiOsT9SnapshotBackup.ps1
?? Reports/backup/
?? Reports/bridge_audit/
?? Reports/cli_everything/
?? automation/orchestration/adapters/chatgpt_to_orchestration/
?? tests/fixtures/
?? tests/orchestration/
```

The branch matches the packet. Dirty state is existing work on the same feature branch. This discovery creates only this report under `Reports/bridge_audit/`.

## Existing Codex Touchpoints

| Touchpoint | Path | Current Role | Discovery Finding |
|---|---|---|---|
| Packet law and Codex execution gate | `AGENTS.md` | Canonical authority | Defines Codex prompt marker, execution token, identity fields, approval gates, protected actions, stop points, and final report rules. |
| Tool routing doctrine | `docs/governance/operational-doctrine.md` | Canonical routing role map | Defines Codex East as bounded repo executor and explicitly blocks self-promotion into protected-action authority. |
| Identity and lane governance | `docs/governance/aios-identity-and-lane-governance.md` | Canonical identity/routing authority | Defines Codex East, temporary worker identity, lane, lock, approval, validator, and stop-point requirements. |
| Worker output interface | `docs/workflows/WORKER_OUTPUT_INTERFACE_STANDARD.md` | Canonical workflow | Defines Codex-to-ChatGPT SITREP concept and required output elements for final reports/handoffs. |
| Codex packet template | `docs/workflows/CODEX_OPENAI_CLI_PACKET_TEMPLATE.md` | Usage artifact | Provides Codex-ready packet shape but remains subordinate to `AGENTS.md`. |
| Codex handoff generator | `automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1` | DRY_RUN handoff helper | Generates a read-only paste-ready Codex prompt, status, validator recommendation, and commit package recommendation. It does not execute Codex. |
| Relay worker | `automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1` | Provider-neutral relay dispatch | Contains a `codex` provider default of `codex exec --sandbox workspace-write -`, but only dispatches under `-Apply`; TIER_2/protected work moves to Relay approvals first. |
| Relay README | `Relay/README.md` | Relay behavior documentation | Describes Relay as local file bridge with Codex as possible provider after command/auth/safety scoping. |
| Relay legacy notice | `Relay/LEGACY_CLI_RELAY_README.md` | Legacy/fallback boundary | Marks CLI Relay as fallback only; active path is packet queue -> worker assignment -> Codex/APPLY lane -> validator -> approval inbox -> commit package -> dashboard status. |
| Relay Codex result example | `Relay/outbox/example-codex-result.result.json` | Example evidence | Shows an old/simple Codex result shape with summary, files changed, validation, blockers, and next safe action. |
| Operator Relief CLI bridge | `automation/operator_relief/cli_bridge.py` | Non-executing handoff evidence | Discovers local Codex/OpenAI CLI availability and writes non-executable handoff records; blocks live execution token. |
| Operator Relief dual review bridge | `automation/operator_relief/dual_review_bridge.py` | Evidence/classification bridge | Accepts Codex report summary as input for authority-aware review evidence; does not launch workers or external reviewers. |
| CLI Everything evidence reports | `Reports/cli_everything/` | Evidence/report vocabulary | Defines `AIOS_CLI_EVIDENCE.v1` as shared evidence vocabulary, with Codex East as repo executor party. |
| ChatGPT adapter scaffold | `automation/orchestration/adapters/chatgpt_to_orchestration/` | First preview-only adapter | Produces canonical envelope, work packet preview, and evidence with `executable=false`; establishes pattern for adapter boundaries. |

## Existing Codex Reports

Existing report-like Codex artifacts found:

- `Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md`
- `Reports/cli_everything/CLI_EVERYTHING_PARTY_BRIDGE_INVESTIGATION.md`
- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`
- `Reports/operator_relief/openai_codex_cli_bridge_discovery/OPENAI_CODEX_CLI_BRIDGE_DISCOVERY.md`
- Operator Relief decision and human-review packets related to parallel Codex workflow.
- `Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_PROOF.md`, which proves the first adapter blocks Codex launch and queue/approval writes.

Report classification:

- Bridge-audit and CLI Everything reports are evidence only unless promoted by future authority-scoped packets.
- Operator Relief reports are evidence or decision artifacts, not the canonical Codex adapter.
- No current report defines a complete `OrchestrationToCodexAdapter` implementation contract.
- No current report defines a complete `CodexResultToEvidenceAdapter` implementation contract.

## Existing Codex Packet Flows

Current observed packet flows:

1. Manual tokenized packet flow:

```text
ChatGPT or Anthony provides complete Codex packet
-> Codex reads authority files
-> Codex confirms branch/worktree
-> Codex executes DRY_RUN/APPLY within allowed scope
-> Codex runs validators
-> Codex reports result in final response format
```

2. Handoff helper flow:

```text
automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1
-> reads current branch, dirty files, active packet, validator recommendation, commit-package recommendation
-> emits paste-ready Codex prompt and PowerShell command block
-> performs no git add, commit, push, or Codex launch
```

3. Relay provider flow:

```text
relay/inbox/*.task.json
-> automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1
-> provider=codex maps to codex exec --sandbox workspace-write -
-> -Apply required for real provider dispatch
-> TIER_2/protected work moves to relay/approvals before CLI dispatch
-> outbox report and done/error/approval state
```

4. Operator Relief CLI handoff flow:

```text
Operator Relief task/prompt text
-> automation/operator_relief/cli_bridge.py
-> CLI availability check
-> non-executable handoff record
-> no Codex invocation
```

5. ChatGPT-to-orchestration preview flow:

```text
ChatGPT packet text
-> ChatGptToOrchestrationAdapter
-> canonical envelope preview
-> canonical work packet preview
-> AIOS_CLI_EVIDENCE.v1-compatible evidence
-> executable=false
```

## Existing Codex Evidence Outputs

Current evidence output shapes:

| Evidence Shape | Source | Key Fields | Limitations |
|---|---|---|---|
| AI_OS terminal final response | Codex final message | Summary, files changed, validation, dirty files, next command, status | Human-readable, not machine-normalized. |
| Codex-to-ChatGPT SITREP concept | `WORKER_OUTPUT_INTERFACE_STANDARD.md` | Lane, worker role, branch, worktree, files read/changed, validation, commit/push/PR status, blockers, next safe action | Concept only; not implemented as a parser or receipt. |
| `AIOS_CLI_EVIDENCE.v1` | CLI Everything evidence contract and ChatGPT adapter evidence | Universal event/status/approval/validator/protected-action fields | Report-derived vocabulary; not yet promoted to schema authority. |
| Relay outbox report text | `Invoke-AiOsRelayWorker.ps1` | ID, worker, provider, provider command, tier, timing, exit code, allowed paths, stdout/stderr | Relay-specific and not canonical queue evidence. |
| Relay example result JSON | `Relay/outbox/example-codex-result.result.json` | packet=result, id, worker, status, files_changed, summary, validation, blockers, next_safe_action | Simple example; insufficient for canonical Codex result receipt. |
| Operator Relief CLI handoff record | `cli_bridge.py` | CLI availability, command preview, handoff path, reasons, prompt text, executable=false | Handoff evidence only, not execution evidence. |
| Authority bridge review | `dual_review_bridge.py` | Codex report summary, ChatGPT review summary, Claude review summary, protected paths, classification, executable=false | Review classifier, not Codex result normalizer. |

## Existing Codex Approval Dependencies

Codex approval dependencies are clear and must remain outside the adapter:

- `AGENTS.md` controls protected action gates.
- `docs/governance/operational-doctrine.md` confirms Human Owner final authority.
- `automation/orchestration/approval_inbox/` is the canonical approval owner.
- `Relay/approvals/` and `relay/approvals/` are fallback/historical evidence unless promoted.
- Operator Relief approval inputs are local evidence/input only.
- Validator PASS does not approve APPLY, commit, push, merge, PR actions, protected edits, secrets, broker/API, live trading, or production behavior.

The Codex adapter may classify and report approval status, but it must not create, approve, consume, or mutate approval records in V1.

## Existing Codex Validator Dependencies

Relevant validator dependencies:

- Packet validator requirements from `AGENTS.md`: authority read, branch/worktree state, allowed/protected paths, validator chain, stop point, final report format.
- `automation/orchestration/validators/output/Test-AiOsWorkerOutput.DRY_RUN.ps1`: checks files touched after a run against allowed paths and protected paths; emits pass, touched, violations, protected violations, and violation reason.
- `automation/orchestration/validators/Get-AiOsValidatorRecommendation.DRY_RUN.ps1`: consumed by Codex handoff generator for recommended validation command.
- `git diff --check`: required after file changes.
- `git status --short --branch`: required at stop point.
- Adapter pytest suite: currently proves `ChatGptToOrchestrationAdapter`, but does not validate Codex result normalization yet.

The Codex adapter should ingest validator command/results as evidence, not run arbitrary validators by itself in V1.

## Existing Codex Completion-Report Formats

Current formats:

1. `AGENTS.md` success format:

```text
SUMMARY:
WHAT CHANGED:
FILES CHANGED:
VALIDATION:
REMAINING DIRTY FILES:
SAFE NEXT COMMAND:
STATUS: COMPLETE, NO COMMIT, NO PUSH
```

2. `AGENTS.md` failure format:

```text
WHAT FAILED:
WHY IT FAILED:
WHAT NEEDS TO HAPPEN NEXT:
WHERE TO REFERENCE:
SAFE NEXT COMMAND OR PROMPT:
STATUS: BLOCKED or FAILED
```

3. `AGENTS.md` DRY_RUN format:

```text
SUMMARY:
WHAT WAS TESTED:
FINDINGS:
RECOMMENDATION:
SAFE NEXT COMMAND:
STATUS: DRY_RUN COMPLETE, NO FILES CHANGED
```

4. Worker output SITREP concept:

```text
Lane, worker role, branch, worktree, files read, files changed, validation result, mutation status, commit status, push status, PR status, blockers, next safe action, stop condition, screenshot need, authority stack, approval state, timestamp.
```

The future Codex adapter should parse or accept these fields explicitly and emit normalized evidence without treating the final report as approval.

## Existing Codex Handoff Paths

| Handoff Path | Status | Adapter Treatment |
|---|---|---|
| Human paste into Codex | Current primary path | Preserve as manual execution path; adapter can normalize results after Codex reports. |
| `automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1` | Active DRY_RUN helper | Candidate input for `OrchestrationToCodexAdapter` preview; no execution. |
| `Relay/handoffs/` and `relay/handoffs/` | Historical/fallback evidence | Candidate Relay adapter input; not canonical Codex adapter owner. |
| `Relay/outbox/` and `relay/outbox/` | Historical/fallback evidence | Candidate input for `CodexResultToEvidenceAdapter` only after source classification. |
| `automation/operator_relief/cli_bridge.py` handoff records | Operator Relief evidence | Candidate input for Operator Relief adapter; not Codex adapter owner. |
| `docs/workflows/CODEX_OPENAI_CLI_PACKET_TEMPLATE.md` | Template only | Useful input shape reference; not authority. |

## What Already Exists

Already exists:

- Codex packet law in `AGENTS.md`.
- Codex role definition in `operational-doctrine.md`.
- Codex identity/lane/stop-point rules in `aios-identity-and-lane-governance.md`.
- Worker output and Codex SITREP concept in `WORKER_OUTPUT_INTERFACE_STANDARD.md`.
- Manual Codex execution flow through tokenized packets.
- DRY_RUN Codex handoff generator.
- Relay provider dispatch that can target Codex under `-Apply`.
- Relay outbox and simple Codex result example.
- Operator Relief non-executing CLI handoff records.
- Shared evidence vocabulary in `AIOS_CLI_EVIDENCE.v1`.
- Proven `ChatGptToOrchestrationAdapter` preview scaffold.

## What Is Missing

Missing:

- A canonical `OrchestrationToCodexAdapter` contract.
- A canonical `CodexResultToEvidenceAdapter` contract.
- A normalized Codex result receipt schema/report.
- Parser for Codex final report formats.
- Explicit mapping from Codex final report fields to `AIOS_CLI_EVIDENCE.v1`.
- Guard that ensures Codex changed files remain inside allowed paths before evidence is marked complete.
- Guard that preserves commit/push/PR status as evidence only.
- Guard that prevents Relay outbox or Operator Relief handoff evidence from becoming canonical approval.
- Acceptance tests for Codex result normalization.
- Fixture set for PASS, FAIL, BLOCKED, validation failure, out-of-scope change, missing final report field, and protected action requested.
- Source import/call guard proving the Codex adapter does not launch Codex, shell, OpenAI, MCP, Relay, or provider dispatch.

## Candidate Codex Adapter Responsibilities

The Codex adapter should be split into two responsibilities:

### 1. OrchestrationToCodexAdapter

Purpose:
Convert a validated canonical work packet into a Codex handoff preview.

Inputs:

- Canonical work packet preview or approved work packet metadata.
- Branch/worktree state.
- Allowed paths.
- Forbidden/protected paths.
- Validator chain.
- Approval status.
- Stop point.
- Packet body or prompt text.

Outputs:

- Codex handoff preview.
- Paste-ready Codex prompt only when the packet is complete.
- `AIOS_CLI_EVIDENCE.v1`-compatible handoff evidence.
- `executable=false` unless a future separately approved execution lane changes that state.

Non-responsibilities:

- No Codex launch.
- No queue writes.
- No approval writes.
- No validator execution.
- No commit package mutation.
- No protected action execution.

### 2. CodexResultToEvidenceAdapter

Purpose:
Convert Codex final reports, Relay Codex outbox reports, or Codex-style result records into normalized evidence receipts.

Inputs:

- Codex final report text.
- Packet ID, lane, branch, worktree, allowed paths, forbidden paths.
- Changed file list.
- Validation command/result evidence.
- Commit/push/PR status.
- Approval state.
- Error or blocked condition text.

Outputs:

- `AIOS_CODEX_RESULT_RECEIPT.v1` preview.
- `AIOS_CLI_EVIDENCE.v1`-compatible evidence.
- Normalized fields for files read, files changed, validators, dirty state, commit status, push status, protected action status, blockers, and next safe action.
- `executable=false`.

Non-responsibilities:

- No approval inference.
- No commit/push/merge/PR action.
- No source modification.
- No Relay state movement.
- No telemetry write in V1.

## Exact Future Codex Adapter Scope

Future V1 scope should be:

- Report/spec first.
- Preview-only implementation second.
- Local text/JSON parsing only.
- Standard library only unless repo standards later approve otherwise.
- No provider dispatch.
- No subprocess.
- No OpenAI/MCP calls.
- No queue writes.
- No approval writes.
- No telemetry writes.
- No schemas until separately approved.
- No protected action execution.
- No live trading or broker/API paths.

Future V1 should accept:

- Codex final report text.
- Optional observed repo state object.
- Optional changed-file list supplied by caller.
- Optional validator result list supplied by caller.
- Optional source type: `manual_codex_final_report`, `relay_outbox_report`, `operator_relief_handoff_result`, or `codex_sitrep`.

Future V1 should produce:

- `AIOS_CODEX_RESULT_RECEIPT.v1` preview.
- `AIOS_CLI_EVIDENCE.v1` evidence preview.
- `status`: `APPLY_COMPLETE`, `DRY_RUN_COMPLETE`, `VALIDATION_FAILED`, `BLOCKED`, `FAILED`, or `UNKNOWN`.
- `approval_status`: evidence only.
- `protected_action_requested`: evidence only.
- `executable=false`.
- next safe action.

## What Should Become The Codex Adapter

Should become the Codex adapter:

- Codex final report normalization.
- Codex SITREP normalization.
- Codex handoff preview from canonical work packet.
- Changed-file evidence normalization.
- Validation evidence normalization.
- Commit/push/PR status normalization as evidence.
- Protected-action classification in Codex output.
- Scope violation classification.
- Result receipt preview.
- Evidence envelope output.

## What Should Remain Outside The Adapter

Must remain outside:

- Packet law: `AGENTS.md`.
- Queue ownership: `automation/orchestration/work_packets/`.
- Approval ownership: `automation/orchestration/approval_inbox/`.
- Worker identity/routing ownership: `automation/orchestration/workers/` and identity governance.
- Validator execution ownership: `automation/orchestration/validators/`.
- Commit package ownership: `automation/orchestration/commit_packages/`.
- Relay execution and file movement.
- Operator Relief runtime loops.
- Night Supervisor and dashboard projection.
- OpenAI/API/MCP use.
- Protected git actions.
- Source mutation.
- Telemetry persistence.
- Live trading, broker/API, real orders, real webhooks, and secrets.

## Acceptance Tests Needed Before Build

Minimum future acceptance tests:

1. PASS: complete Codex success report normalizes to `DRY_RUN_COMPLETE` or `APPLY_COMPLETE` with `executable=false`.
2. PASS: validation output is captured as evidence, not approval.
3. PASS: changed files inside allowed paths are recorded.
4. FAIL: changed files outside allowed paths produce `BLOCKED`.
5. FAIL: protected path touched produces `BLOCKED`.
6. FAIL: final report missing required headings produces `BLOCKED` or `UNKNOWN`.
7. FAIL: commit/push/merge/PR requested without approval produces `NEEDS_APPROVAL` or `BLOCKED`.
8. FAIL: secret, broker/API, or live-trading phrase in result produces blocked risk flag.
9. PASS: Relay Codex outbox example normalizes as historical/evidence-only.
10. PASS: Operator Relief CLI handoff record remains non-executable evidence.
11. PASS: `OrchestrationToCodexAdapter` emits handoff preview and does not launch Codex.
12. PASS: source guard proves no subprocess, OpenAI, MCP, Relay movement, queue write, approval write, telemetry write, git action, broker, or live-trading call.
13. PASS: every output layer preserves `executable=false`.

## Recommended Future Build Order

1. Create `CODEX_ADAPTER_MAPPING.md` report.
2. Create `CODEX_ADAPTER_ACCEPTANCE_TESTS.md` report.
3. Create `CODEX_ADAPTER_IMPLEMENTATION_PLAN.md` report.
4. Create preview-only adapter scaffold for result normalization.
5. Add Codex handoff preview only after result normalization is proven.
6. Do not connect Relay provider dispatch until canonical queue and approval gates are wired and separately approved.

## Exact Future APPLY Scope

The first Codex adapter APPLY should create reports only:

```text
Reports/bridge_audit/CODEX_ADAPTER_MAPPING.md
```

Then:

```text
Reports/bridge_audit/CODEX_ADAPTER_ACCEPTANCE_TESTS.md
Reports/bridge_audit/CODEX_ADAPTER_IMPLEMENTATION_PLAN.md
```

No source code should be created until those three reports exist.

## Exact Next APPLY Packet Recommendation

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
Anthony / AI_OS Owner

PACKET ID:
CODEX_ADAPTER_MAPPING_001

LANE:
CODEX_ADAPTER_MAPPING

ZONE:
AI_OS Adapter Expansion

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

PROTECTED PATHS:
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
4. Read Reports/bridge_audit/CODEX_ADAPTER_DISCOVERY.md.
5. Read Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md.
6. Read Reports/bridge_audit/FIRST_ADAPTER_SELECTION.md.
7. Read Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md.
8. Read docs/workflows/WORKER_OUTPUT_INTERFACE_STANDARD.md.
9. Confirm branch/worktree state.
10. Create only Reports/bridge_audit/CODEX_ADAPTER_MAPPING.md.
11. Run git diff --check.
12. Run git status --short --branch.

MISSION:
Define exactly how Codex final reports and Codex handoff previews map into canonical orchestration evidence.

TASK:
Create a report-only mapping specification for OrchestrationToCodexAdapter and CodexResultToEvidenceAdapter. Include input fields, required identity fields, validator fields, failure classes, result receipt preview schema, evidence schema, approval/protected-action classification, changed-file scope validation, handoff preview boundary, acceptance-test list, PASS/FAIL examples, and exact future implementation boundary.

IMPORTANT:
Do not create code.
Do not create scripts.
Do not create schemas.
Do not create adapters.
Do not create queues.
Do not create approvals.
Do not launch Codex.

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

## Discovery Conclusion

Codex already has authority, templates, manual execution flow, Relay dispatch capability, handoff helpers, evidence vocabulary, and final report rules. What is missing is not another bridge or launcher. The missing piece is a preview-only Codex adapter pair:

- `OrchestrationToCodexAdapter` for canonical work packet -> Codex handoff preview.
- `CodexResultToEvidenceAdapter` for Codex final report -> normalized evidence receipt.

The safest next step is a report-only mapping pass before any Codex adapter code exists.
