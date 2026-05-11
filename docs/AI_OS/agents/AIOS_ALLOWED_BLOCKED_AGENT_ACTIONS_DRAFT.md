# AIOS Allowed Blocked Agent Actions Draft

Stage: 9.1
Status: Draft planning doc

Allowed actions include inspection, DRY_RUN reporting, and approved scoped creation. Blocked actions include destructive file operations, secrets, brokers, live trading, and protected governance edits.

## Music Companion Media Rule

Allowed media actions are limited to storing YouTube video IDs, playlist IDs, and official links, and using official YouTube embedded player behavior or manual user-click External Handoff.

Blocked media actions include downloading, caching, rehosting, converting, scraping, auto-redirecting, or bypassing YouTube bot checks, sign-in checks, region blocks, age gates, ads, DRM, embed restrictions, or playback restrictions.

Codex and future AI agents must report `BLOCKED` if a requested media or Music Companion change violates these rules.

Boundary: blocked actions require explicit human approval or remain prohibited.
