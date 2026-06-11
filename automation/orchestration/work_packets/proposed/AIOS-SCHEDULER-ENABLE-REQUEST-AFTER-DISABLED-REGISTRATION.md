# Proposed Request Packet: Scheduler Enable Request After Disabled Registration

Status: PROPOSED / REVIEW-ONLY / NOT EXECUTABLE

This file is not an executable Codex packet. It does not authorize enabling `AIOS_Relay_Nightly`, running the task, launching runtime, executing runtime, mutating queues, sending SOS, touching broker/live-trading paths, storing credentials, deleting files, pushing to main, merging, or closing a PR.

## Purpose

Request a future, separate human-approved APPLY lane to review whether the disabled Windows scheduled task `AIOS_Relay_Nightly` should be enabled.

## Current Evidence

- Disabled registration evidence: `Reports/autonomy_loop_closure/scheduler_registration_disabled_apply_evidence.json`
- Human-readable evidence: `Reports/autonomy_loop_closure/scheduler_registration_disabled_apply_evidence.md`
- Task name: `AIOS_Relay_Nightly`
- Trigger: daily at `02:00` local time
- Working directory: `C:\Dev\Ai.Os`
- Current required state before any future enable lane: disabled

## Separate Human Approval Required

Anthony must separately approve any future enable action. Disabled registration evidence, validator output, PR review, or this proposed request file must not be treated as approval to enable or run the task.

## Future Enable Lane Requirements

Any future enable packet must include:

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
- explicit Anthony approval for enabling only
- validator chain
- stop point
- mission
- preflight
- final report format

The future packet must explicitly state whether enabling is the only allowed local mutation and must preserve all runtime, queue, SOS, broker, live-trading, credentials, deletion, commit, push, merge, and production blockers unless Anthony separately approves them.

## Future Validation Minimum

A future enable lane must validate:

- repo state before any mutation
- disabled registration evidence exists
- `AIOS_Relay_Nightly` exists
- task is disabled before enable
- task action and working directory match the approved disabled registration evidence
- task is enabled only after separate approval
- task is not run
- runtime is not launched or executed
- queues and approval surfaces are not mutated
- broker and live trading remain blocked

## Stop Point

Stop before enabling unless Anthony provides a separate executable APPLY packet with explicit approval for exactly that local system mutation.

## Safe Next Action

Review the disabled registration PR. If Anthony chooses to proceed later, generate a new complete executable APPLY packet for enabling review.
