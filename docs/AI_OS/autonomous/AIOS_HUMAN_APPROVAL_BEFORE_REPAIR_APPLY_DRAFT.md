# AIOS Human Approval Before Repair APPLY Draft

Stage: 11.3
Status: Draft planning doc

## Purpose

Define the approval gate before any repair APPLY.

## Required Gate

Repair APPLY requires:

- DRY_RUN repair report.
- checkpoint file.
- files inspected list.
- files to change list.
- protected action flag.
- rollback recommendation.
- explicit human approval.

## Rule

No approval means stop.
