# Telemetry Screenshot Intake Workflow

## Purpose

This workflow defines how AI_OS should handle raw local screenshot evidence for future Codex work-time telemetry.

The raw intake folders exist to hold local evidence, especially Codex session screenshots that may show "worked for" or "time worked" stamps:

- `Reports/telemetry/session_archives/inbox_evidence/`
- `Reports/telemetry/session_archives/inbox_screenshots/`

These folders are evidence intake locations only. They are not canonical telemetry ledgers, source-of-truth documents, or approved lifetime storage.

## Privacy Boundary

Raw screenshots may contain private session text, local paths, app state, browser state, account context, or other sensitive data.

By default, raw screenshots are local-only and must not be committed, pushed, attached to pull requests, or shared unless the operator explicitly approves that after review.

The operator decides whether raw screenshots are:

- retained locally
- archived outside the repo
- deleted after extraction
- reviewed again before any future use

## Intake Boundary

Current screenshot and evidence intake is metadata-only unless a future task explicitly approves deeper inspection.

Metadata-only means collecting or previewing:

- file name
- source path
- extension
- detected date
- created timestamp
- modified timestamp
- file size
- session label
- related worker, phase, stage, or commit when known
- notes
- review status

Metadata-only intake does not include OCR, visual inspection, screenshot opening, content classification, link opening, browser access, or extraction of visible text.

Existing metadata-only references:

- `Reports/telemetry/session_archives/AIOS_EVIDENCE_INTAKE_LEDGER.example.csv`
- `Reports/telemetry/session_archives/AIOS_SCREENSHOT_INTAKE_LEDGER.example.csv`
- `Reports/telemetry/daily_snapshots/AIOS_DAILY_TELEMETRY_SNAPSHOT.example.json`
- `Reports/telemetry/TELEMETRY_VALIDATION_REPORT.example.json`
- `automation/telemetry/Import-AiOsEvidenceIntake.DRY_RUN.ps1`
- `automation/telemetry/Import-AiOsScreenshotIntake.DRY_RUN.ps1`

## Extraction Boundary

OCR or visual extraction of "worked for" or "time worked" values from screenshots is a future approved step.

Extraction must not run automatically. A future extraction task must define:

- allowed source folders
- allowed file types
- fields to extract
- privacy review requirements
- output ledger or summary target
- validation steps
- retention decision point
- blocked data classes

## Expected Output

Extracted clean time-work data should flow into a clean telemetry ledger or summary file, not into raw screenshot storage.

Likely future target paths:

- `Reports/telemetry/AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_LEDGER.csv`
- `Reports/telemetry/AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_SUMMARY.json`

`telemetry/work_ledger.jsonl` already exists, but retention and schema policy still need approval before it is used as canonical lifetime work-time storage.

## Do-Not-Commit Rule

Do not commit raw screenshots from `inbox_evidence` or `inbox_screenshots` unless the operator explicitly approves that after privacy review.

Example ledgers, workflow documentation, and approved metadata-only schemas may be tracked. Raw local screenshots should remain untracked unless a future reviewed evidence package is explicitly approved.

## Future Gitignore Rule

After this workflow is documented, a separate task may add `.gitignore` rules for raw local inbox folders.

Any future ignore rule should protect raw local screenshots while keeping example ledgers, workflow docs, and approved telemetry schemas tracked.

## Workflow Stages

1. Capture

   The operator or approved tool places raw local screenshots or evidence files into the intake folders. No automatic recording, screenshot capture, OCR, or extraction is approved by this workflow.

2. Intake Metadata

   Metadata-only helpers may preview file names, paths, extensions, timestamps, sizes, and review status. Current helpers are DRY_RUN only.

3. Review And Privacy Check

   The operator reviews whether the raw evidence may contain private data and decides whether extraction is safe. Sensitive screenshots remain local-only unless explicitly approved for another handling path.

4. Approved Extraction

   A separately approved task may extract clean "worked for" or "time worked" values from reviewed screenshots. This step may use OCR or visual inspection only when explicitly approved.

5. Ledger Update

   Extracted clean values may be written to an approved telemetry ledger or summary path. Raw screenshots should not become the canonical telemetry record.

6. Retention, Archive, Or Delete Decision

   The operator decides whether the raw screenshots stay local, are archived outside the repo, or are deleted after extraction. No deletion, movement, or archive action is approved by this workflow alone.

## Current Status

Extraction automation is not implemented.

Current scripts are DRY_RUN metadata-only helpers:

- `automation/telemetry/Import-AiOsEvidenceIntake.DRY_RUN.ps1`
- `automation/telemetry/Import-AiOsScreenshotIntake.DRY_RUN.ps1`

This workflow does not approve OCR, screenshot opening, screenshot movement, screenshot deletion, `.gitignore` edits, extraction scripts, commits, pushes, broker actions, live trading, or telemetry persistence.
