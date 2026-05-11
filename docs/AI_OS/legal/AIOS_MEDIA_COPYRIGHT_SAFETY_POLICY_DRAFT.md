# AIOS Media Copyright Safety Policy Draft

Status: Draft governance policy
Scope: AI_OS Music Companion and any future media/music feature

## Allowed Storage

Music Companion may store only:

- YouTube video IDs
- YouTube playlist IDs
- official YouTube or YouTube Music links

## Blocked Actions

Music Companion and AI_OS agents must not:

- download audio or video
- cache audio or video
- rehost audio or video
- convert YouTube media to files
- scrape YouTube
- bypass YouTube bot checks
- bypass YouTube sign-in checks
- bypass region blocks
- bypass age gates
- bypass ads
- bypass DRM
- bypass embed restrictions
- bypass playback restrictions

## Playback Rules

Embedded playback must use official YouTube player behavior only.

External Handoff must be manual user-click only. AI_OS must not auto-redirect to YouTube or YouTube Music.

If YouTube blocks embedded playback, AI_OS must show blocked status and stop. No workaround, bypass, scraping, download, cache, conversion, or rehost path is allowed.

## Agent Rule

Codex and future AI agents must report `BLOCKED` if a requested media or Music Companion change violates this policy.
