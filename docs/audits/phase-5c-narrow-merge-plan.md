# Phase 5C Narrow Merge Plan

Status: surgical canonical merge preparation only
Branch: `v2/aios`
Source audit: `docs/audits/phase-5b-canonical-doc-compare.md`

This is a planning document. It does not edit canonical docs, source docs, runtime systems, orchestration, workers, telemetry, approvals, packets, dashboard runtime, trading systems, launchers, credential paths, broker configuration, archive material, or protected governance files.

## Executive Summary

Phase 5B proved that V2 canonical docs already absorbed the main CLEAN-era intelligence. The remaining value is narrow operational detail, not whole-document promotion.

The first surgical merge batch should promote only:

1. Worker allowed lane list.
2. Worker validator command references.
3. APPLY state definitions rewritten with V2 `review package` wording.

The granular ownership table details are useful but should not be included in the first batch. They need a user decision because they can make the canonical ownership map heavier and can accidentally revive `docs/AI_OS/` as active authority if copied carelessly.

## Exact Candidate Summary

| Candidate | Source section | Target file | Recommendation | First batch |
|---|---|---|---|---|
| Granular ownership table details | `## Folder Ownership Table` | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | needs user decision | no |
| Worker allowed lane list | `## Allowed Worker Lanes` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | promote | yes |
| Worker validator command references | `## Validation` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | partially promote | yes |
| APPLY state definitions | `## State Definitions` | `docs/workflows/APPLY_ROUTING_CHAIN.md` | partially promote | yes |

## Candidate 1: Granular Ownership Table Details

| Field | Detail |
|---|---|
| Source file | `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` |
| Exact source heading/section | `## Folder Ownership Table` |
| Target canonical file | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` |
| Exact insertion location | After the existing `## Ownership Table` and before `## Topic Ownership` |
| Recommended target heading | `## Operational Ownership Review Fields` |
| Recommendation | needs user decision |

### Content Summary

Promote only the review-field concept from the source table:

- `Related folders`
- `Current status`
- `Recommended correction`
- `Approval needed before writes?`

Do not promote the full source table.

### Why V2 Benefits

The V2 ownership map already defines folder path, owner category, allowed contents, blocked contents, and risk. The source adds operational review dimensions that help future consolidation work explain connected folders, current state, correction path, and approval requirements.

### What Canonical Already Handles Better

- `docs/` is the active V2 documentation root.
- `docs/AI_OS/` is explicitly legacy/CLEAN-era source material pending repointing.
- The ownership table is shorter and more readable.
- Archive-before-delete doctrine is already present.

### Duplicate Wording That Must NOT Survive

- Full duplicate ownership rows.
- Duplicate protected-root boundary wording.
- Duplicate source-of-truth folder map.
- Any table row copied wholesale when a canonical row already exists.

### Stale CLEAN-Era Assumptions To Reject

- `docs/AI_OS/` as canonical planning root.
- `docs/AI_OS/telemetry/`, `docs/AI_OS/dashboard/`, `docs/AI_OS/brokers/`, and similar paths as final V2 authority destinations.
- `Reports/` as anything other than generated output unless separately governed.
- `agent/` assumptions that may not match current V2 runtime ownership.

### Risks

| Risk type | Assessment |
|---|---|
| Operational | Medium: copying rows wholesale can confuse active ownership. |
| Governance | High: source table conflicts with V2 canonical authority path. |
| Security | Medium: wrong placement rules can weaken protected path handling. |
| Maintainability | High: a second large table can increase cognitive load. |
| Dependency | Medium: folder names may not match current runtime wiring. |

### Validation Required Before Merge

- User decides whether canonical ownership should stay concise or include operational review fields.
- Validate current active folder names before adding examples.
- Confirm no promoted wording makes `docs/AI_OS/` active authority.

### Exact Promotion Text If Approved Later

Add this section after `## Ownership Table`:

```markdown
## Operational Ownership Review Fields

Future ownership-map updates may include these review fields when needed:

- Related folders: connected source, output, runtime, or documentation paths.
- Current status: whether the folder is active, legacy, generated, blocked, or pending decision.
- Recommended correction: the proposed governance or placement action.
- Approval needed before writes: whether edits require explicit user approval.

These fields support cleanup planning. They do not make `docs/AI_OS/` active V2 authority and do not approve file moves, deletes, runtime changes, broker execution, or protected-root edits.
```

### Archive-Only / Reject

Archive-only:

- Source `## Source-Of-Truth Folder Map`
- Full source ownership rows for `docs/AI_OS/...`
- CLEAN-era active status language

Reject:

- Any instruction that makes `docs/AI_OS/` the V2 source of truth.
- Any copied row that duplicates canonical rows without adding current V2 value.

## Candidate 2: Worker Allowed Lane List

| Field | Detail |
|---|---|
| Source file | `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` |
| Exact source heading/section | `## Allowed Worker Lanes` |
| Target canonical file | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` |
| Exact insertion location | After `## Required Lane Metadata` and before `## Path Ownership` |
| Recommended target heading | `## Allowed Worker Lanes` |
| Recommendation | promote |

### Content Summary

Promote the exact allowed worker lane names:

- `Work Intelligence`
- `Operator Orchestration`
- `Dashboard UI`
- `Trading Lab`
- `Validators`
- `Reports`
- `Mock Data`

Promote the rule that any lane outside the list is `UNKNOWN` until the operator approves and documents it.

### Why V2 Benefits

The canonical worker rules require `worker lane` metadata but do not define approved lane names. The lane names are already referenced in Work Intelligence automation, so placing the approved list in the canonical workflow reduces hidden authority.

### What Canonical Already Handles Better

- Branch naming is already concise.
- Required lane metadata is already present.
- Path ownership blocks already cover protected root files, secrets, dashboard assignment, trading execution logic, broker/OANDA/webhook/live execution, and real order paths.
- Collision handling is already canonical.

### Duplicate Wording That Must NOT Survive

- The source purpose paragraph if it implies source authority.
- Repeated path rules already covered by canonical `## Path Ownership`.
- Repeated safety language already covered by canonical text and AGENTS.md.

### Stale CLEAN-Era Assumptions To Reject

- Any implication that the source file remains active authority after promotion.
- Any implication that the lane list creates branches, worktrees, workers, commits, pushes, or merges.

### Risks

| Risk type | Assessment |
|---|---|
| Operational | Low: lane names are already referenced by automation. |
| Governance | Medium: list may later belong in a worker registry. |
| Security | Low: list does not grant permissions by itself. |
| Maintainability | Low: adding the list makes the workflow clearer. |
| Dependency | Medium: lane names should stay aligned with Work Intelligence automation. |

### Validation Required Before Merge

- Confirm lane names remain current.
- Confirm whether a later worker registry should supersede this list.
- Prep reference check found lane references in `automation/work_intelligence/Invoke-AiOsWorkIntelligenceScan.ps1` and `automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1`.

### Exact Promotion Text

Add this section after `## Required Lane Metadata`:

```markdown
## Allowed Worker Lanes

Allowed worker lanes are:

- Work Intelligence
- Operator Orchestration
- Dashboard UI
- Trading Lab
- Validators
- Reports
- Mock Data

Any lane outside this list is `UNKNOWN` until the operator approves and documents it.
```

### Archive-Only / Reject

Archive-only:

- Source branch examples unless the user specifically wants examples in canonical workflow docs.

Reject:

- Any lane permission expansion.
- Any language that weakens path ownership.

## Candidate 3: Worker Validator Command References

| Field | Detail |
|---|---|
| Source file | `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` |
| Exact source heading/section | `## Validation` |
| Target canonical file | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` |
| Exact insertion location | After `## Collision Handling` |
| Recommended target heading | `## Validation` |
| Recommendation | partially promote |

### Content Summary

Promote the command references:

- `powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1`
- `powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1`
- `git diff --check`
- `git status --short --branch`

Add V2 safety language that these commands validate evidence only and do not approve changes.

### Why V2 Benefits

The canonical worker workflow explains collision handling but does not list the validation chain operators should use for worker evidence. The source commands point to existing validators, making this useful operational content.

### What Canonical Already Handles Better

- Canonical states the workflow does not create branches, worktrees, commits, pushes, or merges.
- Canonical keeps worker lane/path rules short.
- Canonical uses V2 wording rather than CLEAN-era active-source wording.

### Duplicate Wording That Must NOT Survive

- Any sentence implying validation is approval.
- Any duplicate safety paragraph that repeats AGENTS.md.
- Any source wording implying validator execution is automatic.

### Stale CLEAN-Era Assumptions To Reject

- Validators as merge approval.
- Validators as APPLY approval.
- Validators as authority to edit files.

### Risks

| Risk type | Assessment |
|---|---|
| Operational | Medium: command references can become stale. |
| Governance | Medium: validator chain may later move to a validator registry. |
| Security | Low: commands are local validation references; no secrets or broker paths are introduced. |
| Maintainability | Medium: canonical docs must not overfit to script paths if tooling moves. |
| Dependency | Medium: scripts must exist and remain authoritative. |

### Validation Required Before Merge

- Confirm script existence.
- Confirm scripts are still intended worker validators.
- Prep check result:
  - `automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1`: exists.
  - `automation/operator/Test-AiOsParallelWorkerReports.ps1`: exists.

### Exact Promotion Text

Add this section after `## Collision Handling`:

````markdown
## Validation

Worker branch and lane reviews may use:

```powershell
powershell -ExecutionPolicy Bypass -File automation/work_intelligence/Test-AiOsWorkIntelligenceScan.ps1
powershell -ExecutionPolicy Bypass -File automation/operator/Test-AiOsParallelWorkerReports.ps1
git diff --check
git status --short --branch
```

These commands validate evidence only. They do not approve APPLY, create branches, create worktrees, stage files, commit, push, merge, or change runtime state.
````

### Archive-Only / Reject

Archive-only:

- Source `## Safety` section, because canonical already covers non-automation.

Reject:

- Any validator wording that implies automatic repair, APPLY, merge, commit, push, runtime mutation, dashboard mutation, trading mutation, or telemetry mutation.

## Candidate 4: APPLY State Definitions

| Field | Detail |
|---|---|
| Source file | `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` |
| Exact source heading/section | `## State Definitions` |
| Target canonical file | `docs/workflows/APPLY_ROUTING_CHAIN.md` |
| Exact insertion location | After `## Chain` and before `## Required Evidence` |
| Recommended target heading | `## State Definitions` |
| Recommendation | partially promote |

### Content Summary

Promote short state definitions for:

- `DRY_RUN`
- `validation`
- `approval request`
- `APPLY candidate`
- `exact-file evidence`
- `review package`

Rewrite the final state from source `merge-ready package` to canonical `review package`.

### Why V2 Benefits

The canonical APPLY routing chain lists the sequence but does not define the states. Definitions reduce ambiguity and support review-before-apply safety without adding a second authority file.

### What Canonical Already Handles Better

- Uses `review package`, not `merge-ready package`.
- Blocks broker, OANDA, API, webhook, and live trading scope.
- Clear non-automation statement for APPLY, edit, stage, commit, push, merge, broker logic, and live trading logic.

### Duplicate Wording That Must NOT Survive

- `merge-ready package`
- Repeated required evidence fields already present in canonical.
- Repeated blocked conditions already present in canonical.
- Repeated non-automation text already present in canonical.

### Stale CLEAN-Era Assumptions To Reject

- Merge readiness as an output state.
- Any implication that evidence completion triggers merge, APPLY, commit, push, or staging.

### Risks

| Risk type | Assessment |
|---|---|
| Operational | Low: definitions clarify existing workflow. |
| Governance | Low: canonical wording remains intact. |
| Security | Low: no credential or execution path is introduced. |
| Maintainability | Low: definitions reduce ambiguity. |
| Dependency | Low: no runtime dependency. |

### Validation Required Before Merge

- Confirm wording aligns with AGENTS.md DRY_RUN/APPLY doctrine.
- Confirm `review package` remains the only final chain term.

### Exact Promotion Text

Add this section after `## Chain`:

```markdown
## State Definitions

`DRY_RUN` means the task has a plan and no files are changed.

`validation` means required validators are identified or run by explicit operator instruction.

`approval request` means the operator is asked to approve exact files and scope.

`APPLY candidate` means the task is ready for approved file edits only.

`exact-file evidence` means changed files and validation output are available for review.

`review package` means evidence is complete enough for operator review. It does not execute merge, commit, push, or APPLY.
```

### Archive-Only / Reject

Archive-only:

- Source `## Chain` because canonical already has the better chain.
- Source `## Required Evidence`, `## Blocked Conditions`, and `## What This Does Not Automate` because canonical already covers them.

Reject:

- `merge-ready package`
- Any language that turns review evidence into execution authority.

## Unsafe Legacy Sections

| Source section | Exact unsafe content | Handling |
|---|---|---|
| `AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` / `## Folder Ownership Table` | Rows positioning `docs/AI_OS/` as active planning root | Archive-only; do not promote as V2 authority |
| `AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` / `## Source-Of-Truth Folder Map` | CLEAN-era source-of-truth paths under `docs/AI_OS/...` | Archive-only; conflicts with V2 canonical structure |
| `AIOS_APPLY_ROUTING_CHAIN.md` / `## Chain` and `## State Definitions` | `merge-ready package` | Reject; use `review package` |
| `AIOS_WORKER_BRANCH_AND_LANE_RULES.md` / `## Safety` | Repeated source safety framing | Archive-only; canonical already covers non-automation |

## Governance Conflicts

| Conflict | Decision |
|---|---|
| `docs/AI_OS/` source material vs active V2 authority under `docs/` | Keep V2 canonical authority under `docs/governance/` and `docs/workflows/`. |
| Full ownership table vs concise canonical map | Do not copy table wholesale. User decision required for operational review fields. |
| Worker lane list in workflow doc vs future worker registry | Promote now as current workflow authority; revisit if a registry is created. |
| Validator commands in workflow doc vs future validator registry | Promote command references with evidence-only wording; revisit if validator registry becomes canonical. |

## Dependency Concerns

- Worker lane names are referenced by Work Intelligence automation and should not be changed during the merge.
- Validator command paths exist now but can become stale if automation moves.
- Ownership-map details may refer to folder paths that are historical, generated, or unresolved.
- APPLY state definitions have no runtime dependency but must remain aligned with AGENTS.md.

## Security Concerns

- Do not add any broker, OANDA, webhook, API, credential, or live trading enablement.
- Do not weaken operator approval.
- Do not imply validators approve execution.
- Do not make runtime, dashboard, telemetry, packet, approval, or launcher paths editable through documentation wording.
- Do not expose or request secrets.

## User Decisions Needed

1. Should `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` gain an `Operational Ownership Review Fields` section, or should that detail remain audit-only?
2. Should worker lane names live permanently in `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`, or eventually move to a worker registry?
3. Should validator command references live permanently in the worker workflow doc, or eventually move to a validator registry?

## First Surgical Merge Batch Recommendation

Approve Phase 5D for only these edits:

1. Edit `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`.
2. Insert `## Allowed Worker Lanes` after `## Required Lane Metadata`.
3. Insert `## Validation` after `## Collision Handling`.
4. Edit `docs/workflows/APPLY_ROUTING_CHAIN.md`.
5. Insert `## State Definitions` after `## Chain`.
6. Run `git diff --check`.
7. Run `git status --short --branch`.

Do not include `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` in the first edit batch unless the user explicitly approves Candidate 1.

## Explicitly Untouched

- CLEAN-era source docs were inspected only.
- V2 canonical docs were inspected only.
- Runtime systems were not touched.
- Orchestration systems were not touched.
- Worker systems were not touched.
- Telemetry systems were not touched.
- Approval systems were not touched.
- Packet systems were not touched.
- Dashboard runtime was not touched.
- Trading systems were not touched.
- Launchers were not touched.
- Credential paths, broker configuration, execution logic, and secrets handling were not touched.
- `archive/` was not touched.
- No files were moved, deleted, renamed, staged, committed, or pushed.
