# AIOS Forex Finish Session Ledger Template V1

## Purpose

Exact human session count is not currently stored as repo metadata, so this ledger template exists to make future session counts factual.

## Session Definition

A counted AIOS Forex finish session must include:

- session_id
- start_time
- end_time
- operator
- Codex packet ID or workflow ID
- repo branch
- files changed
- validators run
- validators passed
- git status at stop point
- outcome
- next action

## Ledger Template

| session_id | start_time | end_time | operator | packet_or_workflow_id | branch | files_changed | validators_run | validators_passed | git_status | outcome | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|

## Counting Rule

Do not infer sessions from PRs, commits, reports, or timestamps; count only explicit ledger entries.

## Current Session Count

current exact human session count from ledger entries: 0, because this template creates the ledger structure and contains no completed entries.
