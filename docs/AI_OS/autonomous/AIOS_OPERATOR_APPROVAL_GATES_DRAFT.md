# AIOS Operator Approval Gates Draft

Stage: 11.4
Status: Draft planning doc

## Purpose

Define approval gates in the autonomous operating loop.

## Approval Required For

- APPLY.
- commit.
- push.
- merge.
- delete, move, rename, overwrite.
- secrets.
- broker or trading work.
- protected root governance edits.

## Rule

If approval is required and missing, status is BLOCKED.
