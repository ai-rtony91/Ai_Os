# AI_OS Evidence Intake Dedup Workflow

## Purpose

This workflow records the approved clipboard evidence intake behavior without committing private evidence captures.

The tracked template is:

- `tools/evidence/Save-Clipboard-To-AIOS-Evidence.template.ps1`

The template is for local installation. It is not an active evidence import job, telemetry writer, scheduler, worker launcher, or approval authority.

## Privacy Boundary

Manual clipboard captures are local provenance. They can contain private conversations, local paths, account context, or operational details.

Do not commit raw captures, metadata sidecars from a live Desktop evidence folder, or raw conversation bodies unless Anthony explicitly approves a reviewed evidence package.

Do not import raw evidence into repo telemetry without a separate approved APPLY packet.

## Save Behavior

The template requires a local evidence root through `-EvidenceRoot` or `AIOS_EVIDENCE_ROOT`.

For each non-empty clipboard capture, it writes:

- one `AIOS_CLIPBOARD_EVIDENCE_<timestamp-ms>_<body-hash>_<random>.txt` file
- one matching `.metadata.json` sidecar

Writes use `CreateNew` semantics and collision checks. Existing evidence files must never be overwritten.

## Hash Fields

`raw_file_sha256` hashes the full saved file, including the generated capture header. It proves file identity and detects exact saved-file copies.

`normalized_body_sha256` hashes the clipboard body after removing the generated AI_OS header, trimming leading and trailing whitespace, normalizing line endings, and collapsing repeated blank lines. It is the metric-counting key for duplicated content.

Manual captures are provenance records. Metrics count canonical `normalized_body_sha256` groups.

## Duplicate Classes

`EXACT_DUPLICATE` means the same `normalized_body_sha256` already exists. Count the group once.

`PARTIAL_OVERLAP_STRONG_SENTENCE` means the full normalized body hash differs, but a strong non-generic sentence appears in another capture. Treat it as a duplicate-content candidate, not an exact duplicate.

`WEAK_SIMILARITY_IGNORE` means only short 2-5 word overlap was detected. Do not classify this as duplicate content.

`UNIQUE` means no matching normalized body hash and no strong sentence overlap was found.

## Strong Sentence Rule

A strong sentence has at least 8 words or at least 50 characters.

Ignore generic greetings, labels, timestamps, headings, thank-you lines, next-step boilerplate, generated capture headers, and repeated workflow boilerplate.

If the same strong sentence appears in two files but the normalized body hashes differ, classify the new record as `PARTIAL_OVERLAP_STRONG_SENTENCE`.

## Counting Rules

Same `normalized_body_sha256` means exact duplicate content. Count once.

Same filename with different content hash means separate evidence and a naming-collision review.

Different filename with the same normalized body hash means duplicate content. Count once.

Same file size alone is not duplicate evidence.

Timestamp proximity alone is not duplicate evidence.

Short 2-5 word overlap is weak similarity and must not drive duplicate classification.

Never delete duplicate evidence automatically. Duplicate classification is evidence-only unless Anthony approves cleanup.

## Current Assessment

The 2026-06-05 audit found:

- 15 manual captures inspected for content deduplication
- 0 raw-file duplicate groups
- 3 normalized-body duplicate groups
- 11 unique normalized body hashes from 15 files

AI_OS should count canonical normalized body groups, not raw capture files.

## Non-Goals

This workflow does not approve:

- importing raw captures into repo telemetry
- deleting, moving, renaming, or merging evidence
- committing live Desktop evidence captures or sidecars
- scheduler creation
- worker launch
- OpenAI API calls or other external API calls
- production promotion
