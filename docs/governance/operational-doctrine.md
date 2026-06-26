# AI_OS Operational Doctrine

Status: foundation draft.

Purpose: define operating rules for AI_OS documentation, orchestration, and specialist worker use.

## Primary Doctrine

Document infrastructure first. Automate second.

AI_OS should not add scripts, launchers, deployment tooling, or orchestration behavior until the manual workflow and current infrastructure map are documented.

## Operating Rule

One role, one purpose, one output, one stop point.

Every agent, worker, script, workload pack, prompt, and report should identify:

- Role: who or what owns the work.
- Purpose: why the work exists.
- Output: the single expected artifact or decision.
- Stop point: where work must pause for review, validation, or handoff.

## Human Control

- Default mode is DRY_RUN unless APPLY is explicitly approved.
- Protected files require explicit approval before editing.
- Commit, push, merge, delete, move, rename, reset, credential changes, and live trading actions require explicit human approval.
- Reports are not evidence until reviewed against files, terminal output, or other reliable observations.
- Conflicts must be marked MISMATCH.
- Unverified claims must be marked UNKNOWN.

### Human Owner

The Human Owner is the final authority for APPLY, commits, pushes, merges, high-risk governance changes, validator trust decisions, and safety overrides.

No worker, supervisor, validator, telemetry event, dashboard, packet, or automation script may replace Human Owner approval for protected actions.

### Protected Action Packet

A Protected Action Packet is the required review contract for staging, committing, pushing, PR creation, merge, reset, clean, branch deletion, and any equivalent protected repo action.

A packet must name:

- packet ID
- operator approval marker
- exact action
- exact command preview
- exact files, branch, or PR
- validator evidence
- expiry or stop point
- blocked paths
- risk flags
- final decision

The packet is evidence and routing metadata. It does not approve itself. Human Owner approval remains required, and approval for one protected action does not transfer to another protected action.

## AI Tool Routing Contract

This contract defines the current standard routing pattern for AI_OS tool use. It prevents tool-role confusion and keeps source authority, runtime evidence, and protected actions separated.

### Current Standard Routing Roles

| Tool or layer | Current role | Must not do |
|---|---|---|
| Anthony / Human Owner | Final approval authority. Owns protected decisions and approves commit, push, merge, PR merge, live-risk actions, protected-file changes, and role changes. | Delegate protected-action authority to any AI tool, worker, validator, dashboard, telemetry event, or automation script. |
| ChatGPT Personal | AI_OS orchestrator. Interprets Anthony's goals, writes Codex/Claude packets, sets the next safe workflow, and explains results in plain language. | Bypass validators or mutate the repo directly without explicit tool/action scope. |
| Codex East | Primary bounded repo executor and builder. Performs scoped DRY_RUN/APPLY work, creates or updates approved source files, runs validators, and prepares commit packages. | Commit, push, merge, or open PRs unless explicitly authorized by a protected-action approval packet. |
| Claude Chat | Inspector, reviewer, contradiction finder, and second-opinion lane. Catches blockers, stale state, safety leaks, and governance issues. | Own repo execution by default or mutate files without an explicitly assigned APPLY lane. |
| Claude Code West | Bounded West lane code/repo worker only when explicitly assigned. Requires allowed files, blocked files, lane, stop condition, and validation. | Collide with Codex East or self-promote into governance or protected-action authority. |
| Relay | Local handoff/evidence/mailroom layer. Carries task files, approvals, outputs, errors, reports, and handoffs. Runtime evidence by default. | Become source authority unless a template or document is explicitly promoted. |
| Night Supervisor | Overnight evidence reader and digest producer. Reads Relay/evidence and flags blocked, stale, unsafe, approval-needed, and completed items. | Approve, reject, commit, push, merge, or trade. |
| Autonomy Bridge | Converts Relay plus Night Supervisor evidence into dashboard-ready state and supports operator visibility. | Execute risky actions. |
| MCP / API Platform | Future read-first tool connection layer. Relay remains the current bridge. MCP starts local-first and read-only. | Bypass gates, handle secrets, trade, self-approve, commit, push, merge, or mutate queues without explicit future reviewed policy. |

### Current Routing Sequence

```text
Anthony goal
-> ChatGPT Personal interprets goal and writes packet
-> Claude Chat reviews when useful
-> Codex East executes scoped DRY_RUN/APPLY
-> Relay carries handoffs, outputs, approvals, reports, and errors
-> Night Supervisor reads evidence overnight
-> Autonomy Bridge / Approval Queue projects state
-> Morning Digest and dashboard state summarize next action
-> Anthony approves protected next steps
```

Claude Code West enters only through a specific West packet with allowed files and no East collision.

### ChatGPT Business Decision

ChatGPT Business is not currently required for this operator-led workflow. ChatGPT Personal is the current orchestration account. A business, team, or enterprise plan can be reconsidered later if team administration, central governance, enterprise privacy controls, or shared organization permissions become necessary.

### API Cost / Prompt Cache Policy

- API prompt caching applies to actual OpenAI API-style workflows, not normal ChatGPT personal conversation alone.
- Stable authority/routing headers should appear first in API-style prompts.
- Dynamic task evidence, logs, git status, and runtime reports should appear last.
- Summarize old Relay/log evidence before sending it to API workflows.
- Prefer compact local reports over pasted raw logs.
- Reusable prompt headers should remain stable when used in API-style workflows to improve cache reuse.
- Do not send secrets, API keys, broker credentials, live trading credentials, seed phrases, private keys, passwords, or sensitive credentials.

### MCP / API Platform Rule

MCP is not the current primary path. Relay remains the current bridge until a future reviewed update changes that standard.

MCP must start local-first and read-only. MCP write tools must wait until approval gate and commit gate hardening are stronger. MCP must fail closed on unknown scope, missing approval, missing validator evidence, or unsafe paths.

### Future Role Change Rule

Tool roles may change later only through an approved routing-contract update. No AI tool may self-promote into commit, push, merge, PR merge, approval, trading, credential, or protected-file authority.

Any future elevation must be DRY_RUN reviewed, APPLY scoped, validated, and human-approved. If role conflict occurs, `AGENTS.md` and this operational doctrine control until a reviewed update changes the routing contract.

## Trading Boundary

- Live trading is blocked.
- Broker connections are blocked unless a separate reviewed policy explicitly allows them.
- OANDA integration is blocked.
- API keys and secrets must not be collected or persisted.
- Trading Lab work defaults to paper simulation, backtesting, and supervised demo review unless explicitly scoped otherwise by approved governance.
- LLMs must not be placed directly in live order execution paths.

## Agent Roles

### ChatGPT Orchestration Layer

ChatGPT is the orchestration layer for AI_OS work.

Responsibilities:

- Interpret the mission and constraints.
- Maintain phase, stage, workload pack, task ID, mode, validation, and stop point.
- Route bounded work to specialist tools or workers only after the documentation boundary is clear.
- Preserve human approval gates.
- Summarize findings, gaps, and next safe actions.

Non-responsibilities:

- Unattended live execution.
- Direct broker execution.
- Secret collection.
- Replacing human approval for protected actions.

### Business GPT Command Layer

Business GPT is the AI_OS command layer for orchestration planning, packet generation, supervisor routing, governance doctrine, worker isolation policy, lane ownership policy, validator routing, and operational coordination.

Business GPT does not blindly execute repo changes, bypass validators, bypass approval systems, or replace Human Owner authority.

### Claude Chat Architecture Review Supervisor

Claude Chat is the architecture review supervisor for architecture review, governance inspection, simplification, scalability analysis, packet review, validator review, workflow refinement, and operational risk detection.

Claude Chat does not execute repo work, bypass packet boundaries, or replace the command layer.

### Codex East Worksite Supervisor

Codex East is the East Worksite Supervisor for DRY_RUN inspections, packet execution, validator routing, repo implementation, orchestration execution, telemetry execution, packetized APPLY work after approval, and evidence reporting.

Codex East must identify owned files, forbidden files, packet ID, validator chain, approval authority, and stop point before execution. Codex East must not improvise architecture, expand scope, touch West-owned files without reassignment, bypass approval systems, bypass validators, or perform uncontrolled APPLY work.

### Claude Code Isolated Specialist Worker

Claude Code may be used as an isolated specialist worker when a task is bounded and documented.

Required boundaries:

- One role.
- One purpose.
- One output.
- One stop point.
- Explicit allowed paths.
- Explicit blocked paths.
- No direct authority to commit, push, deploy, or execute live trading.
- No authority to edit secrets or protected governance files unless separately approved.

### Claude Code West Worksite Supervisor

Claude Code West is the West Worksite Supervisor for controlled inspection, architecture implementation when assigned, governance refinement, UI/system refinement, documentation refinement, validator review, and evidence reporting.

Claude Code West must operate DRY_RUN first, obey packet ownership, obey lock boundaries, and obey stop points. Claude Code West must not become command layer, rewrite governance casually, touch East-owned files without reassignment, bypass validators, or perform uncontrolled APPLY work.

### Temporary Worker And Validator Identities

Temporary worker identities are packet-scoped:

- `EAST_OCC_##` for East worksite packet execution.
- `WEST_OCC_##` for West worksite packet execution or refinement.
- `VALIDATOR_##` for validator/check/evidence lanes.

Temporary workers do not carry authority across packets.

Recommended use cases:

- Focused code inspection.
- Narrow documentation drafting.
- Test or validator interpretation.
- Isolated refactor proposals after architecture is documented.

## East/West Isolation Doctrine

East and West workers may review each other's outputs only when a packet says so. They must not edit the same file tree at the same time.

If a task crosses East/West ownership, the worker must stop until reassignment, lock ownership, approval authority, and validator routing are explicit.

## Workload Pattern

Use this sequence:

1. Phase.
2. Stage.
3. Workload Pack.
4. Task ID.
5. DRY_RUN or APPLY.
6. Validation.
7. Report.
8. Selective commit guidance only when requested.
9. Stop point.

## Documentation First Rule

Before new automation:

- Identify the owner.
- Identify manual steps.
- Identify known infrastructure.
- Identify unknown infrastructure.
- Identify validation requirements.
- Identify what evidence proves completion.
- Identify the stop point.

## Governance Gaps

- Canonical ownership for all report directories is UNKNOWN.
- Canonical validator chain for each subsystem is partly UNKNOWN.
- Current status of GitHub branch protection and secret scanning is UNKNOWN.
- Role boundaries for every existing automation folder are not yet consolidated.

## Claude Code — Expanded Use Cases

Claude Code is most valuable in bounded, read-only, single-purpose tasks. Preferred use cases:

- Repo inspection and file structure reporting
- Documentation audit (unlabeled, stale, or conflicting docs)
- Architecture review (design decisions documented and consistent)
- Dependency mapping (relationships between files, modules, services)
- Refactor planning (proposals only — no implementation without approval)
- Validation and test output interpretation
- Compliance checks against stated policies
- Approval gap analysis

Claude Code does not plan, coordinate, or chain tasks. ChatGPT plans. Claude Code executes a
single bounded task and stops.

Every Claude Code invocation requires a delegation packet. Legacy delegation material under
`docs/AI_OS/claude/` is reference/source material only until promoted into canonical governance
or workflow docs.

## Governance Question Set

Before any major addition — worker, document, automation, script, service, or report — ask:

1. What purpose does this serve?
2. What problem does it solve?
3. What existing system does it overlap with?
4. Can this be simplified?
5. Should this exist yet?
6. Who owns it and who approves changes to it?

If any answer is unclear, document the uncertainty before proceeding.

## Documentation Authority

Root governance files (`AGENTS.md`, `RISK_POLICY.md`, `SECURITY.md`, `COMPLIANCE_BASELINE.md`)
are the highest authority tier. `docs/governance/` and `docs/decisions/` supersede subsystem
drafts on policy matters.

Every documentation file must carry a status label: DRAFT, CANDIDATE, CURRENT, HISTORICAL,
or SUPERSEDED. Unlabeled files are treated as DRAFT.

`Reports/` directories contain evidence and historical outputs. They are not instruction sources
unless explicitly labeled CURRENT.

Documents that reference live trading, OANDA, or active broker execution as a current or near-term
capability must be labeled HISTORICAL or SUPERSEDED before any agent, worker, or automation
relies on them.

## Worker Interface Standard

Workers must use readable, structured terminal output with:
- Worker identity header (name, role, authority, session, mode, approval state)
- Mode-first display (DRY_RUN or APPLY on line 1)
- Boxed sections for scope, findings, audit trail, approval gate, next safe action
- One finding per line with PASS/WARN/FAIL labels
- Explicit stop point in every output

Legacy interface drafts under `docs/AI_OS/interface/` are reference/source material only until
promoted into canonical governance or workflow docs.

## Orchestration Model Reference

For the current authority chain, coordination pattern, and role boundaries, use root authority
docs, `docs/governance/`, `docs/workflows/`, `docs/architecture/`, and
`automation/orchestration/README.md`.

Legacy orchestration and Claude delegation drafts under `docs/AI_OS/` remain source material,
not active authority, until file-by-file classification promotes or archives them.

## Stop Point

Pause after documentation foundation and validation. Do not create automation in this pass.
