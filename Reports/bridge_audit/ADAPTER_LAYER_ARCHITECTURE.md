# Adapter Layer Architecture

Packet: ADAPTER_LAYER_ARCHITECTURE_001
Mode: DRY_RUN report output
Lane: ADAPTER_LAYER_DISCOVERY
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os

## Summary

The adapter layer connects existing systems into the selected canonical harness:

```text
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
```

No adapter owns a queue, approval system, or bridge head. Every adapter translates into or out of the existing orchestration spine and emits evidence using the CLI Everything evidence envelope.

## Adapter Interaction Diagram

```text
ChatGPT Adapter
  |
  v
Canonical Envelope
  |
  v
AI_OS Orchestration Harness
  |
  +--> work_packets/          (queue owner)
  +--> approval_inbox/        (approval owner)
  +--> workers/               (worker identity/routing owner)
  +--> validators/            (validator evidence owner)
  +--> commit_packages/       (commit package planning owner)
  |
  v
Codex Adapter
  |
  v
Result Receipt / Evidence Envelope
  |
  +--> Relay Adapter ----------> relay evidence only
  +--> Night Supervisor Adapter -> active/stale/blocker projection
  +--> Dashboard Adapter -------> display-only state
  +--> OpenAI Adapter (future) -> packet draft only
  +--> MCP Adapter (future) ----> read-first evidence only
```

## Canonical Envelope Flow

```text
source-specific input
-> adapter validates identity, scope, mode, branch/worktree, allowed paths, forbidden paths, validator chain, approval need, stop point
-> canonical envelope with executable=false
-> canonical work packet preview or canonical evidence receipt
-> AI_OS Orchestration Harness
-> normalized evidence envelope
```

The canonical envelope should reuse the fields from `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md` until that vocabulary is promoted into active workflow/governance authority.

Minimum envelope fields:

- `schema`
- `event_id`
- `created_at_utc`
- `source_party`
- `source_command`
- `packet_id`
- `lane`
- `mode`
- `repo_root`
- `branch`
- `worktree`
- `allowed_paths`
- `forbidden_paths`
- `status`
- `status_impact`
- `blocked_reasons`
- `risk_flags`
- `validator_chain`
- `validator_results`
- `approval_required`
- `approval_status`
- `protected_action_requested`
- `display_alert`
- `sos_wake_required`
- `wake_class`
- `redaction_status`
- `executable`
- `next_safe_action`
- `stop_point`

## Queue Flow

Canonical queue:

```text
automation/orchestration/work_packets/
```

Flow:

```text
ChatGPT packet draft / Relay task / Operator Relief candidate / future OpenAI draft / future MCP read result
-> adapter
-> canonical envelope
-> work packet preview
-> automation/orchestration/work_packets/proposed/
-> validation
-> approval gate when required
-> approved/active packet state
-> Codex execution only when packet is complete and authorized
```

Non-canonical queues such as `relay/inbox/`, `reports/operator_relief/inbox/`, `telemetry/operator_relief/packet_queue/current_queue.json`, and `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json` are intake or evidence only.

## Approval Flow

Canonical approval owner:

```text
automation/orchestration/approval_inbox/
```

Flow:

```text
adapter detects approval requirement
-> evidence envelope marks approval_required=true
-> canonical approval request preview
-> automation/orchestration/approval_inbox/
-> Anthony approval decision
-> adapter validates decision against packet, allowed paths, protected action, expiry, replay, and scope
-> work may continue only within approved scope
```

Evidence-only approval stores:

- `relay/approvals/`
- `Relay/approvals/`
- `approval/operator_relief/pending/`
- `automation/operator_relief/approval_input/`
- `control/operation_glue/APPROVAL_INBOX.json`
- dashboard cards
- telemetry projections

These stores may be read by adapters, but they must not authorize execution.

## Evidence Flow

Evidence owners:

```text
Reports/
telemetry/
relay/ and Relay/ as fallback or historical evidence until casing consolidation
```

Flow:

```text
adapter event
-> normalized evidence envelope
-> telemetry/report output
-> Night Supervisor classification
-> Autonomy Bridge state
-> Dashboard display
-> operator review only when display_alert=true or sos_wake_required=true
```

Evidence must never become approval. Validator PASS, dashboard state, telemetry, reports, Relay outbox, and Operator Relief output are decision support only.

## Adapter Naming Standard

Use a stable actor-to-spine pattern:

```text
<Source>ToOrchestrationAdapter
OrchestrationTo<Consumer>Adapter
```

Recommended names:

| Adapter | Standard Name | Direction |
|---|---|---|
| ChatGPT Adapter | `ChatGptToOrchestrationAdapter` | packet draft -> canonical envelope/work packet |
| Codex Adapter | `OrchestrationToCodexAdapter` and `CodexResultToEvidenceAdapter` | canonical packet -> Codex handoff; Codex report -> evidence |
| Relay Adapter | `RelayToOrchestrationAdapter` and `OrchestrationToRelayEvidenceAdapter` | relay records -> canonical packet/evidence |
| Night Supervisor Adapter | `EvidenceToNightSupervisorAdapter` | evidence -> night classification |
| Dashboard Adapter | `EvidenceToDashboardAdapter` | evidence -> display state |
| OpenAI Adapter | `OpenAiDraftToOrchestrationAdapter` | future model output -> packet draft |
| MCP Adapter | `McpReadToEvidenceAdapter` | future read tool response -> evidence/draft |

Rules:

- Names must describe source and destination.
- Names must not include `bridge` unless the component is truly a transport bridge.
- Names must not imply approval authority.
- Names must not imply direct execution unless the adapter is explicitly approved to execute.

## Adapter Definitions

### A. ChatGPT Adapter

Purpose:
Convert ChatGPT-generated packet drafts or complete tokenized packets into canonical orchestration work packet previews.

Inputs:

- ChatGPT packet text.
- Operator goal text when packet generation is requested.
- `AGENTS.md` packet requirements.
- Current branch/worktree preflight evidence.
- Allowed paths, forbidden paths, validator chain, stop point.

Outputs:

- Canonical envelope.
- Work packet preview for `automation/orchestration/work_packets/proposed/`.
- Validation failure report when packet is incomplete or unsafe.

Evidence emitted:

- `AIOS_CLI_EVIDENCE.v1` envelope.
- Missing field list.
- Placeholder/forbidden path checks.
- Branch/worktree alignment result.
- `executable=false` unless separately approved.

Ownership:

- Adapter only.
- Canonical queue remains `automation/orchestration/work_packets/`.
- Packet law remains `AGENTS.md`.

Dependencies:

- `AGENTS.md`
- `README.md`
- `docs/governance/operational-doctrine.md`
- CLI evidence contract vocabulary.
- Current Git preflight.

Failure modes:

- Missing `CODEX-ONLY PROMPT`.
- Missing `AI_OS EXECUTION TOKEN` when executable packet is required.
- Missing identity fields.
- Missing allowed/forbidden paths.
- Placeholder or unresolved path.
- Branch/worktree mismatch.
- Duplicate authority or duplicate queue attempt.

SOS conditions:

- Invalid executable packet that blocks continuation.
- Protected action requested without Anthony approval.
- Forbidden path, secret, broker/API, live trading, or production risk.
- Dirty worktree overlap with mission that cannot be classified safely.

### B. Codex Adapter

Purpose:
Hand a validated canonical packet to Codex execution context and normalize Codex final output into evidence.

Inputs:

- Canonical work packet.
- Approved execution scope when required.
- Validator chain.
- Codex final report, diff summary, validation output, and changed file list.

Outputs:

- Codex execution handoff preview.
- Codex result receipt.
- Normalized evidence envelope.

Evidence emitted:

- Packet ID.
- Lane.
- Files inspected.
- Files changed.
- Validation commands/results.
- Diff summary.
- Commit status.
- Push status.
- Protected action requested or not.
- `executable=false` for evidence receipts.

Ownership:

- Adapter only.
- Codex remains bounded repo executor.
- Protected action gates remain separate.

Dependencies:

- `automation/orchestration/work_packets/`
- `automation/orchestration/validators/`
- `automation/orchestration/approval_inbox/`
- `AGENTS.md`

Failure modes:

- Packet incomplete.
- Validation failure.
- Changed files outside allowed paths.
- Protected path touched without scope.
- Sandbox or tool failure.
- Final report missing required fields.

SOS conditions:

- Validator failure blocking continuation.
- Changed file outside allowed paths.
- Protected action needed.
- Commit/push/merge request without exact approval.
- Secret/broker/live trading risk.

### C. Relay Adapter

Purpose:
Convert Relay goals, handoffs, inbox tasks, outbox reports, approvals, and historical evidence into canonical packet previews or evidence receipts.

Inputs:

- `relay/goals/`
- `relay/handoffs/`
- `relay/inbox/`
- `relay/outbox/`
- `relay/approvals/`
- `Relay/` historical/case-variant records.

Outputs:

- Canonical work packet preview.
- Canonical evidence receipt.
- Approval projection evidence only.

Evidence emitted:

- Source path.
- Source hash.
- Relay item ID.
- Original worker/provider.
- Risk tier.
- Status impact.
- Historical/current classification.
- Casing ambiguity flag when applicable.

Ownership:

- Adapter only.
- Relay remains evidence/fallback until dependency and casing consolidation.
- It does not own queue or approval authority.

Dependencies:

- Relay records.
- Canonical queue and approval owners.
- Evidence contract vocabulary.

Failure modes:

- Duplicate `Relay/` vs `relay/` paths.
- Malformed relay task.
- Missing required packet fields.
- Stale historical record presented as active.
- Relay approval mistaken as canonical approval.

SOS conditions:

- Queue corruption that blocks safe continuation.
- Active Relay task requests protected action without approval.
- Casing ambiguity affects active task routing.
- Relay evidence contains secret/broker/live trading risk.

### D. Night Supervisor Adapter

Purpose:
Classify current evidence into active, stale, blocked, approval-needed, and display-only state for night review.

Inputs:

- Canonical evidence envelopes.
- Work packet state.
- Approval state.
- Validator results.
- Relay and Operator Relief evidence receipts.
- Runtime telemetry.

Outputs:

- Night Supervisor classification.
- Morning digest inputs.
- Blocker and approval-needed summaries.
- `display_alert` / `sos_wake_required` decisions.

Evidence emitted:

- Active current items.
- Historical detail-only items.
- Current blockers.
- Approval-needed items.
- Stale warnings.
- SOS classification.

Ownership:

- Evidence projection only.
- No execution, approval, queue movement, commit, push, merge, or source mutation authority.

Dependencies:

- `automation/orchestration/night_supervisor/`
- `telemetry/night_supervisor/`
- Autonomy Bridge state model.
- CLI evidence contract.

Failure modes:

- Historical Relay noise driving current status.
- Completed approvals counted as active.
- Stale digest mistaken for current state.
- Missing evidence classification.

SOS conditions:

- Active blocker prevents safe continuation.
- Protected action approval is required.
- Validator failure blocks continuation.
- Branch/worktree mismatch blocks assigned task.
- Evidence mismatch makes next action unsafe.

### E. Dashboard Adapter

Purpose:
Render canonical evidence and Night Supervisor state into operator-readable display without becoming approval or execution authority.

Inputs:

- Normalized evidence envelopes.
- Autonomy Bridge state.
- Morning digest state.
- Runtime visibility state.
- Approval projection state.

Outputs:

- Dashboard-readable state.
- Decision cards.
- Blocker cards.
- Display-only summaries.

Evidence emitted:

- Source evidence paths.
- Freshness timestamp.
- Display status.
- `display_alert`.
- `sos_wake_required`.
- `wake_class`.
- Current vs stale classification.

Ownership:

- Display only.
- No queue, approval, execution, commit, push, or merge authority.

Dependencies:

- `services/orchestrator/` read-only runtime API.
- `telemetry/runtime/`
- `telemetry/night_supervisor/`
- Dashboard fixtures or future approved API wiring.

Failure modes:

- Fixture data shown as live.
- Stale state shown without freshness warning.
- `NEEDS_APPROVAL` displayed as SOS when it is review-only.
- Dashboard card interpreted as approval.

SOS conditions:

- Dashboard itself should not create SOS from display alone.
- SOS can be displayed only when upstream evidence has `sos_wake_required=true`.
- Missing or stale dashboard state is display warning unless it blocks a required approval path.

### F. OpenAI Adapter (Future)

Purpose:
Convert future approved OpenAI/Responses output into packet drafts or evidence summaries without bypassing AI_OS gates.

Inputs:

- Approved prompt input.
- Redacted/sanitized context.
- Model output.
- Optional planner fixture output.

Outputs:

- Packet draft only.
- Evidence summary.
- Validation failure if output is incomplete or unsafe.

Evidence emitted:

- Model/provider identifier when allowed.
- Request classification.
- Redaction status.
- External transmission flag.
- Packet completeness result.
- Cost/risk estimate when available.
- `executable=false`.

Ownership:

- Future adapter only.
- No direct execution.
- No approval authority.
- No source mutation.

Dependencies:

- Separate API approval packet.
- No-secret policy.
- Redaction checks.
- Packet schema and `AGENTS.md`.
- OpenAI CLI/API boundary.

Failure modes:

- API key missing or exposed.
- Private evidence sent without approval.
- Model output invents branch/path/state.
- Packet missing required fields.
- Prompt contains secrets or broker/live trading content.

SOS conditions:

- Approved API task blocked by credential/access failure.
- Secret or private evidence exposure risk.
- Generated packet requests protected/live/broker action without approval.
- Model output creates duplicate authority or unsafe execution request.

### G. MCP Adapter (Future)

Purpose:
Expose read-first local AI_OS evidence through narrow MCP tools and convert tool responses into evidence or packet drafts.

Inputs:

- MCP read tool response.
- Scoped file/queue/approval/telemetry query.
- Tool metadata and permission boundary.

Outputs:

- Evidence summary.
- Packet draft preview.
- Fail-closed report on unknown or unsafe scope.

Evidence emitted:

- Tool name.
- Query scope.
- Allowed read paths.
- Returned evidence paths.
- Redaction status.
- Permission result.
- External transmission flag.
- `executable=false`.

Ownership:

- Future read adapter only.
- No write, approval, queue movement, command execution, or protected action authority in v1.

Dependencies:

- MCP prototype plan.
- Allowlisted read scopes.
- Redaction policy.
- Approval and queue ownership rules.

Failure modes:

- Tool scope unknown.
- Tool returns private/secret evidence.
- Write tool appears without approval.
- MCP result treated as current authority without freshness check.

SOS conditions:

- MCP tool attempts unauthorized write or command execution.
- Secret/private evidence risk.
- Required approval evidence is missing for a protected action.
- Tool failure blocks a required human approval or safety check.

## Adapter Build Order

1. Packet adapter report:
   - Define mapping from ChatGPT packet drafts, Relay tasks, and Operator Relief candidates into canonical work packet previews.

2. Result receipt report:
   - Define Codex/Relay/Operator Relief output normalization into evidence receipts.

3. Approval adapter report:
   - Define how evidence-only approval stores project into `automation/orchestration/approval_inbox/` without authority duplication.

4. Relay adapter dry-run implementation proposal:
   - Convert one Relay item to canonical work packet preview.

5. Operator Relief adapter dry-run implementation proposal:
   - Convert one Operator Relief candidate to canonical work packet preview.

6. Codex result adapter dry-run implementation proposal:
   - Normalize one Codex final report into evidence envelope.

7. Night Supervisor/Dashboard adapter alignment:
   - Ensure current/stale/status-impact fields control display and SOS separation.

8. Future OpenAI adapter:
   - Only after API approval, redaction, and no-secret validation.

9. Future MCP adapter:
   - Read-first only, after local evidence and approval mappings are stable.

## Recommended First Adapter To Implement

Recommended first adapter:

```text
ChatGptToOrchestrationAdapter
```

Reason:

- It addresses the highest-friction point first: malformed or incomplete ChatGPT-generated Codex packets.
- It does not require API calls, source mutation, Relay execution, Codex launch, or new queue ownership.
- It can validate packet completeness against `AGENTS.md`.
- It routes output into the already selected canonical queue path.
- It reduces duplicate heads by forcing every future ChatGPT -> Codex handoff through the canonical orchestration spine.

First implementation should be DRY_RUN/report-only:

```text
Read packet text
-> validate against AGENTS.md required fields
-> classify missing fields, placeholders, branch/worktree mismatch, protected actions
-> emit evidence envelope
-> preview canonical work packet
-> stop
```

## Non-Actions

- No new bridge.
- No new queue.
- No new approval system.
- No source edits.
- No scripts.
- No commits.
- No pushes.
- No automation creation.
- No API calls.
- No MCP tools.
- No Codex launch.
- No live trading, broker/API, secrets, or production behavior.

## Recommendation

Build the adapter layer in this order:

```text
ChatGPT Adapter
-> Codex Result Adapter
-> Approval Adapter
-> Relay Adapter
-> Operator Relief Adapter
-> Night Supervisor/Dashboard evidence adapters
-> OpenAI/MCP future adapters
```

Keep all adapters subordinate to:

```text
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
```

The next safe task is a DRY_RUN packet-mapping report for `ChatGptToOrchestrationAdapter`.
