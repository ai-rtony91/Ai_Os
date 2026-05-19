# AI_OS Orchestration Model
**Document Type:** Orchestration Architecture Standard
**Version:** 0.1
**Status:** DRAFT — Operator Review Required
**Execution Mode:** APPLY (documentation only)
**Approval State:** APPROVED — Tony, 2026-05-18

---

## Purpose

This document defines the AI_OS orchestration model: who coordinates work, who executes work,
how authority flows, and how specialist workers are invoked and stopped.

This is not a workflow automation spec. It is a role and responsibility map.

---

## Primary Doctrine

**Document infrastructure first. Automate second.**

The orchestration model does not exist to automate the system. It exists to make coordination
legible — so that every action taken by any agent or worker can be traced back to a human
decision and a documented scope.

---

## Orchestration Roles

### Role 1: ChatGPT — AI_OS Orchestrator

ChatGPT is the orchestration layer for AI_OS work. It operates as the central coordinator and
planner that sits between the human operator and all specialist workers.

**Core responsibilities:**

| Responsibility | Description |
|---------------|-------------|
| Mission interpretation | Translate operator instructions into bounded, scoped tasks. |
| Phase and stage maintenance | Track the current phase, stage, workload pack, and task ID. |
| Gap analysis | Identify what is missing, undocumented, or unclear before routing work. |
| Redundancy prevention | Detect and suppress duplicate work across workers and sessions. |
| Worker routing | Decide when to invoke Claude Code, Codex, or other specialist workers. |
| Approval gate preservation | Surface approval requirements before any APPLY action. |
| Findings summary | Consolidate findings, gaps, unknowns, and next safe actions. |
| Mode enforcement | Ensure DRY_RUN is the default posture; require explicit approval for APPLY. |

**What ChatGPT does not do:**

- Unattended live execution of any kind.
- Direct broker or trading execution.
- Collection or persistence of secrets, tokens, or credentials.
- Replacing human approval for protected actions.
- Bypassing the stop point.

**When ChatGPT should invoke Claude Code:**

Claude Code should be invoked only when the task is:
1. Bounded to a specific scope (exact files, exact purpose).
2. Read-only by default, or APPLY-approved for an exact named action.
3. Documented as a delegation packet before being sent.
4. Expected to produce a single reviewable output.

ChatGPT decides whether to invoke Claude Code. The operator approves or rejects the invocation
and reviews the output before any APPLY action is taken.

---

### Role 2: Claude Code — Isolated Specialist Worker

Claude Code operates as an isolated specialist within the AI_OS architecture. It is not an
autonomous agent and does not have standing authority to make changes, run sequences, or continue
work beyond its defined stop point.

**Default posture: read-only.**

Claude Code may read files in its allowed scope and produce reports, findings, or draft documents.
It may not write files, commit, push, or execute live actions unless the delegation packet
explicitly approves an APPLY action for a named file and operation.

**Recommended use cases:**

| Use Case | Description |
|----------|-------------|
| Repo inspection | Read and report on file structure, contents, gaps. |
| Documentation audit | Find unlabeled, stale, or conflicting docs. |
| Architecture review | Assess whether design decisions are documented and consistent. |
| Dependency mapping | Trace relationships between files, modules, or services. |
| Refactor planning | Propose bounded changes — no implementation without approval. |
| Validation interpretation | Read test or validator output and summarize findings. |
| Compliance check | Verify docs or code against a stated policy or rule set. |
| Approval gap analysis | Identify which actions are missing approval records. |

**What Claude Code does not do:**

- Autonomous re-invocation or self-continuation beyond its stop point.
- Commit, push, merge, deploy, or execute live actions without explicit APPLY approval.
- Edit secrets, protected governance files, or trading execution paths.
- Create automation, scripts, frontend code, or dashboards unless explicitly scoped and approved.
- Decide its own scope — scope is always defined in the delegation packet.

**Required boundaries for every Claude Code invocation:**

Every invocation must define:
1. Role (what Claude is in this task)
2. Mode (DRY_RUN or explicit APPLY)
3. Scope (allowed paths, blocked paths, blocked actions)
4. Rules (governing constraints)
5. Task (exactly what to do)
6. Return format (exactly what output to produce)
7. Stop point (where to stop)
8. Escalation path (what to do if FAIL, MISMATCH, or BLOCKED)
9. Approval state (NOT_REQUIRED or APPROVED with approver and date)

See `docs/AI_OS/claude/CLAUDE_DELEGATION_STANDARD.md` for the full delegation packet format.

---

### Role 3: Codex — Repository Implementer

Codex applies approved repository changes. It operates under ChatGPT coordination and User
approval. Its scope is bounded repository work — code, configuration, and file changes that have
been reviewed and approved before execution.

Codex does not plan or architect. ChatGPT plans; Codex executes approved plans.

---

### Role 4: User (Tony) — Execution Authority

The User is the highest authority in the AI_OS system. All APPLY actions, protected file edits,
commits, pushes, and safe mode exits require User approval. No delegated worker or supervisor can
override this requirement.

**Actions that require User-level approval only:**

- Any APPLY action on protected governance files
- Commits and pushes to the repository
- Exiting SAFE_MODE
- Unlocking trading or broker execution
- Deleting, moving, or renaming files
- Credential, secret, token, or key changes

---

## Authority Chain

```
[User: Tony]  —  Execution authority. Approves APPLY. Highest authority.
     │
     ▼
[ChatGPT-Architect]  —  Orchestration layer. Plans, routes, summarizes, gates.
     │
     ├──▶  [Codex-Executor]  —  Repository implementer. Approved changes only.
     │
     ├──▶  [Claude Code]  —  Isolated specialist. Bounded task. Delegation packet required.
     │
     └──▶  [Other workers]  —  Any future specialist registered in the worker registry.
     │
     ▼
[User: Approval Gate]  —  Review and approve before APPLY execution.
```

**Chain rules:**
- No worker may bypass the User approval gate for protected actions.
- Delegation depth must not exceed 3 levels without a WARN surfaced to the operator.
- Autonomous execution (no traceable human instruction in the chain) is always BLOCKED.
- Supervisors may coordinate workers but may not grant APPLY approval on behalf of the User.

---

## Coordination Pattern

The standard pattern for any significant AI_OS task:

```
1. Operator states objective and constraints.
2. ChatGPT interprets scope, phases the work, and identifies gaps.
3. ChatGPT proposes a bounded DRY_RUN task for Claude Code or Codex.
4. Operator reviews the proposed delegation packet or Codex scope.
5. Operator approves or adjusts.
6. Worker executes the bounded task.
7. Worker produces output in the required return format with a stop point.
8. ChatGPT reviews findings and summarizes gaps, risks, and next safe action.
9. Operator reviews summary and decides whether to proceed to APPLY.
10. If APPLY: operator approves exact scope, worker executes, audit trail is produced.
11. Stop point reached. Cycle repeats from step 1 for next task.
```

No step in this pattern is automated end-to-end. Human decisions occur at steps 1, 4, 9, and 11.

---

## Governance Question Set

Before any major addition to AI_OS — a new worker, a new doc, a new automation, a new service,
or a new script — ask these six questions:

1. **What purpose does this serve?**
   If the answer is vague, the addition is not ready.

2. **What problem does it solve?**
   If the problem is not documented, document it first.

3. **What existing system does it overlap with?**
   If overlap exists, decide whether to consolidate or justify the parallel.

4. **Can this be simplified?**
   If yes, simplify it before proceeding.

5. **Should this exist yet?**
   If the prerequisite documentation and manual workflow are not stable, the answer is no.

6. **Who owns it and who approves changes to it?**
   If the answer is unclear, document the uncertainty before proceeding.

These questions apply to:
- New orchestration components
- New Claude delegation packet types
- New automation scripts
- New report types
- New service or app surfaces
- New governance documents

---

## Documentation Authority Model

Not all documentation carries equal authority. The following hierarchy governs which files take
precedence when guidance conflicts:

| Tier | Files | Role |
|------|-------|------|
| Tier 1 — Root Governance | `AGENTS.md`, `RISK_POLICY.md`, `SECURITY.md`, `COMPLIANCE_BASELINE.md` | Highest authority. Protected. Changes require User approval. |
| Tier 2 — Top-Level Docs | `docs/governance/`, `docs/decisions/`, `docs/infrastructure/`, `docs/workflows/` | Canonical operating rules. Supersede subsystem drafts on policy matters. |
| Tier 3 — Subsystem Docs | `docs/AI_OS/`, `docs/security/` | Detailed implementation and interface standards. |
| Tier 4 — Reports and Evidence | `Reports/` | Historical evidence and generated outputs. Not instruction sources unless explicitly marked CURRENT. |
| Tier 5 — Drafts and Candidates | Any file labeled DRAFT, CANDIDATE, or lacking a status label | Not authoritative until promoted. Must not be relied upon by agents without review. |

### Document Labeling Requirements

Every documentation file must carry a status label. Unlabeled files are treated as DRAFT until
reviewed:

| Label | Meaning |
|-------|---------|
| `DRAFT` | Work in progress. Not yet reviewed or approved. |
| `CANDIDATE` | Ready for review. Not yet adopted. |
| `CURRENT` | Adopted and in active use. |
| `HISTORICAL` | Superseded by a newer document. Retained for reference only. |
| `SUPERSEDED` | Explicitly replaced. Should not be relied upon by workers or agents. |

### Historical and Superseded Content — Specific Risk

The AI_OS repository contains whitepaper and planning documents that reference live trading,
OANDA integration, and broker execution as planned or active capabilities. These references predate
the current trading boundary policy.

**Rule:** Any document that references live trading, OANDA, or active broker execution as
a current or near-term capability must be labeled `HISTORICAL` or `SUPERSEDED` before it is used
as a reference by any agent, worker, or automation.

Documents that cannot be reviewed and labeled yet must be marked `UNKNOWN — STATUS UNVERIFIED`
until a human review is completed. Agents must not treat unreviewed historical language as
current policy.

---

## aios.ps1 Future Direction

`aios.ps1` is the local PowerShell entry point for AI_OS operator sessions. Its current and future
scope is bounded by the following principles:

**What it may do (current scope):**
- Prepare the operator environment for an AI_OS session.
- Display current mode, worker state, and system status.
- Surface the current phase, stage, and workload pack to the operator.

**What it may do (future documented scope):**
- Prepare Claude Delegation Packets as structured text for operator review.
- Display candidate delegation packet templates for the operator to review and send manually.

**What it must never do:**
- Automatically feed packets to Claude without operator review.
- Auto-commit or auto-push outputs produced by Claude.
- Run Claude Code unattended or in a background loop.
- Bypass the operator approval gate between packet preparation and packet use.
- Enable broker connections, live trading, or autonomous execution.

Any expansion of `aios.ps1` scope beyond the current operating rules requires:
1. A documented workload pack describing the expansion.
2. A DRY_RUN review of impact.
3. Operator approval before APPLY implementation.

---

## Orchestration Anti-Patterns

These patterns have caused or will cause control loss. Avoid them:

| Anti-Pattern | Risk | Rule |
|-------------|------|------|
| Asking Claude to "do what's needed" | Open scope — no stop point | Always define exact scope and stop point. |
| Sending a packet without a RETURN FORMAT | Unpredictable output — hard to review | Always specify the return format. |
| Approving "APPLY to any needed files" | Unconstrained write — audit gap | Approval must name exact files. |
| Skipping the delegation packet | No audit trail — no stop point | Delegation packet required for all file-system tasks. |
| ChatGPT deciding APPLY on behalf of User | Authority bypass | User approves APPLY. Supervisors do not. |
| Cascading worker chains without checkpoints | Depth creep — control loss | Maximum 3 delegation levels. Checkpoint after each. |
| Treating Reports/ as current policy | Stale data used as instruction | Reports are evidence/history unless marked CURRENT. |
| Relying on unlabeled historical docs | Old trading/OANDA language as active policy | Label or quarantine before any agent reference. |

---

## Stop Point

This orchestration model is documented. No automation has been created.

Next safe step: operator reviews the authority chain, coordination pattern, and governance question
set. Confirm whether any existing orchestration documents in `docs/AI_OS/orchestration/` conflict
with or should be superseded by this model.

---

*AI_OS Orchestration Model — v0.1 DRAFT*
*Produced: 2026-05-18 | Mode: APPLY (documentation only) | Approved by: Tony 2026-05-18*
