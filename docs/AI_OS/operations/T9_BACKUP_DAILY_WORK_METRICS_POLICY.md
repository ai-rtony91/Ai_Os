# T9 Backup Daily Work Metrics Policy

AIOS T9 backup reports must separate backup copy size from development work.
A full snapshot can copy thousands of files and many megabytes because it is a
recovery artifact. That number does not mean the same amount of new AIOS work
was produced during the day or since the last backup window.

## Required Metric Groups

Every T9 backup or backup-sync report should include:

- `backup_copied_metrics`: what the backup operation copied or previewed.
- `dev_work_delta_metrics`: new development work since the last successful
  backup commit.
- `daily_work_metrics`: work produced on the local date.
- `timeslot_work_metrics`: work produced since the baseline for the named
  backup window.
- `courtesy_sos`: a report-only completion or failure message for the operator.

The report must not blend these groups. For example, a snapshot may copy 22.80
MB and 4819 files while the actual development patch delta is only 204.41 KB.
Both facts are useful, but they answer different questions.

## Baselines

If a last successful backup commit exists, `dev_work_delta_metrics` compares
that commit to the current commit. If the baseline is missing, the report must
set `available` to `false`, use `BASELINE_UNKNOWN` where status is needed, and
tell the operator how to establish a baseline.

Daily metrics should use the local day-start Git baseline when available.
Timeslot metrics should use a stored baseline for that timeslot when available.
Labels such as `3 PM` and `10 PM` are examples only. The schema supports any
named sync window, and scheduler activation is outside this policy.

## Courtesy SOS

The courtesy SOS message is report-only in this packet. It does not register a
live notifier, start a daemon, or activate a scheduler. It exists so every
backup completion or failure plainly states:

- status.
- time slot.
- backup copied size and file count.
- new dev-work patch size, files, insertions, and deletions.
- daily patch size and commit count.
- source and destination commit range.
- safety boundary.

## Safety Boundary

This policy does not authorize delete, mirror, scheduler, daemon, credential,
network, webhook, or notification registration behavior. Secret exclusions must
include `.env`, `*.env`, `*.pem`, `*.key`, `id_rsa`, `id_ed25519`, `*.pfx`,
`*.p12`, `*secret*`, and `*secrets*`.

Robocopy exit codes below 8 are backup-success or backup-warning states, not
hard failures. Exit code 1 means files were copied and is acceptable.
