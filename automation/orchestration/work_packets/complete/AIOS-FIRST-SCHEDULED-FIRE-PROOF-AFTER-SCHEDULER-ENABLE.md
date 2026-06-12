# Proposed Request Packet: First Scheduled Fire Proof After Scheduler Enable

Status: PROPOSED / REVIEW-ONLY / NOT EXECUTABLE

This file is not an executable Codex packet. It does not authorize running `AIOS_Relay_Nightly`, manually invoking the night-cycle script, launching runtime, executing runtime, mutating queues, sending SOS, touching broker/live-trading paths, storing credentials, deleting files, pushing to main, merging, or closing a PR.

## Purpose

Request a future, separate human-approved evidence lane to review the first natural scheduled-fire result after `AIOS_Relay_Nightly` was enabled.

## Current Evidence

- Enable-only evidence: `Reports/autonomy_loop_closure/scheduler_enable_only_apply_evidence.json`
- Human-readable evidence: `Reports/autonomy_loop_closure/scheduler_enable_only_apply_evidence.md`
- Task name: `AIOS_Relay_Nightly`
- Current state after enable packet: enabled and ready
- Trigger: daily at `02:00` local time
- Next scheduled fire time observed during enable packet: `2026-06-12T02:00:00` local

## Separate Human Approval Required

Anthony must separately approve any future first-fire evidence collection lane. Enablement evidence, validator output, PR review, or this proposed request file must not be treated as approval to run the task manually or invoke runtime manually.

## Future First-Fire Evidence Lane Requirements

Any future first-fire proof packet must include:

- `CODEX-ONLY PROMPT`
- `AI_OS EXECUTION TOKEN`
- `AI_OS BOOTSTRAP REQUIRED`
- identity marker
- supervisor identity
- packet ID
- mode
- zone
- worker identity
- lane
- worktree
- branch
- allowed paths
- forbidden paths
- explicit Anthony approval for evidence collection only
- validator chain
- stop point
- mission
- preflight
- final report format

The future packet must explicitly forbid manual task run, direct script invocation, manual runtime launch, queue mutation outside the naturally scheduled task's governed behavior, SOS send by Codex, broker action, live trading, credential access, secret storage, destructive cleanup, direct push to main, merge, and PR closure unless Anthony separately approves an exact protected action.

## Future Evidence Minimum

A future first-fire proof lane must validate:

- repo state before inspection
- enable-only evidence exists
- `AIOS_Relay_Nightly` exists
- task remains enabled
- task action and working directory match the approved registration evidence
- no manual task run was performed by Codex
- Task Scheduler last-run fields changed only because of a natural scheduled fire
- runtime and queue evidence is inspected only inside an explicitly approved read boundary
- broker and live trading remain blocked
- no secrets or ntfy routing values are stored

## Stop Point

Stop before waiting for, consuming, or recording first scheduled-fire evidence unless Anthony provides a separate executable packet with an exact read boundary and explicit approval for evidence collection. Do not manually run the task.

## Safe Next Action

Review the enable-only PR. After the next natural `02:00` scheduled fire, Anthony may provide a separate executable evidence packet that reads only the approved logs and Task Scheduler state.
