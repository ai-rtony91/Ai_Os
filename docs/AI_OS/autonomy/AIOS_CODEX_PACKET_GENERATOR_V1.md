# AIOS Codex Packet Generator V1

## Purpose

Codex packets are hand-crafted and repetitive. This packet generator creates a
deterministic, AGENTS-compliant packet from structured intent so downstream workers
can receive complete handoff text without missing governance fields.

The generator is write-safe and emits packet text that is immediately ready for
human copy/paste into the Codex lane.

## Why this exists

Before this lane, packet drafting commonly missed mandatory execution and safety
fields or copied fragments with omissions. The generator:

- standardizes packet headers
- checks mandatory execution controls
- enforces deterministic formatting for continuation-driven packets
- keeps `execution_allowed` false
- keeps `can_continue_without_anthony` false
- avoids runtime/workspace mutation in packet generation

## Required AGENTS fields it emits

The generated packet always includes at least:

- `CODEX-ONLY PROMPT`
- `AI_OS EXECUTION TOKEN`
- `AI_OS BOOTSTRAP REQUIRED`
- `IDENTITY MARKER`
- `SUPERVISOR IDENTITY`
- `WORKER IDENTITY`
- `PACKET ID`
- `MODE`
- `ZONE`
- `LANE`
- `WORKTREE`
- `START_BRANCH`
- `BRANCH`
- `APPROVAL AUTHORITY`
- `MISSION`
- `PREFLIGHT`
- `REQUIRED PREFLIGHT STATE`
- `BRANCH PLAN`
- `READ FIRST`
- `ALLOWED MUTATION FILES ONLY`
- `FORBIDDEN PATHS`
- `IMPLEMENTATION`
- `VALIDATOR CHAIN`
- `COMMIT`
- `STOP POINT`
- `COMPLETION REPORT FORMAT`
- `STATUS`

It also writes:

- `execution_allowed: false`
- `can_continue_without_anthony: false`
- `writes_files: false`
- output schema `AIOS_CODEX_PACKET_GENERATOR.v1`

## How this stays paper-only

The generator does not execute the target packet. It does not:

- call brokers or OANDA
- load API keys
- call webhooks
- access live market data
- start scheduler, daemon, worker, queue, lock, or approval inbox flows
- commit or push on behalf of the packet

All safety controls are explicit in output text, and the validator script checks
mandatory packet fields before review.

## Validator behavior

`Test-AiOsCodexPacket.DRY_RUN.ps1` validates the generated text for required
fields and returns:

- `packet_valid` boolean
- `missing_required_fields`
- `writes_files` (always false)
- `execution_allowed` (always false)
- `can_continue_without_anthony` (always false)

The validator is strictly DRY_RUN and never writes files.

## Relay bus connection

The packet generator participates in the existing relay/operator flow:

- it creates deterministic packet text for manual approval routing
- it does not bypass relay review or manual execution
- output `STATUS` and `completion` expectations remain aligned with `relay` and
  relay-operator visibility

This keeps packet generation as a structured handoff step, not an autonomous
execution step.

## Example command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/packet_generator/New-AiOsCodexPacket.DRY_RUN.ps1 -PacketId "AIOS-SAMPLE-PACKET" -Mode APPLY -Zone "SAMPLE" -Lane "SAMPLE_LANE" -Mission "Sample mission" -Branch "feature/sample" -ApprovalAuthority "Anthony approves sample only." -AllowedMutationFiles @("docs/sample.md") -ForbiddenPaths @("broker/OANDA/webhook/order/secrets paths") -Validators @("git diff --check") -StopPoint "Stop after one local commit. No push. No PR. No merge." -AsPromptBlock
```

## What remains manual

- human review of the generated packet
- manual execution of review steps in a trusted operator mode
- final decision on commit payload, exact commit path, and protected-action
  approvals

The generator and validator reduce typing risk and omitted fields; they do not
replace human review.
