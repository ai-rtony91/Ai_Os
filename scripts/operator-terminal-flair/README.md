# AI_OS Operator Terminal Flair Preview

This folder contains repo-contained PowerShell preview helpers for AI_OS worker-profile terminal banners.

It previews visual identity only. It does not change Windows Terminal, PowerShell profiles, fonts, registry settings, startup tasks, scheduled tasks, or operating system configuration.

## Preview All Profiles

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/operator-terminal-flair/Show-AiOsTerminalFlairPreview.ps1" -All -Mode HYPE
```

## Preview MAIN_CONTROL

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/operator-terminal-flair/Show-AiOsTerminalFlairPreview.ps1" -ProfileId MAIN_CONTROL -Mode HYPE
```

## Preview EAST_OCC_01

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/operator-terminal-flair/Show-AiOsTerminalFlairPreview.ps1" -ProfileId EAST_OCC -Mode BOSS
```

To show the worker number directly in the banner:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/operator-terminal-flair/New-AiOsTerminalSessionBanner.ps1" -ProfileId EAST_OCC -WorkerNumber 01 -Mode BOSS
```

## Preview VALIDATOR_01

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/operator-terminal-flair/New-AiOsTerminalSessionBanner.ps1" -ProfileId VALIDATOR -WorkerNumber 01 -Mode CLEAN
```

## No-Emoji Preview

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts/operator-terminal-flair/Show-AiOsTerminalFlairPreview.ps1" -All -Mode CLEAN -NoEmoji
```

## What This Does Not Do

- Does not edit Windows Terminal automatically.
- Does not edit `$PROFILE`.
- Does not install modules, prompts, fonts, or themes.
- Does not create startup persistence.
- Does not create background workers.
- Does not run AI_OS automation.
- Does not touch broker, trading, credential, or live execution paths.
- Does not grant approval to APPLY, commit, push, merge, or change protected paths.

## Future Integration

Later, after a separate approved APPLY packet, these banners can be wired into launch scripts or generated terminal profile fragments. That future work must preserve human approval, validation, and protected-path boundaries.
