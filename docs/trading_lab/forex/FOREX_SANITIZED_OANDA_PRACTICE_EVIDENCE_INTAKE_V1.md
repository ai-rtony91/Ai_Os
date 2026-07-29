# Sanitized OANDA Practice Evidence Intake V1

The only approved source directory for this intake is
`telemetry/forex/sanitized_oanda_practice_evidence/`. The intake reads top-level
`.json` files only and performs no broker or network calls.

`NON_EVIDENCE_SCHEMA_EXAMPLE.json` is an intentionally stale, incomplete example.
It is not broker evidence and receives zero readiness credit. Replace neither its
label nor its contents to simulate evidence.

A genuine owner-supplied receipt must identify `OANDA`, use the `PRACTICE` or
`DEMO` environment, confirm broker origin, describe at least one `OPEN` or
`CLOSED` trade, and carry an evidence timestamp no more than seven days old.
Every safety flag in the example must be explicitly `false`. An open trade may
support demo-receipt criteria but never profitability metrics; closed evidence
must also include complete finite metrics and a post-trade review.

Never place credentials, tokens, private or account identifiers, broker order
identifiers, authorization data, raw broker payloads, balances, or private
screenshots in this directory. Inputs containing sensitive values are rejected,
and classifier output reports only boolean risk markers and rejection reasons.

## State regeneration audit

The bounded-intake regeneration preserved all 17 top-level state keys. The prior
inventory contained 296 rejected records and no qualifying demo or profitability
records; the bounded inventory contains one rejected `NON_EVIDENCE` example and
still contains no qualifying records. No credited broker evidence was removed.

The removed inventory entries were classifier output derived from sources outside
the approved intake directory. Their classifications were:

- 100 `BROKER_TELEMETRY_BLOCKED` records;
- 94 `COMMAND_PACKAGE_ONLY` records;
- 45 `OFFLINE_FIXTURE` records;
- 4 `PAPER_SIMULATION` records;
- 7 `SANITIZED_TELEMETRY_REJECTED` records; and
- 46 `UNCLASSIFIED` records.

Of those 296 entries, 277 came from narrative Markdown and 19 from structured
sources. Every entry had `accepted_for_genuine_demo: false` and
`accepted_for_metrics: false`. The size reduction therefore removes duplicated
report-derived, blocked, synthetic, paper, rejected, or otherwise unverified
classifier output—not genuine broker evidence or profitability evidence.
