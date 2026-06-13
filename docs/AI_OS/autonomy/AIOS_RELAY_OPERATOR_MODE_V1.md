# AIOS Relay Operator Mode V1

## Purpose

`aios.ps1 -Mode relay` gives Anthony one read-only command to understand the
current Codex → ChatGPT → PowerShell relay status and the exact next action.

## Existing notes and scripts reused

- `docs/AI_OS/autonomy/AIOS_CODEX_CHATGPT_POWERSHELL_RELAY_V1.md`
- `docs/AI_OS/autonomy/AIOS_CHATGPT_REVIEWED_PR_LIFECYCLE_BRIDGE_V1.md`
- `automation/orchestration/review_bridge/New-AiOsCodexReportRelayItem.DRY_RUN.ps1`
- `automation/orchestration/review_bridge/Invoke-AiOsCodexChatGptRelay.DRY_RUN.ps1`
- `automation/orchestration/review_bridge/New-AiOsChatGptPastebackItem.DRY_RUN.ps1`

## Relay state values

- `EMPTY`
  - No Codex relay report exists.
  - Next action is to store a Codex report artifact.
- `NEEDS_CHATGPT_PROMPT`
  - Codex report exists, but no ChatGPT prompt has been generated.
- `NEEDS_CHATGPT_REVIEW`
  - Prompt exists, but no reviewed pasteback has been saved.
- `PASTEBACK_READY`
  - Pasteback exists and passes safety scan.
- `PASTEBACK_REVIEW_REQUIRED`
  - Pasteback exists but safety scan is missing or failed.

## Actor relay bus handoff precedence

`Get-AiOsRelayOperatorState.DRY_RUN.ps1` now gives actor relay bus suggestions
precedence when actor bus state is explicitly at handoff points.

- When `actor_relay_bus_status` is `EMPTY`, `READY`, or `NEEDS_HUMAN_REVIEW` and `actor_relay_next_action`
  is populated, `exact_next_action` uses the actor bus action.
- Existing `needs_*` bridge fields remain in output for backward compatibility.

## `.\aios.ps1 -Mode relay`

The mode calls:

- `automation/orchestration/review_bridge/Get-AiOsRelayOperatorState.DRY_RUN.ps1 -OutputJson`

It prints:

- status
- latest report/prompt/pasteback paths
- exact next action

No commands are executed.

## What Anthony still does

- Save the Codex report using `New-AiOsCodexReportRelayItem.DRY_RUN.ps1 -Mode APPLY`.
- Paste the generated prompt into ChatGPT.
- Save ChatGPT return using `New-AiOsChatGptPastebackItem.DRY_RUN.ps1 -Mode APPLY`.
- Manually run the reviewed command after the final safety check.

## What Anthony no longer manually interprets

- Directory existence/state inference between report, prompt, and pasteback.
- Exact next action selection across the relay steps.
- Manually checking whether a saved pasteback passed scan.
- Actor-bus handoff summary in the relay operator state.

## What remains blocked

- No automatic execution in `relay` mode.
- No branch mutation, queue mutation, lock mutation, approval mutation, runtime launch.
- No direct actor-relay runtime or future actor dispatch from `relay` output; execution remains a human-gated action.

## Actor relay bus fields in operator state

`AIOS_RELAY_OPERATOR_STATE.v1` now includes:

- `actor_relay_bus_status`
- `actor_relay_latest_message_path`
- `actor_relay_latest_actor`
- `actor_relay_latest_target_actor`
- `actor_relay_next_action`

For details and implementation scope, see [`AIOS_ACTOR_RELAY_BUS_V1.md`](AIOS_ACTOR_RELAY_BUS_V1.md).

## SOS escalation policy surface in relay operator mode

When `actor_relay_bus_status` is `NEEDS_HUMAN_REVIEW`, the operator state now reads the
`Get-AiOsSosEscalationPolicy.DRY_RUN.ps1` output and surfaces:

- `sos_escalation_status`
- `sos_anthony_required`
- `sos_routine_review_allowed`
- `sos_safe_next_action`
- `sos_matched_categories`

This keeps the relay handoff read-only while making classification visible to `aios.ps1 -Mode relay`.

## Future upgrade

- Add checksum linking between report/prompt/pasteback packet IDs.
- Add explicit per-step provenance in a single signed relay manifest.
