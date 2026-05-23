# Archive — Historical and Generated Documentation

**Purpose:** This folder contains archived, generated, and superseded AI_OS documentation.

**Important:** Do not auto-load from this archive/ folder. Archive material is historical reference only.

## Current Authority Sources

Active governance and operational authority lives in:
- `/AGENTS.md` — Codex and worker operating rules (Layer 1 — Critical)
- `/README.md` — Repository front door and orientation (Layer 1 — Critical)
- `/docs/governance/` — Source-of-truth authority mapping and governance doctrine (Layer 2 — Operational)
- `/docs/workflows/` — Operational procedures and worker lifecycle standards (Layer 2 — Operational)
- `/docs/architecture/` — System architecture and design documentation (Layer 2 — Reference)

## Archive Subfolders

### ONEDRIVE_SNAPSHOTS_20260522/
**Contents:** OneDrive project snapshots from May 22, 2026.

**Files:** AGENTS_ONEDRIVE_COPY, README_ONEDRIVE_COPY, AI_OS_MASTER_GUIDELINES_ONEDRIVE_COPY, context packs from system_wizards/, and others.

**Purpose:** Audit trail. OneDrive backups captured during migration/consolidation.

**Status:** Reference only. No unique content (duplicates of canonical files).

**Date:** 2026-05-22

---

### GENERATED_AUDITS_20260504/
**Contents:** Automated audit stages from systematic governance review (May 4, 2026).

**Includes:**
- 04_INVENTORY/ — Generated inventory classifications
- 05_CLASSIFICATION/ — File classification audit results
- 06_APPROVALS/ — Decision packets from approval gate
- 07_MOVE_PLANS/ — Proposed file relocation plans
- 09_REPORTS/ — STAGE1–STAGE27 completion reports

**Purpose:** Audit trail. Documents the systematic review that led to governance consolidation.

**Status:** Reference only. Decisions captured here may be superseded by later governance.

**Date:** 2026-05-04

---

### PHASE_AUDITS_20260504/
**Contents:** Phase-numbered audit records from systematic cleanup.

**Includes:**
- phase-1-* through phase-196-*.md — Phased cleanup/migration records
- orchestration-archive-pass-*.md — Orchestration audit results
- docs-aios-*.md — Documentation audit classifications
- Other phase-indexed audit reports

**Purpose:** Audit trail. Documents multi-phase cleanup execution and decisions.

**Status:** Reference only. Historical record.

**Date:** 2026-05-04

---

### CLEAN_ERA_SUPERSEDED/
**Contents:** Governance files from earlier AI_OS development eras (CLEAN era, OMEN era).

**Includes:**
- AGENTS.md (from docs/AI_OS/ — marked "not authoritative")
- AGENTS_MD_BACKUP_PHASE15_2_20260513.md (backup from Phase 15)
- Other superseded governance variants

**Purpose:** Historical reference. Earlier operating rules, agent roles, and system assumptions.

**Status:** DEPRECATED. Do not load as current authority. Consult only if understanding historical context.

**Date:** Various (May 2026 and earlier)

---

### SYSTEM_WIZARDS_REFERENCE/
**Contents:** Generated context packets and startup audit materials.

**Includes:**
- system_wizards/ folder (context packs from May 4)
- startup_audit/ folder (startup verification results)
- Generated context and wizard materials

**Purpose:** Reference material for understanding AI_OS startup and context generation.

**Status:** For reference. May contain useful context about project state on May 4.

**Date:** 2026-05-04

---

## How to Reference Archive Material

If you need to consult archive material:

1. **For audit trail:** Review GENERATED_AUDITS_20260504/ or PHASE_AUDITS_20260504/ to understand decisions made during consolidation.

2. **For superseded rules:** Reference CLEAN_ERA_SUPERSEDED/ if you need to understand earlier governance models (but follow current /AGENTS.md instead).

3. **For OneDrive snapshot:** Check ONEDRIVE_SNAPSHOTS_20260522/ if you need to recover a specific file or understand what was on OneDrive on May 22.

4. **For context packets:** See SYSTEM_WIZARDS_REFERENCE/ if you need generated context from the May 4 startup audit.

## Integration Notes for AI Workers

When loading AI_OS governance, import logic should:

```python
if path.startswith("archive/"):
    skip_load()  # Do not load archive material
else:
    load_governance()  # Load active authority
```

Active governance path: `/docs/governance/`, `/AGENTS.md`, `/README.md`  
Archive path: `/archive/`

---

**Archive established:** 2026-05-23  
**Method:** Batch 1 governance cleanup (OneDrive snapshots consolidation)  
**Next phases:** Pending operator approval
