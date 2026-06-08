# ChatGPT Codex Harness Heads Audit

Packet: CHATGPT_CODEX_HARNESS_HEADS_AUDIT_002
Mode: DRY_RUN report output
Lane: CHATGPT_CODEX_HARNESS_DISCOVERY
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os

## Summary

AI_OS already contains several bridge and harness heads, but they do not yet form one canonical ChatGPT <-> Codex message-passing system.

The strongest current canonical execution-adjacent path is:

```text
ChatGPT drafts complete tokenized packet
-> Codex executes packet manually in the active worktree
-> Codex reports result
-> Operator/Night Supervisor/Relay evidence captures status
```

The strongest current local automation-adjacent path is:

```text
reports/operator_relief/inbox/*.json
-> automation/operator_relief/runtime_bridge.py
-> automation/operator_relief/inbox_outbox_bridge.py
-> automation/operator_relief/write_enabled_safe_executor.py
-> reports/operator_relief/outbox/*.result.json
```

The strongest current provider-dispatch path is:

```text
relay/goals or relay/handoffs
-> automation/orchestration/relay/Invoke-AiOsRelayRunner.ps1
-> relay/inbox/*.task.json
-> automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1
-> provider CLI command in APPLY mode
-> relay/outbox/*.report.txt
```

These are separate heads. The recommended next move is CONSOLIDATE.

## Bridge Inventory

| Component | Path | Classification | Evidence | Notes |
|---|---|---|---|---|
| AI_OS packet law / Codex execution gate | `AGENTS.md` | CANONICAL | Requires `CODEX-ONLY PROMPT`, `AI_OS EXECUTION TOKEN`, identity fields, allowed/forbidden paths, validator chain, stop point | Highest local authority for Codex behavior. |
| OpenAI/Codex onboarding workflow | `docs/workflows/OPENAI_CODEX_NIGHT_SUPERVISOR_ONBOARDING.md` | CANONICAL | Defines ChatGPT, Codex, OpenAI CLI, Night Supervisor handoff order | Workflow authority, not runtime bridge. |
| Packet template | `docs/workflows/CODEX_OPENAI_CLI_PACKET_TEMPLATE.md` | CANONICAL usage artifact | States `AGENTS.md` wins and provides packet shape | Template only; not executable authority. |
| Operator Relief runtime bridge | `automation/operator_relief/runtime_bridge.py` | CANONICAL for Operator Relief v1 local runtime bridge | Processes oldest `reports/operator_relief/inbox/*.json`, writes one outbox result, archives processed task | Non-executable by design; no Codex/OpenAI invocation. |
| Operator Relief inbox/outbox bridge | `automation/operator_relief/inbox_outbox_bridge.py` | CANONICAL within Operator Relief v1 | Reads one FullAutoTask JSON and writes one outbox report through safe executor | Report bridge, not message-passing bridge. |
| Operator Relief CLI bridge | `automation/operator_relief/cli_bridge.py` | INCOMPLETE | Builds non-executable CLI handoff records and blocks live execution token | Discovers Codex/OpenAI CLI availability but does not invoke them. |
| Operator Relief supervisor loop | `automation/operator_relief/supervisor_loop.py` | INCOMPLETE | Generates packet queue, builds non-executable CLI handoff, writes Engine Room telemetry | One-shot control spine; no worker launch. |
| Operator Relief dual-review authority bridge | `automation/operator_relief/dual_review_bridge.py` | INCOMPLETE / SUPERSEDED-BY-BOUNDARY | Generates authority-aware review evidence; tests prove no subprocess/API/Codex calls | Name suggests dual-review runtime, but implementation is only authority classification evidence. |
| `tools/bridge` dual-review launcher | `tools/bridge/Invoke-DualReviewBridge.ps1`, `tools/bridge/README.md` | DUPLICATE / INCOMPLETE | README claims Codex + ChatGPT + Claude loop; launcher expects API keys and calls Python bridge path | Conflicts with current no-OpenAI/no-recursive-Codex boundary in Operator Relief v1. Needs retirement or hard re-scope. |
| Relay local file bridge | `Relay/README.md`, `relay/README.md` | CANONICAL evidence/fallback, but not primary authority | Describes provider-neutral local file bridge and CLI provider defaults | Directory casing is duplicated (`Relay` and `relay`). |
| Relay worker runner | `automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1` | CANONICAL for provider-neutral relay dispatch | Supports `claude`, `codex`, `openai`, `custom`; hard-stops TIER_2; validates output | Can dispatch CLI in `-Apply`, but OpenAI requires explicit provider command. |
| Relay goal/handoff runner | `automation/orchestration/relay/Invoke-AiOsRelayRunner.ps1` | CANONICAL for local relay intake | Converts goals to handoffs/tasks and writes stub reports | Its APPLY writes relay files; dry-run does not call models. |
| Legacy CLI relay notice | `Relay/LEGACY_CLI_RELAY_README.md`, `relay/LEGACY_CLI_RELAY_README.md` | SUPERSEDED | States CLI relay is legacy fallback only and active path is packet queue -> worker assignment -> Codex/APPLY lane -> validator -> approval inbox -> commit package -> dashboard | Retain until replacement proven; do not use as primary authority. |
| Codex bridge sequence handoff | `relay/handoffs/CODEX_BRIDGE_LOOP_SEQUENCE.md` | ABANDONED / REFERENCE | Drafted by Claude; contains old AI_OS_V2 wording and broad packets | Reference-only; not executable authority. |
| Autonomy Bridge workflow | `docs/workflows/AI_OS_AUTONOMY_BRIDGE_WORKFLOW.md` | CANONICAL evidence projection | Relay + Night Supervisor -> Morning Digest + dashboard state | Visibility bridge, not Codex dispatch. |
| Autonomy bridge implementation | `services/python_supervisor/autonomy_bridge.py` | CANONICAL evidence projection | Produces `telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json` via wrapper | Evidence classifier only. |
| Telemetry bridge contract | `docs/governance/TELEMETRY_BRIDGE_CONTRACT.md` | CANONICAL telemetry bridge | Python supervisor -> telemetry/runtime -> orchestrator/dashboard | Runtime visibility only. |
| Orchestrator app-server | `services/orchestrator/index.js` | CANONICAL read-only API/stub | Serves runtime status/queue/audit/health/visibility; `/api/pipeline/run` is stub | Not ChatGPT/Codex message passing. |
| MCP prototype plan | `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md` | INCOMPLETE future plan | Read-first MCP layer; no mutation or process start | Useful future architecture, not built. |
| OpenAI CLI boundary | `docs/AI_OS/openai_cli/AIOS_OPENAI_CLI_BRIDGE_BOUNDARY.md` | SUPERSEDED/REFERENCE under `docs/AI_OS` | Defines no API key printing and future smoke tests | `docs/AI_OS` is generally reference-only unless promoted. |
| OpenAI to packet generator path | `docs/AI_OS/openai_api_bridge/AIOS_OPENAI_TO_PACKET_GENERATOR_PATH.md` | SUPERSEDED/REFERENCE under `docs/AI_OS` | Future Responses API -> packet draft path | Not active authority; concept should be consolidated into active workflow if retained. |
| OpenAI planner bridge scripts | `automation/orchestration/openai_api_bridge/*` | INCOMPLETE | Fixture/planner pipeline names exist | Needs separate validation before being treated as live integration. |
| Active work packet queue | `automation/orchestration/work_packets/` | CANONICAL queue state | Source-of-truth map marks this active work packet lifecycle root | Queue state, not ChatGPT/Codex bridge by itself. |
| Active approval inbox | `automation/orchestration/approval_inbox/` | CANONICAL approval authority | Source-of-truth map names this single active approval authority | Must not be bypassed by Relay or Operator Relief queues. |
| Worker registry/inbox | `automation/orchestration/workers/` | CANONICAL worker state | Source-of-truth map marks registry and inbox active | Worker routing state; not external message transport. |

## Ownership Inventory

| Owner / Layer | Current Owner Path | Classification | Responsibility |
|---|---|---|---|
| Repo/Codex authority | `AGENTS.md` | CANONICAL | Prompt routing, execution token, identity, approval, protected-action, stop-point law. |
| Human front door | `README.md` | CANONICAL | Repo identity and contributor orientation. |
| Whitepaper pointer | `WHITEPAPER.md` | CANONICAL pointer | Points to canonical candidate; no bridge ownership. |
| AI tool routing contract | `docs/governance/operational-doctrine.md` | CANONICAL | ChatGPT, Codex, Claude, Relay, Night Supervisor, Autonomy Bridge, MCP/API role split. |
| Work packet lifecycle | `automation/orchestration/work_packets/` | CANONICAL | Active/proposed/approved/blocked/complete packet state. |
| Approval authority | `automation/orchestration/approval_inbox/` | CANONICAL | Active approval inbox and apply approval gate. |
| Local evidence mailroom | `relay/` / `Relay/` | DUPLICATE casing; evidence/fallback | File handoffs, outbox, approvals, reports, historical relay artifacts. |
| Operator Relief v1 harness | `automation/operator_relief/` | CANONICAL for its bounded local v1 | Safe executor, packet queue, CLI handoff evidence, runtime bridge, supervisor loop. |
| Runtime visibility | `telemetry/runtime/`, `services/orchestrator/` | CANONICAL visibility | Read-only runtime/dash status. |
| Night Supervisor evidence | `automation/orchestration/night_supervisor/`, `telemetry/night_supervisor/` | CANONICAL observer/evidence | Night reports and Autonomy Bridge state. |
| Future MCP/API | `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md` | INCOMPLETE | Future read-first local tool layer only. |

## Duplicate-Head Inventory

| Duplicate Head | Paths | Classification | Consolidation Risk |
|---|---|---|---|
| Relay directory casing | `Relay/` and `relay/` | DUPLICATE | Windows hides casing risk; Git and tools can still produce confusing duplicate references. Pick one canonical casing later, likely lowercase `relay/`, after dependency review. |
| Approval stores | `automation/orchestration/approval_inbox/`, `relay/approvals/`, `approval/operator_relief/pending/`, `automation/operator_relief/approval_input/`, `control/operation_glue/APPROVAL_INBOX.json` | DUPLICATE | Only `automation/orchestration/approval_inbox/` is active approval authority. Others are evidence, projections, or local approval input until consolidated. |
| Packet queues | `automation/orchestration/work_packets/`, `relay/inbox/`, `reports/operator_relief/inbox/`, `automation/operator_relief/packet_queue.py`, `telemetry/operator_relief/packet_queue/current_queue.json` | DUPLICATE | Different queue shapes exist for different experiments. Need one canonical message envelope before ChatGPT <-> Codex passing. |
| Codex handoffs | `docs/workflows/CODEX_OPENAI_CLI_PACKET_TEMPLATE.md`, `automation/orchestration/handoff/New-AiOsCodexHandoff.DRY_RUN.ps1`, `relay/handoffs/*.handoff.json`, `automation/operator_relief/cli_bridge.py` | DUPLICATE | Multiple ways to represent a Codex instruction; only AGENTS-compliant tokenized packet should execute. |
| Bridge concepts | `automation/operator_relief/*bridge*.py`, `tools/bridge/*`, `docs/workflows/AI_OS_AUTONOMY_BRIDGE_WORKFLOW.md`, `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md`, `docs/governance/TELEMETRY_BRIDGE_CONTRACT.md` | DUPLICATE terminology | "Bridge" means evidence projection, file relay, CLI handoff, runtime report, telemetry export, or dual review depending on file. Needs naming discipline. |
| OpenAI integration | `docs/workflows/OPENAI_CODEX_NIGHT_SUPERVISOR_ONBOARDING.md`, `docs/AI_OS/openai_cli/*`, `docs/AI_OS/openai_api_bridge/*`, `automation/orchestration/openai_api_bridge/*`, `automation/orchestration/openai_cli/*` | DUPLICATE / INCOMPLETE | Active workflow allows readiness checks only; legacy/future docs discuss API bridge. Consolidate into one active OpenAI bridge boundary. |
| Supervisor loops | `automation/operator_relief/supervisor_loop.py`, `automation/orchestration/supervisor/*`, `automation/orchestration/night_supervisor/*`, `services/python_supervisor/*` | DUPLICATE roles | Need clear split: repo supervisor, night observer, runtime API, Operator Relief one-shot loop. |

## Missing Pieces Inventory

| Missing Piece | Why It Matters | Current Evidence |
|---|---|---|
| Single canonical message envelope | ChatGPT packets, relay tasks, Operator Relief tasks, and work packets use different shapes | Schemas exist under `schemas/aios/orchestration/`, but no single ChatGPT <-> Codex bridge envelope is designated. |
| Canonical queue selection | Multiple queue roots can accept "work" | Active source-of-truth says `automation/orchestration/work_packets/` is canonical, while Relay and Operator Relief use separate inboxes. |
| ChatGPT ingress mechanism | ChatGPT has no direct governed local write/read path into the repo except human paste or future MCP/API | MCP plan is read-first only and not implemented. |
| Codex dispatch authorization gate | Relay worker can call `codex` in APPLY, but AI_OS packet law still requires complete tokenized packets and approval gates | `Invoke-AiOsRelayWorker.ps1` provider dispatch exists; `AGENTS.md` forbids unscoped execution. |
| Output normalization | Codex terminal final reports, relay reports, Operator Relief JSON, and telemetry states differ | Output validator exists for Relay, but no universal Codex result schema is canonical. |
| Approval unification | Active approval authority is clear, but evidence queues are fragmented | `docs/governance/APPROVAL_UNIFICATION_PLAN.md` exists; consolidation not complete. |
| Secret/API boundary for real ChatGPT calls | OpenAI API/CLI calls are mostly future/boundary-only | Readiness checks do not call API; future smoke tests require separate approval. |
| Worker collision and lock integration | ChatGPT <-> Codex bridge must not launch overlapping lanes | Worker locks/registries exist but are not connected to Operator Relief or Relay as a single canonical launch gate. |
| End-to-end validator chain | Existing validators are narrow and path-specific | Need bridge-level validator proving input envelope -> queue -> Codex execution -> output report -> approval status. |
| Retention/casing cleanup for `Relay` vs `relay` | Duplicate casing can create path ambiguity | Both casings appear in file lists and telemetry references. |

## Candidate Canonical Harness

Recommended candidate canonical harness path:

```text
automation/orchestration/harness/chatgpt_codex/
```

Recommended canonical queue path for actual work state:

```text
automation/orchestration/work_packets/
```

Recommended evidence/output path:

```text
telemetry/chatgpt_codex_harness/
```

Recommended report/dry-run path:

```text
Reports/bridge_audit/
```

Reasoning:

- `automation/orchestration/` is already the canonical orchestration root.
- `work_packets/` and `approval_inbox/` are already canonical state/approval homes.
- `telemetry/` is already the runtime evidence layer.
- Operator Relief and Relay can be adapters into the canonical harness, not new heads.

## Candidate Retirement List

Retirement here means "future consolidation candidate only"; this audit does not approve delete, move, archive, or rewrite.

| Candidate | Recommendation | Reason |
|---|---|---|
| `tools/bridge/Invoke-DualReviewBridge.ps1` | RETIRE or re-scope to evidence-only | Current README describes live Codex + reviewer API loop, but current governance and Operator Relief v1 block OpenAI API calls and recursive Codex by default. |
| `tools/bridge/README.md` | RETIRE or rewrite after canonical harness decision | Over-promises "ends copy-paste loop" and API key flow before current authority is ready. |
| `relay/handoffs/CODEX_BRIDGE_LOOP_SEQUENCE.md` | RETIRE / archive as reference | Old Claude-drafted sequence, contains legacy AI_OS_V2 wording and broad packet plans. |
| Duplicate `Relay/` casing references | CONSOLIDATE later | Pick one casing after dependency review; likely lowercase `relay/`. |
| `docs/AI_OS/openai_api_bridge/*` active-looking docs | CONSOLIDATE into active workflow or mark reference-only | `docs/AI_OS` is reference/source material; active OpenAI bridge boundary should live in `docs/workflows/` or `docs/governance/`. |
| `docs/AI_OS/openai_cli/*` active-looking docs | CONSOLIDATE into active onboarding/boundary docs | Avoid parallel OpenAI authority. |
| `approval/operator_relief/pending/` as approval authority | RETIRE as authority; retain as local evidence/input if needed | Active approval authority is `automation/orchestration/approval_inbox/`. |
| `relay/approvals/` as approval authority | RETIRE as authority; retain as evidence/fallback | Relay approval evidence is historical/fallback unless promoted. |

## Exact Path To Build ChatGPT <-> Codex Message Passing

Build path:

```text
automation/orchestration/harness/chatgpt_codex/
```

Minimum modules/scripts to build later:

```text
automation/orchestration/harness/chatgpt_codex/README.md
automation/orchestration/harness/chatgpt_codex/New-AiOsChatGptCodexEnvelope.DRY_RUN.ps1
automation/orchestration/harness/chatgpt_codex/Test-AiOsChatGptCodexEnvelope.DRY_RUN.ps1
automation/orchestration/harness/chatgpt_codex/Convert-AiOsEnvelopeToWorkPacket.DRY_RUN.ps1
automation/orchestration/harness/chatgpt_codex/Export-AiOsCodexResultReceipt.DRY_RUN.ps1
schemas/aios/orchestration/chatgpt_codex_envelope.schema.json
schemas/aios/orchestration/codex_result_receipt.schema.json
telemetry/chatgpt_codex_harness/
```

Bridge sequence:

```text
ChatGPT packet draft or operator goal
-> validated ChatGPT/Codex envelope
-> canonical work packet under automation/orchestration/work_packets/proposed/
-> approval/validator gate
-> Human Owner execution approval when required
-> Codex executes complete tokenized packet
-> Codex result receipt
-> telemetry/chatgpt_codex_harness/
-> Autonomy Bridge / Morning Digest / dashboard visibility
```

## Recommended Canonical Harness Architecture

1. Keep `AGENTS.md` as packet law.
2. Keep `automation/orchestration/work_packets/` as canonical task queue.
3. Keep `automation/orchestration/approval_inbox/` as canonical approval authority.
4. Add a narrow ChatGPT/Codex envelope schema that can represent:
   - packet id
   - actor identities
   - lane
   - branch/worktree preflight
   - allowed paths
   - forbidden paths
   - validator chain
   - stop point
   - risk tier
   - approval requirements
   - prompt body
   - execution token state
   - result receipt path
5. Build adapters, not new heads:
   - Relay adapter: relay task -> canonical work packet.
   - Operator Relief adapter: Operator Relief packet candidate -> canonical work packet.
   - OpenAI adapter: OpenAI/Responses output -> packet draft only.
   - Codex adapter: Codex final report -> result receipt.
6. Keep direct OpenAI/ChatGPT API calls out of v1 unless a separate API-smoke packet approves credentials, timeout, redaction, no-write boundaries, and output validation.
7. Do not use `tools/bridge` as the first build path. It is too broad and reviewer/API-heavy for current governance maturity.

## Recommendation

Recommendation: CONSOLIDATE.

Do not BUILD a new standalone bridge head and do not RETIRE Relay/Operator Relief immediately.

Next best move:

```text
Create a DRY_RUN-only canonical ChatGPT/Codex envelope and adapter plan under automation/orchestration/harness/chatgpt_codex/, using automation/orchestration/work_packets/ and automation/orchestration/approval_inbox/ as the only canonical queue and approval heads.
```

Do not:

- launch Codex from a bridge yet.
- call OpenAI APIs from the bridge yet.
- let Relay approvals or Operator Relief approvals become canonical approval authority.
- delete or move `Relay/` or `relay/` until dependency review resolves casing and references.
- promote `tools/bridge` without reconciling it with current no-recursive-Codex and no-OpenAI-API default boundaries.

## Validation Notes

Read-first files:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `docs/governance/AI_OS_REPO_MEMORY.md`
- `docs/governance/source-of-truth-map.md`
- `docs/audits/active-system-map.md`

Targeted discovered files included:

- `aios.ps1`
- `automation/operator_relief/runtime_bridge.py`
- `automation/operator_relief/inbox_outbox_bridge.py`
- `automation/operator_relief/cli_bridge.py`
- `automation/operator_relief/supervisor_loop.py`
- `automation/operator_relief/unattended_mission_runner.py`
- `automation/operator_relief/dual_review_bridge.py`
- `automation/orchestration/relay/Invoke-AiOsRelayRunner.ps1`
- `automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1`
- `docs/workflows/FULL_OPERATOR_RELIEF_CLOSED_LOOP.md`
- `docs/workflows/AI_OS_AUTONOMY_BRIDGE_WORKFLOW.md`
- `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md`
- `docs/workflows/OPENAI_CODEX_NIGHT_SUPERVISOR_ONBOARDING.md`
- `docs/workflows/CODEX_OPENAI_CLI_PACKET_TEMPLATE.md`
- `docs/AI_OS/openai_cli/AIOS_OPENAI_CLI_BRIDGE_BOUNDARY.md`
- `docs/AI_OS/openai_api_bridge/AIOS_OPENAI_TO_PACKET_GENERATOR_PATH.md`
- `docs/governance/TELEMETRY_BRIDGE_CONTRACT.md`
- `services/orchestrator/index.js`
- `Relay/README.md`
- `Relay/LEGACY_CLI_RELAY_README.md`
- `relay/handoffs/CODEX_BRIDGE_LOOP_SEQUENCE.md`
- selected bridge-related tests under `tests/operator_relief/`

No source files were edited by this audit.
