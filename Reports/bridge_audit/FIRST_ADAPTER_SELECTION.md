# First Adapter Selection

Packet: FIRST_ADAPTER_SELECTION_001
Mode: DRY_RUN report output
Lane: ADAPTER_PRIORITY_SELECTION
Branch observed: feature/full-operator-relief-closed-loop-v1
Worktree observed: C:\Dev\Ai.Os

## Decision

The first adapter to implement should be:

```text
ChatGptToOrchestrationAdapter
```

This adapter has the highest leverage because malformed, incomplete, or state-misaligned ChatGPT-generated Codex packets are the current front-door failure point. Fixing this first prevents bad packets from reaching Codex, Relay, Night Supervisor, Dashboard, OpenAI, or MCP paths.

The adapter must connect to the existing AI_OS Orchestration Harness:

```text
automation/orchestration/work_packets/
automation/orchestration/approval_inbox/
automation/orchestration/workers/
automation/orchestration/validators/
automation/orchestration/commit_packages/
```

It must not create a new bridge, queue, approval system, or execution head.

## Ranked Adapter Order

| Rank | Adapter | Recommendation | Reason |
|---:|---|---|---|
| 1 | ChatGPT Adapter | BUILD FIRST | It validates and normalizes the upstream packet before any worker, queue, approval, or evidence layer can drift. |
| 2 | Codex Adapter | BUILD SECOND | Codex output must become normalized evidence receipts after packet ingress is stable. |
| 3 | Relay Adapter | BUILD THIRD | Relay already has intake/outbox behavior, but it should adapt into canonical orchestration after packet and result shapes are stable. |
| 4 | Night Supervisor Adapter | BUILD FOURTH | Night Supervisor gains value from normalized evidence, not raw fragmented bridge heads. |
| 5 | Dashboard Adapter | BUILD FIFTH | Dashboard should display canonical evidence after evidence ownership is stable. |
| 6 | MCP Adapter (future) | DEFER | Useful for read-first tool access, but only after local packet/evidence contracts are stable. |
| 7 | OpenAI Adapter (future) | DEFER | External API, credential, redaction, and model-output risks make this lower priority than local governed adapters. |

## Adapter Evaluations

### 1. ChatGPT Adapter

Value delivered:

- Validates ChatGPT-generated Codex packets against `AGENTS.md` before Anthony or Codex spends time on manual repair.
- Converts packet text into a canonical envelope and work packet preview.
- Stops duplicate bridge heads by routing upstream intent into the selected orchestration spine.
- Reduces execution risk by preserving `executable=false` until explicit approval and packet completeness are proven.

Complexity:

- Medium-low for the first implementation because it can be DRY_RUN/report-only and local.
- No API calls, Codex launch, script execution, queue mutation, or approval mutation are required for the first pass.

Dependencies:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md`
- `Reports/bridge_audit/CANONICAL_HARNESS_SELECTION.md`
- `Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md`
- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md`
- Current Git preflight evidence.

Risks:

- Creating duplicate packet law instead of enforcing `AGENTS.md`.
- Treating a report, validator result, or dashboard card as approval.
- Writing directly to a live queue before the mapping is proven.
- Accepting invented branch/worktree state, placeholders, or missing protected-path boundaries.

Required evidence:

- Packet completeness result.
- Missing-field inventory.
- Placeholder and prohibited-path check.
- Branch/worktree alignment result.
- Allowed path and protected path classification.
- Validator-chain presence.
- Approval requirement and protected-action classification.
- Redaction/no-secret result.
- `executable=false` result.
- Next safe action.

Required approval gates:

- No protected approval gate for DRY_RUN report-only mapping.
- Anthony approval required before writing any canonical work packet.
- Protected Action Gate required for `git add`, commit, push, merge, reset, branch deletion, or PR actions.
- Separate approval required before external API calls, secrets, broker/API paths, live trading paths, or production behavior.

### 2. Codex Adapter

Value delivered:

- Normalizes Codex final reports, changed-file lists, diff checks, validation results, commit status, and push status into evidence receipts.
- Gives Night Supervisor, Relay, Dashboard, and approval projections one stable output shape.

Complexity:

- Medium.
- It must preserve the distinction between successful validation, human approval, protected actions, and actual execution outcome.

Dependencies:

- Stable ChatGPT packet ingress.
- Canonical work packet identity.
- `automation/orchestration/validators/`
- `automation/orchestration/approval_inbox/`
- `AGENTS.md` completion report rules.

Risks:

- Inferring approval from a passing validator.
- Missing files changed outside scope.
- Treating a Codex final response as queue state without provenance.
- Normalizing failed tasks as complete.

Required evidence:

- Packet ID, lane, mode, branch, and worktree.
- Files inspected and files changed.
- Validation command outputs.
- Diff summary.
- Commit and push status.
- Protected action requested or not requested.
- Failure/block status when applicable.

Required approval gates:

- No approval for evidence normalization.
- Anthony approval required for APPLY execution when the packet requires it.
- Protected Action Gate required for staging, committing, pushing, merging, or PR operations.

### 3. Relay Adapter

Value delivered:

- Converts Relay goals, handoffs, inbox tasks, outbox reports, and approval evidence into canonical packet previews or evidence receipts.
- Keeps Relay useful without allowing it to remain a duplicate queue or approval head.

Complexity:

- Medium-high because Relay has both `relay/` and `Relay/` casing, historical records, provider dispatch, approvals, and fallback behavior.

Dependencies:

- Stable packet ingress and result receipt formats.
- Relay dependency/casing inventory.
- Canonical approval boundary.

Risks:

- Mistaking stale Relay files for active work.
- Letting Relay approvals bypass `automation/orchestration/approval_inbox/`.
- Casing ambiguity on Windows and Git.
- Provider dispatch becoming execution without packet approval.

Required evidence:

- Source path and hash.
- Relay item ID and original provider/worker.
- Current vs historical classification.
- Casing ambiguity flag.
- Queue/approval/evidence role classification.

Required approval gates:

- No approval for read-only evidence classification.
- Anthony approval required before converting Relay records into canonical queue entries.
- Protected Action Gate required before provider dispatch, source edits, commit, push, merge, or PR actions.

### 4. Night Supervisor Adapter

Value delivered:

- Converts normalized evidence into current, stale, blocked, approval-needed, display-alert, and SOS classifications.
- Reduces Anthony's overnight/morning triage burden by separating active blockers from historical noise.

Complexity:

- Medium.
- Its accuracy depends on upstream evidence normalization.

Dependencies:

- Codex evidence receipts.
- Relay evidence receipts.
- Canonical approval state.
- Runtime and Night Supervisor telemetry.

Risks:

- Historical evidence causing false active blockers.
- Display alerts being mistaken for approval requests.
- Completed or stale approvals reappearing as current.

Required evidence:

- Evidence freshness.
- Current/stale classification.
- Blocking reason.
- Approval-needed reason.
- `display_alert`.
- `sos_wake_required`.
- Wake class.

Required approval gates:

- No approval for display/evidence projection.
- Anthony approval required for any action requested from a Night Supervisor card.
- Protected Action Gate required for any protected repo action.

### 5. Dashboard Adapter

Value delivered:

- Shows normalized harness state to the operator without making the dashboard a command or approval authority.
- Improves scanability after the evidence layer is stable.

Complexity:

- Medium.
- Frontend/API display work becomes risky if evidence freshness and authority fields are not stable first.

Dependencies:

- Night Supervisor classifications.
- Normalized evidence envelope.
- Runtime/dashboard API boundaries.

Risks:

- Fixture data displayed as live state.
- Dashboard card interpreted as approval.
- Stale status shown without freshness metadata.
- UI expanding before the execution loop is closed.

Required evidence:

- Source evidence path.
- Freshness timestamp.
- Current/stale flag.
- Display-only status.
- Alert/SOS fields from upstream evidence.

Required approval gates:

- No approval for read-only display.
- Anthony approval required before dashboard-triggered queue writes or approvals.
- Protected Action Gate required before any repo protected action.

### 6. MCP Adapter (Future)

Value delivered:

- Provides a future read-first local tool layer for scoped AI_OS inspection and evidence retrieval.
- Could reduce copy/paste once local evidence contracts are stable.

Complexity:

- Medium-high.
- Tool permissions, redaction, freshness, and write prevention must be exact.

Dependencies:

- Stable evidence contract.
- Stable approval ownership.
- Allowlisted read scopes.
- MCP prototype governance.

Risks:

- Read tools expanding into write tools.
- Secret/private evidence exposure.
- MCP output being treated as authority without freshness checks.
- Duplicate tool surface before the canonical harness is finished.

Required evidence:

- Tool name.
- Query scope.
- Allowed read paths.
- Returned source paths.
- Redaction status.
- Permission result.
- External transmission flag.
- `executable=false`.

Required approval gates:

- No approval for approved read-only inspection.
- Separate approval required for any write-capable MCP tool.
- Protected Action Gate required for any protected repo action.

### 7. OpenAI Adapter (Future)

Value delivered:

- Converts future approved OpenAI output into packet drafts or evidence summaries.
- Could help draft packets, validation summaries, or adapter recommendations after local gates are stable.

Complexity:

- High for production use because it introduces external transmission, credentials, model output validation, cost/rate limits, and redaction requirements.

Dependencies:

- API approval packet.
- Redaction and no-secret checks.
- Stable packet completeness validator.
- Stable local evidence contract.
- OpenAI CLI/API boundary.

Risks:

- API key exposure.
- Private repo evidence sent without approval.
- Model output inventing branch/path/state.
- Generated packet creating duplicate authority.
- Broker/API/live trading boundary drift.

Required evidence:

- Provider/model identifier when allowed.
- External transmission approval.
- Redaction status.
- Packet completeness result.
- Cost/risk classification when available.
- `executable=false`.

Required approval gates:

- Separate Anthony approval required before API use.
- Separate approval required for credentials or secret handling.
- Protected Action Gate required for repo protected actions.
- Live trading, broker/API, and real order paths remain blocked.

## Why ChatGPT Adapter Should Be First

The ChatGPT Adapter is first because it fixes the highest-upstream source of harness fragmentation. If ChatGPT packet output is incomplete, unsafe, or state-misaligned, every downstream component has to compensate manually. A local DRY_RUN ChatGPT packet adapter can reject or normalize that input before it enters any queue, approval path, Relay path, Night Supervisor digest, dashboard display, OpenAI future path, or MCP future path.

This removes the operator pain of repeatedly repairing packet structure, checking missing fields, explaining why Codex cannot execute partial prompts, and resolving duplicate head confusion after the packet has already reached the worker lane.

## Existing AI_OS Components Connected

The first adapter connects to these existing components:

- `AGENTS.md` for packet law and execution gating.
- `README.md` for repo identity and safety posture.
- `WHITEPAPER.md` for protected whitepaper pointer and paper-only Trading Lab boundary.
- `automation/orchestration/work_packets/` as the canonical queue owner.
- `automation/orchestration/approval_inbox/` as the canonical approval owner.
- `automation/orchestration/workers/` as worker identity/routing owner.
- `automation/orchestration/validators/` as validator evidence owner.
- `automation/orchestration/commit_packages/` as commit package planning owner.
- `Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md` as report-level evidence vocabulary until promoted.
- `Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md` as the current adapter architecture report.

It does not connect directly to provider dispatch, OpenAI APIs, MCP tools, live Relay execution, source mutation, scripts, secrets, broker/API paths, or live trading paths.

## Operator Pain Removed

- Manual repair of ChatGPT-generated Codex packets.
- Repeated missing-field checks.
- Confusion between executable packets, ChatGPT planning text, and reference-only context.
- Late discovery that a packet lacks branch/worktree alignment, allowed paths, protected paths, validator chain, approval authority, or stop point.
- Duplicate queue and approval-head drift caused by unnormalized upstream packets.
- Unclear next safe action after packet validation fails.

## Measurable Success

The first adapter is successful when it can take one ChatGPT-generated Codex packet and produce a DRY_RUN report that includes:

- PASS/FAIL packet completeness classification.
- Complete missing-field list when invalid.
- Placeholder/prohibited-path check.
- Branch/worktree alignment result.
- Allowed/protected path classification.
- Validator-chain classification.
- Approval-required and protected-action classification.
- Redaction/no-secret classification.
- Canonical envelope preview with `executable=false`.
- Canonical work packet preview path under `automation/orchestration/work_packets/` without writing it.
- One exact next safe action.

The first implementation should not launch Codex, call OpenAI, write queues, write approvals, edit source, create scripts, or mutate protected files.

## Exact Next APPLY Packet Recommendation

The next packet should be an APPLY-scoped report-only mapping pass. It should create a mapping report, not adapter code.

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

IDENTITY MARKER:
AI_OS_EXECUTABLE_PACKET

SUPERVISOR IDENTITY:
Anthony / AI_OS Owner

PACKET ID:
CHATGPT_TO_ORCHESTRATION_ADAPTER_MAPPING_APPLY_001

LANE:
CHATGPT_ADAPTER_MAPPING

ZONE:
AI_OS Adapter Build Sequence

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
Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md
Reports/bridge_audit/CANONICAL_HARNESS_SELECTION.md
Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md
Reports/bridge_audit/FIRST_ADAPTER_SELECTION.md
Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md

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

MISSION:
Create a report-only mapping specification for ChatGptToOrchestrationAdapter. The report must define how ChatGPT packet text is validated, classified, normalized into a canonical envelope preview, and mapped to a canonical work packet preview without writing queue files or approvals.

VALIDATOR CHAIN:
1. Read AGENTS.md.
2. Read README.md.
3. Read WHITEPAPER.md.
4. Read Reports/bridge_audit/CHATGPT_CODEX_HARNESS_HEADS_AUDIT.md.
5. Read Reports/bridge_audit/CANONICAL_HARNESS_SELECTION.md.
6. Read Reports/bridge_audit/ADAPTER_LAYER_ARCHITECTURE.md.
7. Read Reports/bridge_audit/FIRST_ADAPTER_SELECTION.md.
8. Read Reports/cli_everything/CLI_EVERYTHING_EVIDENCE_CONTRACT.md.
9. Confirm current path, branch, remote, and git status.
10. Create only Reports/bridge_audit/CHATGPT_TO_ORCHESTRATION_ADAPTER_MAPPING.md.
11. Run git diff --check.
12. Run git status --short --branch.

TASK:
Define the ChatGptToOrchestrationAdapter mapping report with packet input fields, validation rules, failure classes, canonical envelope fields, work packet preview fields, evidence fields, approval classification, protected-action classification, stop conditions, and acceptance tests.

STRICT RULES:
- Report only.
- No code.
- No scripts.
- No source edits.
- No queue writes.
- No approval writes.
- No automation creation.
- No OpenAI API calls.
- No MCP tools.
- No Codex launch.
- No commit.
- No push.
- No live trading paths.
- No broker paths.
- No secrets.

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

## Recommendation

Recommendation: BUILD.

Build only the first local report/mapping layer for `ChatGptToOrchestrationAdapter` next. Defer adapter code until the mapping report proves the input validation, canonical envelope, evidence, queue preview, approval classification, and stop conditions. Defer Relay, Night Supervisor, Dashboard, MCP, and OpenAI adapters until the upstream packet validator and output evidence shape are stable.

## Stop Point

Report only. No code created. No scripts created. No source files edited. No queue files written. No approval files written. No commit. No push.
