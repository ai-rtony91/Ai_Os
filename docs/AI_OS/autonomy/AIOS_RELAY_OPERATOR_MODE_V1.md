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

## What remains blocked

- No automatic execution in `relay` mode.
- No branch mutation, queue mutation, lock mutation, approval mutation, runtime launch.

## Future upgrade

- Add checksum linking between report/prompt/pasteback packet IDs.
- Add explicit per-step provenance in a single signed relay manifest.
