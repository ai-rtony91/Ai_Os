# AIOS Blocked Action Matrix Draft

Status: Draft planning doc
Stage: 12.8

## Blocked Actions

| Action | Default |
| --- | --- |
| overwrite files | BLOCKED |
| delete files | BLOCKED |
| move files | BLOCKED |
| rename files | BLOCKED |
| add secrets | BLOCKED |
| connect brokers | BLOCKED |
| create live trading code | BLOCKED |
| place trades | BLOCKED |
| deploy | BLOCKED |
| self-replicate | BLOCKED |
| automatic repair | BLOCKED |
| download YouTube audio/video | BLOCKED |
| cache YouTube audio/video | BLOCKED |
| rehost YouTube audio/video | BLOCKED |
| convert YouTube media to files | BLOCKED |
| scrape YouTube | BLOCKED |
| bypass YouTube bot, sign-in, region, age, ad, DRM, embed, or playback restrictions | BLOCKED |
| auto-redirect Music Companion to YouTube or YouTube Music | BLOCKED |

## Music Companion Media Boundary

Music Companion may store YouTube video IDs, playlist IDs, and official links only.

Embedded playback must use official YouTube player behavior only. External Handoff must be manual user-click only.

If YouTube blocks embedded playback, AI_OS must show blocked status and stop. No workaround is allowed.

## Boundary

Planning only.
