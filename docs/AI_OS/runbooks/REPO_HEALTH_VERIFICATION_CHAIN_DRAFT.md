# AI_OS Repo Health Verification Chain Draft

## Purpose

This draft defines the read-only verification chain used before AI_OS repo work. The chain reports first and applies later.

## Ordered Verification Chain

1. Confirm active repo path.
2. Confirm git branch and upstream state.
3. Confirm working tree clean or list changes.
4. Confirm protected root files exist.
5. Confirm top-level folders exist.
6. Confirm Reports folders exist.
7. Confirm Stage helper scripts exist.
8. Confirm no unsafe operations were attempted.
9. Print final PASS/WARN/FAIL.

## PASS/WARN/FAIL Definitions

PASS means the checked item is present, readable, and matches the expected safe repo state.

WARN means the checked item may need human review, but the check did not prove an unsafe or blocking condition.

FAIL means the checked item is missing, the active path is wrong, git cannot provide required status, or an unsafe/blocking condition was detected.

## Operating Rules

Report first, apply later. The verification chain must print what it observed before any later APPLY work-order is considered.

GitHub clean status is authoritative over OneDrive icon status. OneDrive sync icons may be useful visual hints, but they do not replace `git status --short --branch`.

The verification chain must not stage, commit, push, delete, move, rename, overwrite, launch apps, change startup settings, touch broker systems, or enable trading behavior.

## Human Verification Checkpoint

After the chain runs, the human should read the final PASS/WARN/FAIL summary, confirm whether only expected repo changes are present, and decide the next approved action.
