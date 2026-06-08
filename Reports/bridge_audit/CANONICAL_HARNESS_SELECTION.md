# Canonical Harness Selection

Packet: CANONICAL_HARNESS_SELECTION_001
Mode: DRY_RUN report output
Lane: CHATGPT_CODEX_HARNESS_SELECTION
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os

## Decision

The canonical harness head should be the existing AI_OS orchestration spine:

```text
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
```

This is not a new bridge. It is the current canonical queue, approval, worker, validator, and commit-package structure already named by active AI_OS authority. The harness architecture should finish this winner and convert other bridge heads into adapters or evidence-only sources.

The canonical harness should be named:

```text
AI_OS Orchestration Harness
```

The ChatGPT <-> Codex harness is a lane inside that harness, not a separate head.

## Canonical Harness Diagram

```text
Anthony / Human Owner
  |
  v
ChatGPT packet draft
  |
  v
AGENTS.md packet validation law
  |
  v
AI_OS Orchestration Harness
  |
  +--> Queue owner: automation/orchestration/work_packets/
  |
  +--> Approval owner: automation/orchestration/approval_inbox/
  |
  +--> Worker owner: automation/orchestration/workers/
  |
  +--> Validator owner: automation/orchestration/validators/
  |
  +--> Commit package owner: automation/orchestration/commit_packages/
  |
  v
Codex East executes only complete approved packet
  |
  v
Codex result receipt / final report
  |
  v
Evidence layer
  |
  +--> telemetry/
  +--> Reports/
  +--> relay/ as fallback evidence
  +--> Operator Relief output as adapter evidence
  |
  v
Night Supervisor / Autonomy Bridge / dashboard visibility
```

## Component Classification

| Component | Path | Classification | Selection Rationale |
|---|---|---|---|
| Packet execution law | `AGENTS.md` | EVIDENCE ONLY for this report; governing authority overall | It is authority, not the harness head. It defines what the harness must obey. |
| Human front door | `README.md` | EVIDENCE ONLY | Front-door context only. |
| Whitepaper pointer | `WHITEPAPER.md` | EVIDENCE ONLY | No harness ownership. |
| Work packet lifecycle | `automation/orchestration/work_packets/` | CANONICAL HARNESS | Existing canonical task queue and packet state root. |
| Approval inbox and apply gate | `automation/orchestration/approval_inbox/` | CANONICAL HARNESS | Existing canonical approval authority; must own approval state. |
| Worker registry and worker inbox | `automation/orchestration/workers/` | CANONICAL HARNESS | Existing canonical worker identity/routing state. |
| Validator chain | `automation/orchestration/validators/` | CANONICAL HARNESS | Existing validator evidence root; validator PASS remains evidence only. |
| Commit package flow | `automation/orchestration/commit_packages/` | CANONICAL HARNESS | Existing commit-package planning root; no commit/push without approval. |
| Command queue | `automation/orchestration/command_queue/` | ADAPTER | Can feed canonical work packets but should not become a separate task head. |
| Relay runner | `automation/orchestration/relay/Invoke-AiOsRelayRunner.ps1` | ADAPTER | Converts relay goals/handoffs into task packets. Keep as intake adapter, not authority. |
| Relay worker | `automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1` | ADAPTER | Existing provider-dispatch mechanism can execute bounded packets after gates; should consume canonical packets or mapped envelopes. |
| Relay file mailroom | `relay/` / `Relay/` | EVIDENCE ONLY | Useful handoff/outbox/history store, but duplicate casing and legacy fallback status block it from head ownership. |
| Relay legacy CLI notice | `Relay/LEGACY_CLI_RELAY_README.md` and `relay/LEGACY_CLI_RELAY_README.md` | EVIDENCE ONLY | Preserves fallback boundary. |
| Codex bridge loop sequence | `relay/handoffs/CODEX_BRIDGE_LOOP_SEQUENCE.md` | RETIRE CANDIDATE | Old planning sequence; not authority and contains legacy framing. |
| Operator Relief runtime bridge | `automation/operator_relief/runtime_bridge.py` | ADAPTER | Strong one-shot local processing pattern. It should adapt Operator Relief task JSON into canonical work packet/result evidence. |
| Operator Relief inbox/outbox bridge | `automation/operator_relief/inbox_outbox_bridge.py` | ADAPTER | Useful bounded report bridge; not queue authority. |
| Operator Relief CLI bridge | `automation/operator_relief/cli_bridge.py` | ADAPTER | Builds non-executable CLI handoff records. Useful as command-shape evidence adapter. |
| Operator Relief supervisor loop | `automation/operator_relief/supervisor_loop.py` | ADAPTER | One-shot decision cycle and Engine Room evidence; should feed canonical queue rather than own queue. |
| Operator Relief packet queue | `automation/operator_relief/packet_queue.py`, `telemetry/operator_relief/packet_queue/current_queue.json` | ADAPTER | Candidate generator only. Canonical queue remains `automation/orchestration/work_packets/`. |
| Operator Relief Engine Room telemetry | `automation/operator_relief/engine_room_telemetry.py`, `telemetry/operator_relief/engine_room/current_status.json` | EVIDENCE ONLY | Display/status evidence. |
| Operator Relief dual-review authority bridge | `automation/operator_relief/dual_review_bridge.py` | ADAPTER | Useful authority-risk classifier; not a live reviewer bridge. |
| Tools dual-review bridge | `tools/bridge/Invoke-DualReviewBridge.ps1`, `tools/bridge/README.md` | RETIRE CANDIDATE | It tries to become a separate live Codex + reviewer/API loop and conflicts with current no-recursive-Codex/no-OpenAI-API defaults. |
| Autonomy Bridge workflow | `docs/workflows/AI_OS_AUTONOMY_BRIDGE_WORKFLOW.md` | EVIDENCE ONLY | Visibility bridge only. |
| Autonomy Bridge implementation | `services/python_supervisor/autonomy_bridge.py` | EVIDENCE ONLY | Projects Relay/Night Supervisor evidence into dashboard-ready state. |
| Telemetry bridge contract | `docs/governance/TELEMETRY_BRIDGE_CONTRACT.md` | EVIDENCE ONLY | Runtime visibility contract. |
| Orchestrator app-server | `services/orchestrator/index.js` | EVIDENCE ONLY | Read-only runtime/status API plus stub pipeline, not message-passing head. |
| OpenAI/Codex onboarding workflow | `docs/workflows/OPENAI_CODEX_NIGHT_SUPERVISOR_ONBOARDING.md` | EVIDENCE ONLY | Defines role split and readiness; not harness head. |
| Codex/OpenAI packet template | `docs/workflows/CODEX_OPENAI_CLI_PACKET_TEMPLATE.md` | ADAPTER | Packet rendering aid. It must stay subordinate to `AGENTS.md`. |
| MCP prototype plan | `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md` | ADAPTER for future read-only inspection | Future read-first tool adapter, not current head. |
| OpenAI CLI boundary docs under `docs/AI_OS/openai_cli/` | RETIRE CANDIDATE unless promoted | Active-looking but under reference-only `docs/AI_OS`; consolidate into active workflow if retained. |
| OpenAI API bridge docs under `docs/AI_OS/openai_api_bridge/` | RETIRE CANDIDATE unless promoted | Future concept; not active authority. |
| OpenAI planner bridge scripts | `automation/orchestration/openai_api_bridge/` | ADAPTER | Existing fixture/planner path can become draft-packet adapter after separate validation. |
| CLI Everything evidence contract | `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md` | EVIDENCE ONLY | Good envelope contract for future harness evidence, but report is not source authority. |
| CLI Everything party investigation | `Reports/cli_everything/CLI_EVERYTHING_PARTY_BRIDGE_INVESTIGATION.md` | EVIDENCE ONLY | Useful party/layer map; not harness authority. |

## Adapter Inventory

| Adapter | Input | Output | Canonical Boundary |
|---|---|---|---|
| ChatGPT packet adapter | ChatGPT-generated complete packet or packet draft | Proposed work packet or validation failure | Must validate against `AGENTS.md` and write only into canonical packet flow when APPLY is approved. |
| Codex result adapter | Codex final report, diff summary, validation result | Normalized evidence receipt | Must not self-approve commit/push/merge. |
| Relay adapter | `relay/goals/`, `relay/handoffs/`, `relay/inbox/`, `relay/outbox/` | Canonical work packet or evidence receipt | Relay state remains evidence/fallback unless explicitly promoted. |
| Operator Relief adapter | `reports/operator_relief/inbox/`, generated packet candidates, runtime outbox | Canonical work packet proposal or evidence receipt | Operator Relief queues do not own approval or task authority. |
| CLI bridge adapter | CLI availability and non-executable command shape | Command preview evidence | No Codex/OpenAI call by default. |
| OpenAI planner adapter | OpenAI/planner fixture or future API response | Packet draft only | No API call or external transmission without separate approval. |
| MCP adapter | Future local read tool response | Evidence summary or packet draft | Read-first only until separate write-tool approval. |
| Autonomy Bridge adapter | Relay/Night Supervisor evidence | Dashboard/morning digest projection | Visibility only, not task routing or approval. |
| Telemetry adapter | Runtime/supervisor status | Runtime evidence state | Evidence only. |
| Orchestrator API adapter | Runtime telemetry | Read-only API response | No execution authority. |

## Adapter Responsibilities

Adapters must:

- translate source-specific records into the canonical work packet, approval, validator, or evidence vocabulary.
- preserve `executable=false` unless a separate approved execution lane changes that state.
- fail closed on missing identity, branch, worktree, allowed paths, forbidden paths, validator chain, stop point, or approval authority.
- preserve source evidence paths and hashes where possible.
- never create new approval authority.
- never treat validator PASS, dashboard display, telemetry, Relay output, Operator Relief output, or report text as approval.
- never call OpenAI APIs, Codex, shell passthrough, scheduler, broker/API, live trading, or notification sends unless separately scoped and approved.

## Queue Ownership

Canonical queue owner:

```text
automation/orchestration/work_packets/
```

Queue rule:

```text
All work intended for governed Codex execution must become a canonical work packet before execution.
```

Non-canonical queues:

- `relay/inbox/`
- `reports/operator_relief/inbox/`
- `telemetry/operator_relief/packet_queue/current_queue.json`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- `work_packets/` root examples/state outside canonical orchestration path

These can be intake or evidence adapters only.

## Approval Ownership

Canonical approval owner:

```text
automation/orchestration/approval_inbox/
```

Approval rule:

```text
Human Owner remains final approval authority; canonical approval state lives in automation/orchestration/approval_inbox/.
```

Evidence-only approval stores:

- `relay/approvals/`
- `Relay/approvals/`
- `approval/operator_relief/pending/`
- `automation/operator_relief/approval_input/`
- `control/operation_glue/APPROVAL_INBOX.json`
- `telemetry/approvals/`
- dashboard approval cards

These stores may inform the canonical approval adapter, but they must not become approval authority.

## Evidence Ownership

Canonical evidence layers:

```text
telemetry/
Reports/
relay/ and Relay/ as fallback/historical evidence until casing consolidation
```

Evidence rule:

```text
Evidence supports decisions; it does not authorize execution.
```

Recommended future evidence contract source:

```text
Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md
```

Current status: evidence contract report only. If AI_OS wants it to become durable authority, promote its core vocabulary into a proper active governance/workflow file through a separate authority-scoped APPLY packet.

## Exact Future Build Sequence

1. Canonical selection closeout:
   - Treat this report as the DRY_RUN selection record.
   - Do not build new head paths.

2. Evidence contract promotion decision:
   - Decide whether the `CLI_EVERYTHING_EVIDENCE_CONTRACT.md` vocabulary should be promoted into an active workflow/governance file.
   - If yes, run a separate authority-scoped packet.

3. Canonical packet adapter spec:
   - Define how ChatGPT packet drafts, Relay tasks, and Operator Relief candidates map into `automation/orchestration/work_packets/`.
   - Output report only first.

4. Canonical result receipt spec:
   - Define how Codex final reports and Relay/Operator Relief outbox records become normalized evidence receipts.
   - Keep receipts evidence-only.

5. Approval adapter spec:
   - Define how Relay approvals, Operator Relief pending approvals, and Operation Glue approvals project into `automation/orchestration/approval_inbox/` without mutating existing stores.

6. Relay adapter dry-run:
   - Convert one relay task into a canonical work packet preview.
   - Do not execute provider CLI.

7. Operator Relief adapter dry-run:
   - Convert one Operator Relief packet candidate into a canonical work packet preview.
   - Do not process source changes.

8. Codex result adapter dry-run:
   - Normalize one existing Codex-style final report into a receipt.
   - Do not infer approvals.

9. Harness validation chain:
   - Validate canonical packet completeness, branch/worktree alignment, allowed/forbidden paths, approval state, validator chain, and stop point.

10. Only after 1-9:
   - Consider a bounded APPLY implementation inside existing `automation/orchestration/` paths.
   - Do not use `tools/bridge` as implementation base.

## Risks

| Risk | Impact | Control |
|---|---|---|
| Building another head | More drift and conflicting queues | Use existing `automation/orchestration/` as harness head. |
| Relay casing ambiguity | Windows/Git path confusion | Keep as evidence until dependency review selects one casing. |
| Approval authority fragmentation | Unsafe or duplicated approvals | Keep `automation/orchestration/approval_inbox/` as sole canonical approval owner. |
| Operator Relief queue self-promotion | Separate autonomy track bypassing orchestration | Treat Operator Relief as adapter into canonical packet queue. |
| Tools bridge overreach | Recursive Codex/API loop before gates mature | Retire or re-scope `tools/bridge` before use. |
| Evidence contract not authority | Future builders may treat report as law | Promote only through separate authority packet if needed. |
| OpenAI/API leakage | Secret/private evidence exposure | Keep API integration adapter-only and no-call by default. |
| Validator PASS misuse | Execution without approval | Preserve rule that validators are evidence only. |
| Dashboard/telemetry approval confusion | UI state mistaken for permission | Keep display and approval separated. |
| Trading boundary drift | Broker/API/live order risk | Keep paper-only and blocked-live defaults. |

## Recommendation

Recommendation: finish the existing AI_OS Orchestration Harness.

Canonical harness head:

```text
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
```

Adapter strategy:

```text
Relay -> adapter
Operator Relief -> adapter
CLI bridge -> adapter
OpenAI/MCP -> future read/draft adapters
Autonomy Bridge / Telemetry / Orchestrator -> evidence-only projections
tools/bridge -> retire candidate
```

Do not create `automation/orchestration/harness/chatgpt_codex/` yet as a new implementation head. If a namespace is needed later, make it an adapter package under existing orchestration ownership, not the harness owner.

The next safe move is a DRY_RUN report that defines the canonical packet adapter mapping from Relay and Operator Relief into `automation/orchestration/work_packets/`.

## Stop Point

Report only. No source files edited. No scripts created. No commit. No push.
