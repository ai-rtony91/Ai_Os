# AIOS Actor Relay Bus V1

## Purpose

AIOS Actor Relay Bus V1 is a file-based relay foundation for actor-to-actor
handoff in the Codex → ChatGPT → PowerShell control loop.

It is not an execution engine. It only records messages, evidence, and handoff
state so each actor can operate without runtime coupling.

## Why this exists

Today, each relay step is different. This bus normalizes routing so future
actors can be added without redesigning the pipeline.

- Codex writes relay messages.
- ChatGPT writes review text/payload guidance.
- PowerShell operator reads messages and executes only by manual pasteback.

This keeps execution human-guarded while making cross-actor coordination
extensible.

## Starter actors

- `chatgpt_supervisor` (enabled) — human-facing review and policy actor.
- `openai_cli` (future, disabled) — reserved for future CLI integration.
- `codex_cli` (enabled) — packet and relay message producer.
- `powershell_operator` (enabled) — manual execution endpoint.
- `aios_relay` (enabled) — internal bus orchestration actor.

### Future actors in this build

- `claude_code` — not connected in this V1.
- `unreal_engine_5` — not connected in this V1.
- `vscode` — not connected in this V1.
- `github_actions` — not connected in this V1.

Future actors are intentionally `enabled=false` to prevent accidental integration.

## Actor registry

Registry location:

- `control/relay_bus/actors/AIOS_RELAY_ACTORS.json`

Each actor entry includes:

- `actor_id`
- `display_name`
- `actor_type`
- `enabled`
- `allowed_message_types`
- `notes`

## Relay message envelope

Messages use schema `AIOS_RELAY_MESSAGE.v1` with these required fields:

- `schema`
- `message_id`
- `created_utc`
- `actor`
- `target_actor`
- `packet_id`
- `branch`
- `message_type`
- `intent`
- `status`
- `payload_text`
- `evidence`
- `next_action`
- `requires_human_review`
- `execution_allowed`
- `can_continue_without_anthony`

Defaults:

- `execution_allowed = false`
- `can_continue_without_anthony = false`
- `requires_human_review = true` unless the payload is clearly safe and explicitly marked.

`actor` and `target_actor` must exist in the registry.

The message writer never executes payload text.

## Security / token safety

`New-AiOsRelayMessage.DRY_RUN.ps1` rejects payloads containing obvious
secret-like patterns before any write:

- `AIOS_TG_BOT_TOKEN`
- `token=`
- `api_key`
- `secret`
- `bearer`
- `xoxb-`

Unknown actor IDs are also rejected.

## Message flow scripts

### `automation/orchestration/relay_bus/New-AiOsRelayMessage.DRY_RUN.ps1`

- Builds and writes a relay message under:
  `control/relay_bus/messages/inbox/`
- Supports `DRY_RUN` preview and `APPLY` write mode.
- File name format:
  `yyyyMMddTHHmmssZ_<actor>_<message_type>_<packet_id>.json`

### `automation/orchestration/relay_bus/Get-AiOsRelayBusState.DRY_RUN.ps1`

- Reads registry and message folders.
- Exposes latest message summary, pending review count, and state.
- Returns:
  `AIOS_RELAY_BUS_STATE.v1`

State rules:

- `EMPTY` when no messages exist.
- `NEEDS_HUMAN_REVIEW` when latest message needs human handling.
- `READY_FOR_POWERSHELL_PASTEBACK` for `reviewed_powershell`.
- `BLOCKED_NEEDS_OWNER` when latest status is `blocked_needs_owner`.
- `REVIEW_READY` when latest evidence message needs review.

## Copy/paste actions into relay

- Codex/ChatGPT/PowerShell handoff text is persisted as envelope payload.
- The bus tracks handoff path and next action so manual operators do not infer
  implicit state transitions.

Copy/paste remains explicit:
- no automatic command execution.
- no queue lock mutation.
- no runtime/runtime-like path mutation.

## `.\aios.ps1 -Mode relay`

`automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1` now
also reports actor relay bus state so one command can show both historical relay and
actor-bus state.

New operator-state fields include:

- `actor_relay_bus_status`
- `actor_relay_latest_message_path`
- `actor_relay_latest_actor`
- `actor_relay_latest_target_actor`
- `actor_relay_next_action`

## What remains manual

- deciding final command execution
- opening/pasting reviewed PowerShell content
- approving external API and runtime decisions

## What remains blocked

- live API integration
- live OpenAI CLI calls
- live Claude Code integration
- Unreal Engine automation
- file writes outside allowed `control/relay_bus` folders from this bus

## Extending to new actors

To add a new actor:

1. Add a new object in `AIOS_RELAY_ACTORS.json`.
2. Decide if it is `enabled` now or staged as future.
3. Declare supported `allowed_message_types`.
4. Emit and consume `AIOS_RELAY_MESSAGE.v1` using existing scripts.

No redesign of bus folders or schemas is required.
