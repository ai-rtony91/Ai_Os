# AI_OS Worker Interface Architecture Specification
**Document Type:** Interface Standard Draft
**Version:** 0.1
**Status:** DRAFT — Operator Review Required Before Any Implementation
**Execution Mode:** APPLY (documentation only)
**Approval State:** APPROVED by operator 2026-05-18
**Files Changed:** This file only — docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md

---

## 1. Core Interface Philosophy

The AI_OS worker interface exists to make execution state **unambiguous at a glance**. Every worker
output — whether in a terminal, a log file, or a future dashboard panel — must answer three questions
without the operator needing to read prose:

1. **Who** produced this output and under whose authority?
2. **What mode** is this execution in (DRY_RUN, APPLY, BLOCKED)?
3. **What is the current safety posture** (approval state, audit trail, escalation needed)?

This is modeled on the operational discipline of the Claude Code terminal UI: boxed regions, short
status labels, consistent indentation, and color-coded severity that communicates intent before
content. The interface is **human-first, not data-first**. Operators absorb state in seconds, not
after reading paragraphs.

**Governing principle:** If the operator must read a sentence to know whether something is safe to
proceed, the interface has failed.

**DRY_RUN is the default posture.** No worker may default to APPLY. Every worker output that touches
files must be preceded by a visible DRY_RUN preview. APPLY only becomes reachable after explicit
operator approval that names the exact mode, file, path, and action.

---

## 2. Terminology Definitions

### 2a. Execution Mode Terms

| Term | Definition |
|------|------------|
| `DRY_RUN` | Worker produces output but makes no file changes. Preview-only. Safe to read and share. The default mode for all workers. |
| `APPLY` | Worker makes file changes or takes an action with real-world effect. Requires prior explicit operator approval. |
| `BLOCKED` | A worker attempted an action that is prohibited by policy. The action did not execute. The worker halted and reported the block. |
| `PAUSED` | Worker reached a checkpoint and is awaiting operator instruction before continuing. No further action taken. |
| `SKIPPED` | An action was within scope but was deliberately not executed, usually because a dependency was missing or a safety rule prevented it. |

### 2b. Authority Terms

| Term | Definition |
|------|------------|
| `User` | The human operator. Highest authority. Only the User can approve APPLY work, exit SAFE_MODE, or unlock trading execution. |
| `Supervisor` | A worker (e.g. ChatGPT-Architect) delegated by the User to coordinate other workers. May instruct sub-workers but cannot grant APPLY approval. |
| `Autonomous` | A worker operating without a traceable human instruction in its authority chain. This state is always BLOCKED in AI_OS. |

### 2c. Safety Posture Terms

| Term | Definition |
|------|------------|
| `SAFE_MODE` | Maximum restriction posture. No destructive actions permitted. All writes require explicit operator approval. |
| `AUDIT_MODE` | Maximum logging posture. All reads, decisions, and outputs are recorded. Does not by itself restrict execution. |
| `PROTECTED` | A specific file or path that no worker may modify without an explicit unlock instruction from the User. |
| `TRADING_BLOCKED` | Broker orders and live trading execution are blocked. Cannot be bypassed by any worker. Requires a separate explicit human unlock. |
| `LIVE_BLOCKED` | Live execution in any domain is blocked. Requires separate explicit human unlock. |

---

## 3. Worker Identity Standard

Every worker output block must open with an identity header. The header is non-negotiable. No worker
output is valid without it.

### 3a. Required Identity Fields

```
┌─────────────────────────────────────────────────────────────────────┐
│  WORKER          │  <WorkerName>                                     │
│  ROLE            │  <architect | executor | reviewer | auditor>      │
│  AUTHORITY       │  <User | Supervisor: <name> → User | Autonomous>  │
│  SESSION         │  <YYYY-MM-DD HH:MM>                              │
│  EXECUTION MODE  │  <DRY_RUN | APPLY | BLOCKED>                     │
│  APPROVAL STATE  │  <PENDING | APPROVED | NOT_REQUIRED | DENIED>     │
└─────────────────────────────────────────────────────────────────────┘
```

**WorkerName examples from the AI_OS architecture:**
- `ChatGPT-Architect`
- `Codex-Executor`
- `ClaudeCode-Reviewer`
- `MorningBrief-Generator`
- `ReportWriter`
- `DailyMetrics-Helper`
- `RepoHealth-Helper`
- `SessionEvidence-Helper`
- `CheckpointDraft-Helper`

### 3b. Worker Identity Example — DRY_RUN

```
┌─────────────────────────────────────────────────────────────────────┐
│  WORKER          │  ReportWriter                                     │
│  ROLE            │  executor                                         │
│  AUTHORITY       │  Supervisor: ChatGPT-Architect → User (Tony)      │
│  SESSION         │  2026-05-18 09:00                                │
│  EXECUTION MODE  │  DRY_RUN                                         │
│  APPROVAL STATE  │  NOT_REQUIRED                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3c. Worker Identity Example — APPLY (Approved)

```
┌─────────────────────────────────────────────────────────────────────┐
│  WORKER          │  Codex-Executor                                   │
│  ROLE            │  executor                                         │
│  AUTHORITY       │  Supervisor: ChatGPT-Architect → User (Tony)      │
│  SESSION         │  2026-05-18 09:14                                │
│  EXECUTION MODE  │  APPLY                                           │
│  APPROVAL STATE  │  APPROVED — Tony, 2026-05-18 09:12               │
└─────────────────────────────────────────────────────────────────────┘
```

### 3d. Supervisor Chain Display

When a worker operates under delegation, the full chain must be visible:

```
│  AUTHORITY  │  Supervisor: ChatGPT-Architect → User (Tony)          │
```

For chains deeper than one level:

```
│  AUTHORITY  │  User (Tony) → ChatGPT-Architect → Codex → ReportWriter  │
```

Chain depth must be shown in full. A three-level chain must display all three steps. The operator
must be able to trace authority back to the User without asking.

---

## 4. Required Layout Regions

Every worker output document must contain these seven regions in this order. Regions may be empty
but must be labeled. Omitting a region is not permitted.

```
┌── [1] IDENTITY HEADER ──────────────────────────────────────────────┐
│   Worker name, role, authority, session, mode, approval state       │
└─────────────────────────────────────────────────────────────────────┘

┌── [2] SCOPE DECLARATION ────────────────────────────────────────────┐
│   What this worker is allowed to touch and not allowed to touch     │
│   Files in scope:     <exact paths>                                 │
│   Files out of scope: <exact paths or policy reference>             │
│   Escalation path:    <this worker → supervisor → User>             │
└─────────────────────────────────────────────────────────────────────┘

┌── [3] EXECUTION RESULT ─────────────────────────────────────────────┐
│   Task / Action / Output                                            │
│   One action per line. No prose. Short labels.                     │
└─────────────────────────────────────────────────────────────────────┘

┌── [4] FINDINGS ─────────────────────────────────────────────────────┐
│   PASS / WARN / FAIL / UNKNOWN / MISMATCH / INVALID DATA            │
│   Critical findings (FAIL, BLOCKED) appear before WARN and PASS     │
└─────────────────────────────────────────────────────────────────────┘

┌── [5] AUDIT TRAIL ──────────────────────────────────────────────────┐
│   Files inspected | Files changed | Protected files encountered     │
└─────────────────────────────────────────────────────────────────────┘

┌── [6] APPROVAL GATE ────────────────────────────────────────────────┐
│   What requires human approval before proceeding                    │
│   Exact mode / file / path / action that needs sign-off             │
│   Empty state: "No approval required."                              │
└─────────────────────────────────────────────────────────────────────┘

┌── [7] NEXT SAFE ACTION ─────────────────────────────────────────────┐
│   One instruction. Exact. Not optional.                             │
│   Empty state: "No further action required."                        │
└─────────────────────────────────────────────────────────────────────┘
```

**Regions 6 and 7 are mandatory even when empty.** An empty region must display its empty-state
label. The operator must always see the approval gate and next action slots — even blank ones
confirm that the worker considered and cleared them.

### 4a. Complete 7-Region Example Output

```
┌─────────────────────────────────────────────────────────────────────┐
│  WORKER          │  RepoHealth-Helper                                │
│  ROLE            │  auditor                                          │
│  AUTHORITY       │  Supervisor: ChatGPT-Architect → User (Tony)      │
│  SESSION         │  2026-05-18 09:00                                │
│  EXECUTION MODE  │  DRY_RUN                                         │
│  APPROVAL STATE  │  NOT_REQUIRED                                     │
└─────────────────────────────────────────────────────────────────────┘

─────────────────────────────────────────────────────────────────────
[2] SCOPE DECLARATION

  Files in scope:    C:\Dev\Ai.Os\
  Files out of scope: C:\Users\mylab\OneDrive\AI-OS-Project\TradingEngineV1\
  Protected:         Root files, AGENTS.md, secrets, credentials
  Escalation path:   This worker → ChatGPT-Architect → User (Tony)

─────────────────────────────────────────────────────────────────────
[3] EXECUTION RESULT

  Checked: repo health chain .............. complete
  Checked: protected file list ............ complete
  Checked: validator status ............... complete (1 WARN)
  Skipped: metrics row .................... helper missing

─────────────────────────────────────────────────────────────────────
[4] FINDINGS

  ├─ repo health ..................... PASS
  ├─ protected files ................. PASS
  ├─ validator ........................ WARN  (daily-validator helper not found)
  └─ metrics row ..................... UNKNOWN  (helper missing, treat as WARN)

─────────────────────────────────────────────────────────────────────
[5] AUDIT TRAIL

  Files read:     3
  Files changed:  0
  Protected files encountered: 0
  Audit log:      N/A (AUDIT_MODE not active this session)

─────────────────────────────────────────────────────────────────────
[6] APPROVAL GATE

  No approval required.
  (DRY_RUN output only — no APPLY actions in scope.)

─────────────────────────────────────────────────────────────────────
[7] NEXT SAFE ACTION

  Provide the missing daily-validator helper path to resolve the WARN finding,
  then re-run RepoHealth-Helper to confirm PASS status.
```

---

## 5. Status Label System

Status labels are the atomic unit of worker communication. They must be short, uppercase, and
consistent across all workers and sessions. New label variants are not permitted without a
documented revision to this specification.

### 5a. Execution Mode Labels

| Label | Meaning | Trigger |
|-------|---------|---------|
| `DRY_RUN` | No files changed. Output is preview-only. Safe to read. | Default state for all workers. |
| `APPLY` | Files were or will be changed. | Requires prior explicit operator approval. |
| `BLOCKED` | Action attempted and halted by policy. No output produced. | Any prohibited action detected. |
| `PAUSED` | Worker halted at a checkpoint. Awaiting human instruction. | Worker reaches a gate. |
| `SKIPPED` | Action was in scope but deliberately not executed. | Missing helper, safety rule, dependency absent. |

### 5b. Finding Labels

| Label | Meaning | Operator Response |
|-------|---------|------------------|
| `PASS` | Condition verified and met. | No action needed. |
| `WARN` | Condition borderline or missing. Review recommended. | Investigate before proceeding. |
| `FAIL` | Condition not met. Do not proceed. | Stop. Escalate or fix before continuing. |
| `UNKNOWN` | Could not be verified. Treat as WARN. | Verify before proceeding. |
| `MISMATCH` | Observed state conflicts with prior record. Log immediately. | Stop. Log in ERROR_LOG.md. Escalate. |
| `INVALID DATA` | Evidence cannot be verified against files or terminal output. | Stop. Do not act on unverified data. |
| `BLOCKED` | Action cannot proceed by policy. | Acknowledge block. Do not attempt to bypass. |

### 5c. Approval State Labels

| Label | Meaning |
|-------|---------|
| `NOT_REQUIRED` | DRY_RUN output. No approval gate applies. |
| `PENDING` | Approval needed before any APPLY action proceeds. Worker is paused. |
| `APPROVED` | Human named exact mode, file, path, action. Record includes approver name and timestamp. |
| `DENIED` | Human rejected. Worker must stop and not retry without a new explicit instruction. |
| `EXPIRED` | Prior approval is stale. Re-approval required before APPLY proceeds. |

### 5d. Safety and Restriction Labels

| Label | Meaning |
|-------|---------|
| `SAFE_MODE` | Worker operating under maximum restriction. No destructive actions. |
| `AUDIT_MODE` | Worker logging all reads and decisions. No writes without separate approval. |
| `PROTECTED` | File or path is protected. No changes without explicit unlock from User. |
| `TRADING_BLOCKED` | Trading and broker execution blocked. Cannot be bypassed by worker policy. |
| `LIVE_BLOCKED` | Live execution blocked. Requires separate explicit human unlock. |

---

## 6. Color Semantic Guidance

Colors are **secondary to labels, not primary.** The interface must be fully readable in
monochrome — in a plain log file, in a terminal with colors disabled, or in a printed document.
Color adds speed for operators who are scanning; it never substitutes for a text label.

| Color | Semantic Role | Used For |
|-------|--------------|---------|
| Red | Stop / Blocked / Fail | FAIL, BLOCKED, DENIED, TRADING_BLOCKED, LIVE_BLOCKED |
| Yellow / Amber | Caution / Review | WARN, UNKNOWN, MISMATCH, PENDING |
| Green | Clear / Pass | PASS, APPROVED, DRY_RUN complete without errors |
| Blue | Informational / Identity | Worker name, role, session header |
| White / Default | Standard output | Body text, scope declarations, audit trail |
| Dim / Gray | Suppressed / Not applicable | SKIPPED, NOT_REQUIRED, out-of-scope items |
| Cyan | Mode indicator | DRY_RUN label, APPLY label, mode badge in identity header |
| Magenta / Purple | Authority / Escalation | Supervisor chain display, escalation path, authority warnings |

### 6a. Terminal Fallback Rule

When color is unavailable, prefix every status with a bracketed text label:

```
[FAIL]    repo health check failed
[WARN]    validator helper not found
[PASS]    protected files — no violations
[UNKNOWN] metrics row helper — cannot verify
```

Labels are always present. Color is never the only indicator. A worker output that relies on color
alone to communicate a FAIL state is non-compliant with this standard.

### 6b. Color Application Priority

Apply color to the **label only**, not to the entire line. This preserves readability and avoids
color fatigue:

```
  ├─ repo health ..... [green]PASS[/green]
  ├─ validator ....... [yellow]WARN[/yellow]  (helper not found)
  └─ metrics row ..... [yellow]UNKNOWN[/yellow]
```

---

## 7. Box and Panel Conventions

### 7a. Terminal Box Format

Use single-line box-drawing characters for standard terminal output:

```
┌─────────────────────────────────────────────────────────────┐
│  LABEL   │  Value                                           │
└─────────────────────────────────────────────────────────────┘
```

Nested sub-sections use indent with a pipe-and-dash tree prefix:

```
┌── FINDINGS ───────────────────────────────────────────────────┐
│  ├─ repo health .............. PASS                            │
│  ├─ protected files ........... PASS                           │
│  ├─ validator ................. WARN  (missing helper)         │
│  └─ metrics row ............... UNKNOWN                        │
└───────────────────────────────────────────────────────────────┘
```

Dot leaders align values to a fixed column. This is the AI_OS standard — not prose, not tables.

### 7b. Double-Line Box — Reserved Use Only

Double-line boxes (═) are reserved exclusively for SAFE_MODE and TRADING_BLOCKED banners. Nothing
else uses double-line borders. This visual distinction means any double-line box is immediately
recognizable as a critical safety state.

```
╔═══════════════════════════════════════════════════════════════╗
║  [ SAFE MODE ACTIVE ]   No destructive actions permitted.    ║
║  All writes require explicit operator approval.              ║
╚═══════════════════════════════════════════════════════════════╝
```

### 7c. Section Separators

Between layout regions, use a blank line plus a thin horizontal rule:

```
─────────────────────────────────────────────────────────────────
```

Not a box — just a rule. Boxes are reserved for defined regions; rules are region separators.

### 7d. Panel Width Standard

- Terminal target: **80 characters** — works in any terminal; no word-wrap risk
- Extended terminal: up to **120 characters** when extra columns are available
- Dashboard panel: follow the dashboard grid unit; never overflow a panel boundary

### 7e. Density Principle

One finding per line. No merged findings. No labels wrapping across lines. A finding that needs
more than one line of explanation is a **note** — notes belong in the body text below the finding
line, indented with two spaces and no status label prefix.

---

## 8. Safe Mode Indicators

Safe mode must be the **most visible element** on any output where it is active. It must not be
buried in the identity header. It repeats as a banner immediately after the identity header and
again immediately before the Approval Gate region.

### 8a. Safe Mode Banner — Terminal

```
╔═══════════════════════════════════════════════════════════════╗
║  [ SAFE MODE ACTIVE ]   No destructive actions permitted.    ║
║  All writes require explicit operator approval.              ║
╚═══════════════════════════════════════════════════════════════╝
```

### 8b. Safe Mode in Identity Header

```
│  EXECUTION MODE  │  DRY_RUN  [ SAFE_MODE ACTIVE ]            │
```

### 8c. Safe Mode Exit Gate

Any transition out of safe mode requires an entry in the Approval Gate region and must name the
exact mode, file, path, and action being unlocked:

```
┌── [6] APPROVAL GATE ────────────────────────────────────────────────┐
│  EXIT_SAFE_MODE requires explicit User (Tony) approval.             │
│  Approval must name: mode, file, path, action.                      │
│  Approval state: PENDING                                            │
└─────────────────────────────────────────────────────────────────────┘
```

Safe mode can only be exited by the `User` authority level. Supervisor-delegated workers cannot
exit safe mode independently.

---

## 9. Audit Mode Indicators

Audit mode is distinct from safe mode. Safe mode restricts execution. Audit mode maximizes logging
without necessarily restricting execution. Both may be active simultaneously.

### 9a. Audit Mode Banner

```
┌─────────────────────────────────────────────────────────────────────┐
│  [ AUDIT MODE ACTIVE ]  All reads, decisions, and outputs logged.   │
│  Log destination:  <exact file path>                                │
│  Log start:        <YYYY-MM-DD HH:MM>                              │
└─────────────────────────────────────────────────────────────────────┘
```

Single-line box, not double-line. Blue label. Not as visually severe as safe mode.

### 9b. Audit Trail Region Content When Audit Mode Active

```
┌── [5] AUDIT TRAIL ──────────────────────────────────────────────────┐
│  [ AUDIT MODE ACTIVE ]                                              │
│  Audit log:      docs/AI_OS/audits/session-2026-05-18.log           │
│  Log format:     AIOS-audit-v1                                      │
│  Log start:      2026-05-18 09:00                                   │
│  Files read:     7                                                  │
│  Decisions:      4                                                  │
│  Writes:         NONE                                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 10. Approval-Required Indicators

Approval is the human gate between DRY_RUN and APPLY. It must be impossible to miss. Approval
banners appear in the Approval Gate region and, when critical, also as a standalone banner.

### 10a. Approval Pending Banner

```
┌─────────────────────────────────────────────────────────────────────┐
│  [ APPROVAL REQUIRED ]  Worker is paused.                           │
│  Action:      Write session evidence log to docs/AI_OS/audits/      │
│  Scope:       docs/AI_OS/audits/session-2026-05-18.log              │
│  Mode:        APPLY                                                 │
│  Approved by: PENDING                                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 10b. Approval Denied Display

```
┌─────────────────────────────────────────────────────────────────────┐
│  [ APPROVAL DENIED ]  Worker has stopped.                           │
│  No further action will be taken on this scope.                     │
│  To retry: issue a new explicit instruction.                        │
└─────────────────────────────────────────────────────────────────────┘
```

### 10c. Approval Granted Display

```
┌─────────────────────────────────────────────────────────────────────┐
│  [ APPROVED ]  Operator: Tony  |  2026-05-18 09:14                  │
│  Action:      Write session evidence log                            │
│  Scope:       docs/AI_OS/audits/session-2026-05-18.log              │
│  Mode:        APPLY                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

The approval record is immutable. It is reproduced verbatim in the Audit Trail region. The
approval must include: approver name, timestamp, exact action, exact scope, exact mode.

### 10d. What Cannot Be Approved by a Supervisor

The following actions require **User-level approval only**. No supervisor delegation is sufficient:

- Exiting SAFE_MODE
- Unlocking TRADING_BLOCKED or LIVE_BLOCKED
- Deleting, moving, or renaming any file
- Modifying protected files
- Git staging, commit, or push
- Credential, secret, token, or key changes
- Broker orders or live execution of any kind

---

## 11. Orchestration Hierarchy and Escalation Visibility

### 11a. Hierarchy Visualization Standard

When workers operate in a chain, the hierarchy must be visible in every output that is produced by
a delegated worker:

```
┌── ORCHESTRATION HIERARCHY ──────────────────────────────────────────┐
│                                                                     │
│  [User: Tony]  ──▶  [ChatGPT-Architect]                             │
│                           │                                         │
│                           ▼                                         │
│                     [Codex-Executor]   ←── current worker           │
│                           │                                         │
│                           ▼                                         │
│                    [ClaudeCode-Reviewer]  (optional pass)            │
│                           │                                         │
│                           ▼                                         │
│                     [User: Approval Gate]                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

The current worker is marked with `←── current worker`. All others are shown as context.

### 11b. Delegation Depth Warning

The interface must display a warning if the delegation depth exceeds 3 levels:

```
│  WARN: Delegation depth = 4. Verify authority chain integrity.       │
```

Depth greater than 3 is a signal to the operator that the chain may have drifted from the original
instruction. It does not automatically block execution but must be acknowledged.

### 11c. Autonomous Execution Block — Mandatory Display

If a worker detects it is being asked to operate without a traceable human instruction in its
authority chain, it must display:

```
╔═══════════════════════════════════════════════════════════════════╗
║  [ BLOCKED: AUTONOMOUS EXECUTION ]                               ║
║  No human instruction found in authority chain.                  ║
║  Worker will not proceed without explicit User command.          ║
╚═══════════════════════════════════════════════════════════════════╝
```

This is a hard block, not a warning. Autonomous execution is not permitted in AI_OS at any stage.

### 11d. Escalation Trigger Conditions

A worker must escalate to its supervisor when any of the following are detected:

- A `FAIL` finding appears in the Findings region
- A `MISMATCH` or `INVALID DATA` finding appears
- A protected file is encountered during APPLY scope
- A trading or broker action is within scope
- Delegation depth exceeds 3
- An `UNKNOWN` state that the current worker cannot resolve

### 11e. Escalation Display in Next Safe Action Region

```
┌── ESCALATION REQUIRED ──────────────────────────────────────────────┐
│  Reason:      MISMATCH detected in repo health check                │
│  Escalate to: ChatGPT-Architect (supervisor)                        │
│  Action:      Review findings and provide updated instruction.      │
│  Worker state: PAUSED                                               │
└─────────────────────────────────────────────────────────────────────┘
```

### 11f. Escalation Path Declaration

Each worker must declare its escalation path in the Scope Declaration region:

```
│  Escalation path:  This worker → ChatGPT-Architect → User (Tony)    │
```

---

## 12. Terminal-First Recommendations

### 12a. Format Priority Order

Apply these layers in order. Each layer must work without the next:

1. **Plain text with ASCII-safe characters** — works in every environment; no rendering dependency
2. **Box-drawing Unicode** (┌─┐│└┘) — works in modern terminals; graceful fallback to plain text
3. **ANSI color codes** — last layer; never used as the sole carrier of meaning
4. **Rich terminal libraries** (Rich, Textual) — acceptable for interactive tools only, never for
   log files or piped output

### 12b. Operator Readability Rules

- **No paragraphs in status output.** Status is labels plus values, not sentences.
- **One finding per line.** Dot-leader alignment to a fixed column.
- **Mode badge on line 1.** The operator sees `[DRY_RUN]` or `[APPLY]` before reading anything
  else.
- **Critical items at top.** FAIL and BLOCKED findings appear before WARN and PASS.
- **NEXT SAFE ACTION is the last visible element.** Operators read top-to-bottom; the actionable
  item is at the bottom.
- **Width discipline.** No line exceeds 80 characters in standard terminal output. No horizontal
  scrolling for status blocks.

### 12c. Logging Compatibility Rules

All terminal output must be safe to pipe to a log file without modification:

- No cursor control sequences in non-interactive output
- No progress bars or spinners in log-safe mode
- All ANSI color codes stripped automatically when output destination is not a TTY
- All Unicode box characters fall back to ASCII equivalents (`+`, `-`, `|`) when the terminal does
  not support Unicode

### 12d. One-Glance Scan Pattern

Terminal output must be readable by an operator doing a one-glance scan in this order:

```
Line 1:   Mode badge           → DRY_RUN or APPLY?
Line 2-6: Identity header      → Who? Under whose authority?
Line 7:   Safe mode banner     → Is anything restricted?
...
Findings: Critical items first → Any FAIL or BLOCKED?
Last line: Next safe action    → What do I do now?
```

If the scan pattern breaks — if the mode badge is buried, or the next action is in the middle, or
FAIL findings appear after PASS findings — the output is non-compliant.

---

## 13. Future Dashboard Compatibility Considerations

The terminal format described in this specification is the **authoritative source of truth**. A
dashboard is a projection of terminal output data, not an independent source of state. Dashboards
must read from the same data that the terminal produces; they must not generate their own findings.

### 13a. Terminal-to-Dashboard Panel Mapping

| Terminal Region | Dashboard Panel |
|----------------|----------------|
| [1] Identity Header | Worker status card (pinned bar or top-left) |
| [2] Scope Declaration | Collapsible detail panel |
| [3] Execution Result | Activity feed or log panel |
| [4] Findings | Status grid — PASS / WARN / FAIL indicators |
| [5] Audit Trail | Audit log panel — read-only, scrollable |
| [6] Approval Gate | Alert card — high-priority, never auto-collapsed |
| [7] Next Safe Action | Action prompt widget — pinned bottom or top |

### 13b. Dashboard Alert Severity Hierarchy

Following the existing AI_OS dashboard operator view draft:

1. `BLOCKED` / `FAIL` — Red. Always visible. Never collapsed.
2. `WARN` / `MISMATCH` — Amber. Visible. Can be acknowledged but not dismissed.
3. `PENDING` approval — Amber banner. Cannot be dismissed until approved or denied.
4. `PASS` / `INFO` — Green / Gray. Collapsible.

### 13c. Dashboard Must Not Create New State

Dashboards read and display worker output. They do not:
- Produce findings independently
- Create approval records
- Issue instructions
- Override worker mode labels

All authoritative state lives in terminal output and log files. If a dashboard shows PASS but the
terminal log says WARN, the terminal log is correct. Dashboards must be updated to match, not the
other way around.

### 13d. Keyboard Navigation Requirements

Future dashboard keyboard bindings must include at minimum:

| Keybinding Purpose | Status |
|-------------------|--------|
| Focus Approval Gate panel | Not yet implemented |
| Focus Next Safe Action | Not yet implemented |
| Focus Findings / Status Grid | Not yet implemented |
| Navigate worker hierarchy | Not yet implemented |
| Acknowledge WARN finding | Not yet implemented |

These are forward compatibility requirements. The dashboard rendering stack has not yet been
selected. Any stack selected must support these navigation patterns.

### 13e. Multi-Monitor Conceptual Layout

Future multi-monitor expansion (conceptual only, not yet implemented):

- Display 1: Analytics and daily metrics
- Display 2: Alerts, approval gate, and trading readiness boundary
- Display 3: Workflow state, morning brief, and next safe action

This layout follows the priority ordering established in the AI_OS Dashboard Operator View Layout
Draft (AIOS_DASHBOARD_OPERATOR_VIEW_LAYOUT_DRAFT.md).

---

## 14. Risks of Inconsistent Worker UX

If workers do not share a common interface standard, the following failure modes are predictable.
These are not hypothetical — they reflect the failure patterns that motivated this specification.

| Risk | Description | Severity |
|------|-------------|----------|
| **Mode confusion** | Operator cannot tell DRY_RUN from APPLY at a glance | Critical |
| **Silent APPLY** | Worker executes APPLY without a visible mode banner | Critical |
| **Approval bypass** | Worker proceeds without surfacing the approval gate | Critical |
| **Autonomous execution** | Worker operates without traceable human instruction | Critical |
| **Authority ambiguity** | Operator cannot trace who authorized an action | High |
| **Mismatch blindness** | Conflicting findings not labeled; operator proceeds with bad data | High |
| **Escalation invisibility** | Worker encountered FAIL but operator missed the escalation signal | High |
| **Audit gap** | Write occurred but not recorded in the audit trail | High |
| **Dashboard / terminal drift** | Dashboard shows PASS; terminal log says WARN; operator trusts wrong source | Medium |
| **Worker identity collision** | Two workers produce same-format output; operator cannot distinguish them | Medium |
| **Depth creep** | Delegation chain grows silently; operator loses visibility of authority chain | Medium |
| **Label drift** | Different workers invent their own label variants; vocabulary diverges over time | Medium |

**The single highest risk is silent APPLY.** A worker that changes files without surfacing the mode
indicator prominently is the failure this standard is primarily designed to prevent. Every other
risk is recoverable. Silent APPLY may not be.

---

## 15. Recommended Future Architecture

These are design decisions that should be made before any implementation begins. They are recorded
here as forward requirements, not as approved work items.

1. **Worker Output Schema** — A machine-readable schema (JSON or structured text) that mirrors the
   7 layout regions. Terminal rendering reads this schema. Dashboard rendering reads the same
   schema. One source of truth, two rendering paths.

2. **Mode Registry** — A single file that lists all valid execution modes and their rules. Workers
   validate their declared mode against the registry. New modes cannot be invented in worker output
   without a registry update.

3. **Approval Record Format** — A structured approval record format with a timestamp and approver
   name. Every APPLY action produces a record. The audit trail references the record. This closes
   the loop between approval and execution.

4. **Worker Registry** — A registry of known workers, their roles, their default authority levels,
   and their escalation paths. The identity header validates against this registry. An unknown
   worker name is flagged immediately.

5. **Audit Log Schema** — A machine-readable audit log format consistent with the AI_OS telemetry
   roadmap (see AIOS_PRODUCTION_TELEMETRY_ROADMAP_DRAFT.md). Terminal audit trail and dashboard
   audit panel read the same file.

6. **Safe Mode Authority Lock** — Safe mode exit is enforced at the schema level, not by
   convention. A worker output that declares an APPLY action while SAFE_MODE is active and
   APPROVAL STATE is not APPROVED by User must be rejected before execution.

---

## Stop Point

**This specification document is complete.**

### Scope Confirmation

| Item | Status |
|------|--------|
| Documentation file created | APPLY — this file |
| Frontend code produced | NONE |
| Dashboard implementation | NONE |
| Automation generated | NONE |
| Runtime behavior changed | NONE |
| Commits made | NONE |
| Pushes made | NONE |
| Files changed outside docs/AI_OS/interface/ | NONE |

### What Was Produced

One file: `docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md`

### Suggested Next Safe Step

Operator reviews sections 3 (Worker Identity), 4 (7-Region Layout), and 5 (Status Labels) and
confirms which elements are approved as stable standards. Specific decisions needed:

1. Approve or revise the 7-region layout order and mandatory regions
2. Approve or revise the status label vocabulary — especially any labels not yet seen in AI_OS output
3. Confirm color semantic assignments match the existing AI_OS dashboard theme system
   (see AIOS_DASHBOARD_THEME_SYSTEM_DRAFT.md)
4. Confirm the authority chain depth limit (this draft specifies: 3)
5. Decide whether a machine-readable worker output schema should be drafted next or whether
   the terminal text format is sufficient for the current stage

---

*AI_OS Worker Interface Architecture Specification — v0.1 DRAFT*
*Produced: 2026-05-18 | Mode: APPLY (documentation only) | Approved by: Tony 2026-05-18*
*File: docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md*
