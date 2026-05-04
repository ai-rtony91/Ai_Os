# Reports Storage Policy (Hybrid)

## Purpose

This policy defines what report artifacts are stored in GitHub versus archive-only storage.

## GitHub (tracked)

Track curated, reviewable markdown artifacts in GitHub, including:

- Curated markdown summaries
- Checkpoints
- Mismatch reports
- Incident summaries
- Policy documents

## OneDrive archive-only (not tracked in GitHub)

Keep raw and bulky report artifacts in OneDrive archive-only storage, including:

- Raw inventory dumps
- Full filesystem scans
- Bulky logs
- Host-specific TXT exports

## Raw data exception handling

If raw report data is needed in GitHub context, do **not** commit the raw dump.
Commit a short, sanitized markdown summary instead.

## Enforcement via `.gitignore`

The repository should ignore raw report artifact patterns such as inventory and dry-run TXT dumps under `Reports/daily`.

## Report and Mismatch Rules

- Every APPLY or DRY_RUN action must end with a written report summary.
- If observed evidence conflicts with prior notes, mark the conflict as **MISMATCH**.
- If evidence cannot be verified against files, terminal output, or screenshots, mark it as **INVALID DATA**.
- Do not hide mismatches; log them immediately in `ERROR_LOG.md` and summarize them in the current report.
- Unknown facts must be labeled **UNKNOWN** until verified.
- Report summaries must list: Task, Files inspected, Files changed, Dry-run/APPLY result, Errors, Unknowns, and Next safe action.
