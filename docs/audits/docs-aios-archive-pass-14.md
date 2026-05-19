# docs/AI_OS Archive Pass 14

Date: 2026-05-19
Branch: phase-82-copy-paste-reduction-runner
Mode: APPLY, archive move only

## Purpose

Archive the remaining generated `docs/AI_OS` folders that were unblocked by Pass 13 reference retirement.

This pass did not delete files. It used `git mv` to preserve history and move generated folders to `archive/docs_aios_legacy/`.

## Folders Inspected

| Folder | Exists before move | File count | Classification |
| --- | --- | ---: | --- |
| `docs/AI_OS/checkpoints` | YES | 11 | ARCHIVE SAFE |
| `docs/AI_OS/progress` | YES | 9 | ARCHIVE SAFE |
| `docs/AI_OS/backfill` | YES | 6 | ARCHIVE SAFE |
| `docs/AI_OS/morning_brief` | YES | 5 | ARCHIVE SAFE |

## Reference Scan Results

Pre-move reference scan covered:

- `docs`
- `automation`
- `scripts`
- `apps`
- `services`
- `aios`
- `schemas`
- `tests`
- `.github`

Findings:

- No active automation/script/app/service/runtime dependency required the exact candidate paths.
- Remaining references were docs, audits, historical planning notes, or self-references inside the candidate folders.
- Pass 11 canonical summaries preserve the high-level doctrine and ideas before archive.
- Pass 13 retired automation/script references to these exact paths.

Post-move reference scan still reports historical references in docs and audits, including:

- `docs/AI_OS/audits/AIOS_FOLDER_OWNERSHIP_AUDIT_DRY_RUN.md`
- `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md`
- `docs/AI_OS/governance/AIOS_CANONICAL_SOURCE_OF_TRUTH_PROMOTION_PLAN_DRAFT.md`
- `docs/AI_OS/index/AIOS_OWNERSHIP_PATH_PATTERN_VALIDATION_DRAFT.md`
- prior audit reports under `docs/audits/`

Those references are documentation/history references, not active runtime dependencies.

## Folders Moved

| Source | Destination | Reason |
| --- | --- | --- |
| `docs/AI_OS/checkpoints/` | `archive/docs_aios_legacy/checkpoints/` | Generated stage checkpoint drafts; automation now uses canonical summaries. |
| `docs/AI_OS/progress/` | `archive/docs_aios_legacy/progress/` | Generated progress/status doctrine; roadmap summary now carries active direction. |
| `docs/AI_OS/backfill/` | `archive/docs_aios_legacy/backfill/` | Generated backfill planning drafts; Pass 10/11 audit summaries preserve cleanup plan. |
| `docs/AI_OS/morning_brief/` | `archive/docs_aios_legacy/morning_brief/` | Generated morning brief planning drafts; no active automation/scripts references remain. |

## Folders Kept

None of the four Pass 14 candidate folders were kept in active `docs/AI_OS`.

Out of scope and intentionally left active:

- `docs/AI_OS/dashboard`
- `docs/AI_OS/dispatcher`
- `docs/AI_OS/orchestration`
- `docs/AI_OS/operator`
- `docs/AI_OS/governance`
- `docs/AI_OS/security`
- `docs/AI_OS/architecture`
- `docs/AI_OS/source_control`
- `docs/AI_OS/runbooks`
- `docs/AI_OS/product`
- `docs/AI_OS/productization`

## Remaining docs/AI_OS Size Estimate

Tracked files under `docs/AI_OS` after the move: 735.

Largest remaining tracked `docs/AI_OS` areas:

| Count | Folder |
| ---: | --- |
| 127 | `docs/AI_OS/dashboard` |
| 57 | `docs/AI_OS/dispatcher` |
| 49 | `docs/AI_OS/orchestration` |
| 24 | `docs/AI_OS/agent_runtime` |
| 23 | `docs/AI_OS/operator` |
| 23 | `docs/AI_OS/writers` |
| 23 | `docs/AI_OS/telemetry` |
| 22 | `docs/AI_OS/governance` |
| 21 | `docs/AI_OS/security` |
| 19 | `docs/AI_OS/bootstrap_engine` |

## Risks

- Historical docs still mention the old active paths. That is acceptable for this pass but may confuse readers until a final docs reassessment updates source-of-truth notes.
- `docs/AI_OS/dashboard`, `docs/AI_OS/dispatcher`, and `docs/AI_OS/orchestration` remain large clutter areas.
- Some remaining `docs/AI_OS` folders may still contain useful doctrine mixed with generated planning drafts.
- No code validators were run because this pass moved docs only and did not edit PowerShell, JSON, app, service, schema, or test files.

## Validation Commands

Required validation for this pass:

```powershell
git status --short
git diff --stat
git diff --name-status
git diff --check
Get-ChildItem docs,automation,scripts,apps,services,aios,schemas,tests,.github -Recurse -File -ErrorAction SilentlyContinue |
  Select-String -Pattern 'docs/AI_OS/checkpoints|docs/AI_OS/progress|docs/AI_OS/backfill|docs/AI_OS/morning_brief'
git ls-files docs/AI_OS | Measure-Object
git ls-files docs/AI_OS |
  ForEach-Object {
    $parts = $_ -split '/'
    if ($parts.Count -ge 3) { "docs/AI_OS/$($parts[2])" } else { $_ }
  } |
  Group-Object |
  Sort-Object Count -Descending |
  Select-Object -First 15 Count,Name |
  Format-Table -AutoSize
```

## Recommended Final Reassessment Pass

Run a final docs cleanup reassessment before moving any more folders:

1. Recount active `docs/AI_OS`.
2. Re-scan references to the largest remaining folders.
3. Decide whether `dashboard`, `dispatcher`, and `orchestration` should get compact extraction docs before archive.
4. Update source-of-truth docs that still describe archived generated folders as active paths.

Recommended next pass name:

`AI_OS DOCS PASS 15 - FINAL docs/AI_OS REASSESSMENT AFTER GENERATED ARCHIVE`
