# OCC worker-count: findings, rule proposal, and duplicate-case culprit

**Type:** ADVISORY · `executable=false` · read-only review
**Generated:** 2026-06-07
**Decision status:** **HELD by Human Owner.** No count chosen, no consumer wired,
nothing committed/pushed. The draft `automation/orchestration/workers/WORKER_FLEET.json`
has been **voided** (declares no count) so it cannot become another stray source.

---

## 1. The mistake (root cause)

The OCC worker count is **hard-coded independently in ~6 places** instead of being
read from one source, so the values have drifted to **four different numbers**:

| Value | Where | Nature |
|------|-------|--------|
| **4** | `aios.ps1:7` `[int]$WorkerCount = 4` (passed to the launcher at `aios.ps1:310-311`); `mission_plan.json`; `apps/dashboard/mock-data/aios-command-center-state*.json` `total_workers:4` | **Functional runtime default** |
| **5** | `aios.ps1:90,364` `"5-WORKER TERMINAL LAYOUT"` banner; `docs/CODEX_TERMINAL_MIGRATION_PACKET.txt` | **Cosmetic** (Write-Host text, no effect) |
| **8** | `automation/operator/Test-AiOsWorkerAutoRouting.DRY_RUN.ps1:149` "must include 8 workers"; dashboard `worker-auto-routing` / `worker-production` fixtures | **Enforced by a validator** |
| **10** | `automation/operator/Test-AIOSCodexWindowSnapshot.DRY_RUN.ps1:65` "exactly 10 workers"; archived dispatcher snapshots | **Enforced by a validator** |

**The sharp edge:** `aios.ps1` *contradicts itself* (4 in the launched parameter,
5 in the layout banner), and the **8 and 10 are asserted by DRY_RUN validators** —
so those tests can only pass against fixtures, never against the real launched
fleet. This is not just messy docs; it is an enforced contradiction.

## 2. Human Owner direction (2026-06-07)

Count is **undecided** ("still learning"). Stated intuition: **"one per
job/task/workflow"** — i.e. the fleet should likely be **elastic**, not a fixed
scalar. Instruction: **hold; do not overwrite, PR, or commit.**

## 3. Recommended direction (for when the decision is made)

1. **Prefer the elastic model.** Treat *active workers = active jobs/tasks*. The
   "count" is then a **derived runtime metric**, not a constant. A registry holds
   the **pool / max** and the **named lanes** (EAST OCC, WEST OCC), not a fixed total.
2. **One source of truth.** Whatever the model, declare it in exactly one place
   (e.g. an `OCC_WORKER_REGISTRY`/`WORKER_FLEET` once decided). Every consumer
   reads from it.
3. **Validators assert against the registry, not literals.** Remove the hard
   `8` and `10` from the two DRY_RUN tests; have them read the source.
4. **Regenerate fixtures + fix the `5-worker` banner** from the same source.
5. Retire the archive/legacy `10` references so scans stop surfacing them.

> None of step 3–5 is applied here — they require the Human Owner's chosen model
> and the normal packet/approval flow with allowed paths and a stop point.

## 4. Proposed AGENTS.md rule (recommended addition — NOT applied)

Add under a governance/consistency section of `AGENTS.md`:

```md
## Single-Source-of-Truth for Fleet / Config Counts

Operational counts and fleet parameters (worker count, lane count, swarm size,
and similar) MUST be declared in exactly one canonical source. No script,
validator, test, dashboard fixture, banner, preview, or document may hard-code
such a value; each consumer MUST read it from the canonical source (or be
generated from it).

- A second independent declaration of a fleet/config count is a review-blocking
  defect and must be reconciled before merge.
- Validators MUST assert against the canonical value, never a numeric literal.
- Display/banner text is never authority; if it states a count it must be
  generated from the canonical source.
- Where a value is naturally dynamic (e.g. workers = active jobs), the canonical
  source declares the MODEL and bounds (pool/max), not a fixed number, and the
  live value is reported as a derived runtime metric.
```

This is the rule that would have prevented the 4/5/8/10 drift.

## 5. Duplicate-case culprit (recollection from this session)

The earlier "more than one canonical" problem has the **same root disease** — one
fact copied into many places with no single authority — and a concrete culprit:

**Culprit: AI_OS repositories stored inside OneDrive, plus un-versioned copies.**

Evidence observed this session:

- `C:\Dev\Ai.Os` — the **only** correctly-tracked clone (origin `ai-rtony91/Ai_Os`,
  active branch) **and the only one outside OneDrive**. This is canonical.
- `OneDrive\GitHub\Ai_Os` — a copy with **no git / no remote** (loose, drifting).
- `OneDrive\GitHub\AIOS_CLAUDE_01`, `OneDrive\GitHub\AIOS_CODEX_01` — copies with
  **no git / no remote**.
- `OneDrive\GitHub\AI_OS_V2_OLD_DO_NOT_USE` — a real clone of the **same remote**
  on old branch `v2/aios` (already self-labeled "DO NOT USE").
- 12 `OneDrive\GitHub\aios-worker-*` repos (separate worker projects).

**Mechanism:** OneDrive's sync layer corrupts git and files — observed directly as
`.git/config` corruption on `git init`, mid-write file **truncation**, a stray
**NUL byte** in JSON, and dozens of phantom "modified" tracked files (line-ending
churn). The canonical clone is healthy precisely **because it lives on `C:\Dev`,
off OneDrive.**

**Recommendation (advisory):**
1. `C:\Dev\Ai.Os` is the single source of truth; keep code **off OneDrive**.
2. Archive/rename the OneDrive copies (`ARCHIVE_*`) so they cannot be mistaken
   for live; never commit from them.
3. One canonical per fact — same rule as §4, applied to repositories.

---

**Safety:** advisory only · no source mutation beyond voiding the stray draft ·
no delete/move/rename of existing files · no commit · no push · no validator
weakened. Awaiting Human Owner decision on the worker-count model before any wiring.
