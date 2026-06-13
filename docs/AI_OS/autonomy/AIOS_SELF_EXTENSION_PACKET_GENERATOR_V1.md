# AIOS Self-Extension Packet Generator V1

## Purpose

AI_OS currently needs reusable packet drafting for future capabilities that are not yet
hand-built. This draft generator lets ChatGPT propose a new capability at runtime
and automatically receive a structured, AGENTS-compliant Codex packet stub.

It is intentionally conservative:

- no live execution
- no broker/OANDA path
- no secrets/API keys
- no runtime mutation
- no scheduler/worker/daemon launch

## What it adds

- rough capability intake (`CapabilityName`, `CapabilityIntent`)
- automatic classification (`capability_type`)
- safety gating (`safety_tier`)
- actor suggestion (`suggested_actor`)
- generated draft packet id and packet text
- optional relay-ready mode through existing packet generator

## Capability taxonomy used for classification

- `local_code`
- `cli_tool`
- `saas_api`
- `browser_ui`
- `file_bridge`
- `game_engine`
- `devops`
- `broker_sandbox`
- `unknown`

## Safety tiers

- `READ_ONLY`
- `DRY_RUN_ONLY`
- `SCOPED_APPLY`
- `REQUIRES_SECRET_REVIEW`
- `BLOCKED_HIGH_RISK`

High-risk intent (broker APIs, live trading, secrets, destructive system actions)
is routed to `REQUIRES_SECRET_REVIEW` or `BLOCKED_HIGH_RISK`.

## Draft output shape

`New-AiOsCapabilityPacketDraft.DRY_RUN.ps1` emits JSON with at least:

- `schema` (`AIOS_CAPABILITY_PACKET_DRAFT.v1`)
- `capability_name`
- `capability_type`
- `safety_tier`
- `suggested_actor`
- `generated_packet_id`
- `generated_packet_text`
- `packet_valid`
- `execution_allowed` (always `false`)
- `can_continue_without_anthony` (always `false`)
- `requires_human_review` (always `true`)
- `exact_next_action`
- `forbidden_paths`
- `allowed_mutation_files`

The generated packet text is validated through
`Test-AiOsCodexPacket.DRY_RUN.ps1` before being returned.

## Why this remains paper-only

This feature creates packet drafts only. It does not integrate any external
service, does not execute tools, and does not apply changes to the target
system.

## Relay and AGENTS alignment

- Uses `New-AiOsCodexPacket.DRY_RUN.ps1` to produce relay-ready packet text.
- Keeps packet validation and review in human/ChatGPT review flow.
- Preserves `execution_allowed: false` and `can_continue_without_anthony: false`.

## Example command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/packet_generator/New-AiOsCapabilityPacketDraft.DRY_RUN.ps1 `
    -CapabilityName "Claude Code" `
    -CapabilityIntent "connect Claude Code as optional code review actor" `
    -OutputJson
```

## What is still manual

- deciding the actual safety tier from operational context
- confirming allowed mutation path in AGENTS-compliant execution packets
- turning draft packet text into a full APPLY packet after review
- all approvals and protected actions

`execution_allowed` remains false until a human-authored APPLY packet is reviewed.
