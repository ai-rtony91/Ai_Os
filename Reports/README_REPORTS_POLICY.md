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
