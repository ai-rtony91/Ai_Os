> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Claude Delegation Standard
**Document Type:** Worker Delegation Standard
**Version:** 0.1
**Status:** APPROVED - Active AI_OS Claude Delegation Standard
**Execution Mode:** APPLY (documentation only)
**Approval State:** APPROVED — Tony, 2026-05-18

---

## Purpose

This document defines the standard format for a Claude Delegation Packet — the structured
instruction set given to Claude Code whenever it is invoked as an isolated specialist worker within
the AI_OS architecture.

A delegation packet ensures that Claude Code:
- Knows its role and boundaries before it begins
- Cannot drift scope, generate unrequested output, or take undeclared actions
- Returns a predictable, reviewable artifact
- Has an explicit stop point that prevents runaway execution

Claude Code is not an autonomous agent in AI_OS. It is a bounded specialist called with a specific
job and expected to stop when that job is done.

---

## Primary Rule

**One role. One purpose. One output. One stop point.**

Every Claude delegation packet must enforce this rule. A packet that asks Claude to do multiple
unrelated things, produce multiple artifact types, or leave the stop point open is a malformed
packet and should be revised before sending.

---

## Prompt Scope Calibration

Claude delegation scope must match risk, uncertainty, system depth, and mutation scope.

Core formula:

```text
prompt scope = risk + uncertainty + system depth + mutation scope
```

Claude delegation packets should use these scope levels:

- `narrow`: one known file, one known behavior, low risk, low uncertainty.
- `scoped`: bounded multi-file work with clear allowed paths, blocked paths, validation, and stop point.
- `broad`: discovery, audit, classification, ownership mapping, or stale/conflicting authority review only.
- `architecture-level`: authority, topology, runtime, safety, orchestration, workflow doctrine, cross-system ownership, or role-boundary work.

Broad Claude prompts are for discovery, audit, and classification only. They do not authorize APPLY.

Architecture-level Claude prompts require justification. The packet must state why authority, topology, runtime, safety, orchestration, workflow doctrine, cross-system ownership, or role boundaries are in scope.

Scope expansion cannot be silent. If Claude determines that a task requires paths, systems, risks, or authority layers outside the packet, Claude must stop, report `REVIEW_REQUIRED`, and explain the proposed expansion instead of continuing.

Timeline estimates must use uncertainty ranges. Claude must not invent deadlines or promise completion dates. Checkpoint estimates are preferred over completion-date promises.

---

## Claude Next 3 Best Moves Requirements

When Claude is asked for the "next 3 best moves," the response must include:

- project depth assessment.
- current checkpoint awareness.
- dependency awareness.
- risk level.
- expected effort range.
- uncertainty range.
- suggested order.
- rough checkpoint timeline range.

Claude should estimate project depth from:

- number of subsystems affected.
- authority level touched.
- dependency uncertainty.
- runtime or topology involvement.
- safety risk.
- stale or legacy material involved.
- whether the task changes behavior or only documents it.

Use these project depth labels:

- `LOW`: one file or one isolated document.
- `MEDIUM`: one subsystem or bounded workflow.
- `HIGH`: multiple subsystems, orchestration, worker routing, validators, or runtime-adjacent work.
- `STRATEGIC`: authority, topology, safety, architecture, or repo-wide sequencing.

Claude checkpoint timeline ranges should use practical ranges such as:

- `same session`: narrow or scoped inspection, small documentation update, or single validation pass.
- `1-2 work sessions`: bounded multi-file workflow, registry, validator, or documentation update.
- `2-4 work sessions`: broad audit followed by a controlled APPLY pass.
- `multi-checkpoint`: architecture, topology, runtime, safety doctrine, or cross-system ownership work.

Each timeline should name checkpoints rather than fake completion dates. Example checkpoint order:

1. Inspect and classify.
2. Update the existing canonical files.
3. Validate and decide whether a commit package is ready.

---

## Delegation Packet Structure

Every Claude task must include all nine fields. Fields may not be omitted. If a value is genuinely
unknown, write `UNKNOWN` or `N/A — not applicable` rather than leaving the field blank.

```
ROLE:
  <What Claude is in this task. One phrase. Example: isolated code auditor, documentation
  reviewer, dependency mapper, refactor planner.>

MODE:
  <DRY_RUN or APPLY. Default is DRY_RUN. APPLY requires explicit operator approval and must
  name the exact file, path, and action being approved.>

SCOPE:
  Allowed paths:
    <Exact file paths or directory patterns Claude may read or touch.>
  Blocked paths:
    <Exact file paths or directory patterns Claude must not touch.>
  Blocked actions:
    <What Claude must never do in this task — e.g., no commits, no pushes, no secrets,
    no live trading, no automation creation, no frontend code.>

RULES:
  <Short list of constraints that govern this task. Reference the operative policy if it
  has a doc. Examples: DRY_RUN only / report first / no new automation / no protected file
  edits / mark unknowns as UNKNOWN / mark conflicts as MISMATCH.>

TASK:
  <Exactly what Claude must do. One bounded task. No open-ended exploration unless the ROLE
  is explicitly an Explore pass. Use a numbered list if the task has ordered steps.>

RETURN FORMAT:
  <The exact format of the required output. Examples: 7-region worker layout per
  AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md / bullet list of findings / structured
  Markdown table / plain text summary with PASS/WARN/FAIL labels.>

STOP POINT:
  <Where Claude must stop. The condition that ends the task. Examples: stop after producing
  the report / stop after listing findings, do not fix / stop after the DRY_RUN summary,
  do not proceed to APPLY without separate approval.>

ESCALATION PATH:
  <Who to notify or what to output if a FAIL, MISMATCH, UNKNOWN, or BLOCKED state is
  encountered. Example: output a MISMATCH finding and stop — do not proceed to APPLY.>

APPROVAL STATE:
  <NOT_REQUIRED (DRY_RUN) or PENDING or APPROVED — <operator name, date, exact action>.>
```

---

## Delegation Packet Examples

### Example 1 — DRY_RUN Repo Audit

```
ROLE:
  Isolated repo auditor.

MODE:
  DRY_RUN. No files changed. Output is preview-only.

SCOPE:
  Allowed paths:
    docs/AI_OS/
    docs/governance/
    docs/infrastructure/
    docs/workflows/
    docs/audits/
    docs/decisions/
  Blocked paths:
    apps/
    services/
    automation/
    scripts/
    aios/
    agent/
    Reports/
    Any path containing secrets, credentials, tokens, or keys.
  Blocked actions:
    No commits. No pushes. No file edits. No automation creation.
    No frontend code. No live trading. No broker connections.

RULES:
  - DRY_RUN only.
  - Report findings first.
  - Mark unverified facts as UNKNOWN.
  - Mark conflicting evidence as MISMATCH.
  - Do not fix — only identify.

TASK:
  1. Inspect docs/AI_OS/ for files without a status label (DRAFT, CANDIDATE, CURRENT,
     HISTORICAL, SUPERSEDED).
  2. List files that appear to reference live trading or OANDA as an active capability
     without a HISTORICAL or SUPERSEDED label.
  3. List files with no clear ownership or stop point.

RETURN FORMAT:
  7-region worker layout per AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md.
  Findings region: one finding per line with PASS/WARN/FAIL label.
  Next Safe Action: one exact instruction.

STOP POINT:
  Stop after producing the findings list. Do not fix or edit any file.

ESCALATION PATH:
  If a protected file (AGENTS.md, RISK_POLICY.md, SECURITY.md, COMPLIANCE_BASELINE.md)
  is found to need relabeling, output a WARN finding and stop. Do not edit the file.

APPROVAL STATE:
  NOT_REQUIRED (DRY_RUN).
```

---

### Example 2 — APPLY Documentation Update

```
ROLE:
  Isolated documentation writer.

MODE:
  APPLY — approved by Tony, 2026-05-18, for the exact action below only.

SCOPE:
  Allowed paths:
    docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md
  Blocked paths:
    All other paths.
  Blocked actions:
    No commits. No pushes. No automation. No code changes.

RULES:
  - APPLY mode approved for this file only.
  - Do not edit any file not listed in allowed paths.
  - Report what was changed in the Audit Trail region.
  - Stop after the single edit.

TASK:
  Add a "Revision History" section at the bottom of
  docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md
  recording: version 0.1 initial draft date, author, and approval state.

RETURN FORMAT:
  7-region worker layout.
  Audit Trail region must list: file changed, section added, lines changed.

STOP POINT:
  Stop after the single file edit. Do not create other files.

ESCALATION PATH:
  If the file is not found at the exact path, output FAIL and stop. Do not create a new file.

APPROVAL STATE:
  APPROVED — Tony, 2026-05-18. File: docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md.
  Action: add Revision History section only.
```

---

## When to Use a Delegation Packet

A delegation packet is required whenever Claude Code is invoked for a task that:

- Reads or touches repository files
- Produces a report, audit finding, or documentation artifact
- Reviews or validates code, configuration, or documentation
- Proposes a refactor, architecture change, or dependency mapping
- Is being delegated by ChatGPT rather than directly instructed by the operator

A delegation packet is not required for:
- Simple conversational questions with no file system access
- Ad-hoc exploratory questions where no output is stored

When in doubt, use a delegation packet. The overhead is low; the protection is high.

---

## What Must Never Be in a Delegation Packet

The following must never appear as an allowed action or implied permission in a delegation packet:

| Prohibited Item | Reason |
|----------------|--------|
| Commit or push files | Requires explicit separate operator approval. |
| Edit secrets, tokens, credentials, or keys | Blocked by policy. No delegation packet may override. |
| Modify protected governance files (AGENTS.md, RISK_POLICY.md, etc.) | Requires User-level approval only. |
| Create automation, scripts, or launchers | Document first. Automate second. |
| Create frontend code or dashboards | Prohibited in current doctrine. |
| Enable broker connections or live trading | Blocked by policy. Cannot be delegated. |
| Open-ended APPLY scope ("edit any file that needs it") | Scope must name exact files and actions. |
| Autonomous re-invocation or self-continuation | Claude Code must stop at the stop point. |

---

## aios.ps1 Relationship

`aios.ps1` may, in a future documented stage, prepare Claude Delegation Packets as structured text
output for the operator to review and send manually.

`aios.ps1` must not:
- Automatically feed packets to Claude without operator review
- Auto-commit or auto-push outputs from Claude
- Run Claude unattended
- Bypass the operator approval gate between packet creation and packet use

Human approval remains required between packet preparation and Claude invocation. The packet is
a prepared brief, not an automated trigger.

This direction is documented here as intent. Implementation requires a separate approved workload
pack.

---

## Delegation Packet Governance

This standard is owned by the AI_OS documentation governance layer. Changes to the required fields
or prohibited items require:

1. A DRY_RUN review of impact on existing packets and worker outputs.
2. A decision record (see docs/decisions/).
3. Operator approval before any APPLY changes.

---

## Stop Point

This standard is documented. No packets are being sent. No automation is created.

Next safe step: operator reviews the packet structure, confirms the nine required fields, and
determines whether example packets should be drafted for the most common Claude use cases in the
current phase.

---

*AI_OS Claude Delegation Standard — v0.1 DRAFT*
*Produced: 2026-05-18 | Mode: APPLY (documentation only) | Approved by: Tony 2026-05-18*
