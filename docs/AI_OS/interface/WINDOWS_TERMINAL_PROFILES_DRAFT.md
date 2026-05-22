# AI_OS Windows Terminal Profile Entries — DRAFT

**Status:** DRAFT — Operator review required before adding to settings.json  
**Mode:** Documentation only. Do not auto-edit settings.json.  
**Produced:** 2026-05-18

---

## Instructions

1. Open Windows Terminal settings: `Ctrl+,` → Open JSON file
2. Locate the `"profiles"` → `"list"` array
3. Append the five profile objects below
4. Locate the `"schemes"` array
5. Append the five color scheme objects below
6. Update `startingDirectory` in each profile to match your repo root path
7. Save and restart Windows Terminal

**Never run a script to auto-edit settings.json. Copy manually.**

---

## Profile Entries

Append each block into the `"profiles"` → `"list"` array.

### 1. AI_OS MAIN CONTROL

```json
{
    "guid": "{aios-0001-0000-0000-000000000001}",
    "name": "AIOS-MAIN-CONTROL",
    "colorScheme": "AIOS-Dark-Cyan",
    "tabTitle": "AI_OS | MAIN CONTROL | DRY_RUN",
    "startingDirectory": "C:\\Dev\\Ai.Os",
    "commandline": "powershell.exe -NoExit -ExecutionPolicy Bypass -File automation\\operator\\Show-AiOsWorkerBanner.ps1 -Worker \"AI_OS MAIN CONTROL\" -Mode DRY_RUN"
}
```

### 2. CODEX BUILD LANE

```json
{
    "guid": "{aios-0002-0000-0000-000000000002}",
    "name": "AIOS-CODEX-BUILD",
    "colorScheme": "AIOS-Dark-Blue",
    "tabTitle": "AI_OS | CODEX BUILD LANE | DRY_RUN",
    "startingDirectory": "C:\\Dev\\Ai.Os",
    "commandline": "powershell.exe -NoExit -ExecutionPolicy Bypass -File automation\\operator\\Show-AiOsWorkerBanner.ps1 -Worker \"CODEX BUILD LANE\" -Mode DRY_RUN"
}
```

### 3. CLAUDE REVIEWER

```json
{
    "guid": "{aios-0003-0000-0000-000000000003}",
    "name": "AIOS-CLAUDE-REVIEWER",
    "colorScheme": "AIOS-Dark-Magenta",
    "tabTitle": "AI_OS | CLAUDE REVIEWER | DRY_RUN",
    "startingDirectory": "C:\\Dev\\Ai.Os",
    "commandline": "powershell.exe -NoExit -ExecutionPolicy Bypass -File automation\\operator\\Show-AiOsWorkerBanner.ps1 -Worker \"CLAUDE REVIEWER\" -Mode DRY_RUN"
}
```

### 4. VALIDATOR WORKER

```json
{
    "guid": "{aios-0004-0000-0000-000000000004}",
    "name": "AIOS-VALIDATOR",
    "colorScheme": "AIOS-Dark-Amber",
    "tabTitle": "AI_OS | VALIDATOR WORKER | DRY_RUN",
    "startingDirectory": "C:\\Dev\\Ai.Os",
    "commandline": "powershell.exe -NoExit -ExecutionPolicy Bypass -File automation\\operator\\Show-AiOsWorkerBanner.ps1 -Worker \"VALIDATOR WORKER\" -Mode DRY_RUN"
}
```

### 5. APPROVAL INBOX

```json
{
    "guid": "{aios-0005-0000-0000-000000000005}",
    "name": "AIOS-APPROVAL-INBOX",
    "colorScheme": "AIOS-Dark-Green",
    "tabTitle": "AI_OS | APPROVAL INBOX | DRY_RUN",
    "startingDirectory": "C:\\Dev\\Ai.Os",
    "commandline": "powershell.exe -NoExit -ExecutionPolicy Bypass -File automation\\operator\\Show-AiOsWorkerBanner.ps1 -Worker \"APPROVAL INBOX\" -Mode DRY_RUN"
}
```

---

## Color Scheme Entries

Append each block into the `"schemes"` array in settings.json.

Each scheme uses a dark background with the worker's identity color as the foreground.
The `name` field must match the `colorScheme` value in the profile entries above.

### AIOS-Dark-Cyan (MAIN CONTROL)

```json
{
    "name": "AIOS-Dark-Cyan",
    "background": "#0A0A14",
    "foreground": "#00E5FF",
    "cursorColor": "#00E5FF",
    "black": "#1A1A2E", "red": "#FF5555", "green": "#55FF99",
    "yellow": "#FFB86C", "blue": "#5AB4FF", "purple": "#CC88FF",
    "cyan": "#00E5FF", "white": "#CCCCCC",
    "brightBlack": "#555566", "brightRed": "#FF7777", "brightGreen": "#77FFAA",
    "brightYellow": "#FFD080", "brightBlue": "#88CCFF", "brightPurple": "#DDAAFF",
    "brightCyan": "#55FFFF", "brightWhite": "#FFFFFF"
}
```

### AIOS-Dark-Blue (CODEX BUILD LANE)

```json
{
    "name": "AIOS-Dark-Blue",
    "background": "#0A0F1A",
    "foreground": "#5AB4FF",
    "cursorColor": "#5AB4FF",
    "black": "#1A1E2E", "red": "#FF5555", "green": "#55FF99",
    "yellow": "#FFB86C", "blue": "#5AB4FF", "purple": "#CC88FF",
    "cyan": "#44DDFF", "white": "#CCCCCC",
    "brightBlack": "#555566", "brightRed": "#FF7777", "brightGreen": "#77FFAA",
    "brightYellow": "#FFD080", "brightBlue": "#88CCFF", "brightPurple": "#DDAAFF",
    "brightCyan": "#77EEFF", "brightWhite": "#FFFFFF"
}
```

### AIOS-Dark-Magenta (CLAUDE REVIEWER)

```json
{
    "name": "AIOS-Dark-Magenta",
    "background": "#100A14",
    "foreground": "#CC88FF",
    "cursorColor": "#CC88FF",
    "black": "#1E1A2E", "red": "#FF5555", "green": "#55FF99",
    "yellow": "#FFB86C", "blue": "#5AB4FF", "purple": "#CC88FF",
    "cyan": "#44DDFF", "white": "#CCCCCC",
    "brightBlack": "#555566", "brightRed": "#FF7777", "brightGreen": "#77FFAA",
    "brightYellow": "#FFD080", "brightBlue": "#88CCFF", "brightPurple": "#DDAAFF",
    "brightCyan": "#77EEFF", "brightWhite": "#FFFFFF"
}
```

### AIOS-Dark-Amber (VALIDATOR WORKER)

```json
{
    "name": "AIOS-Dark-Amber",
    "background": "#14100A",
    "foreground": "#FFB84D",
    "cursorColor": "#FFB84D",
    "black": "#2E1A0A", "red": "#FF5555", "green": "#55FF99",
    "yellow": "#FFB84D", "blue": "#5AB4FF", "purple": "#CC88FF",
    "cyan": "#44DDFF", "white": "#CCCCCC",
    "brightBlack": "#555566", "brightRed": "#FF7777", "brightGreen": "#77FFAA",
    "brightYellow": "#FFD080", "brightBlue": "#88CCFF", "brightPurple": "#DDAAFF",
    "brightCyan": "#77EEFF", "brightWhite": "#FFFFFF"
}
```

### AIOS-Dark-Green (APPROVAL INBOX)

```json
{
    "name": "AIOS-Dark-Green",
    "background": "#0A140C",
    "foreground": "#44FF88",
    "cursorColor": "#44FF88",
    "black": "#0A2E10", "red": "#FF5555", "green": "#44FF88",
    "yellow": "#FFB86C", "blue": "#5AB4FF", "purple": "#CC88FF",
    "cyan": "#44DDFF", "white": "#CCCCCC",
    "brightBlack": "#555566", "brightRed": "#FF7777", "brightGreen": "#77FFAA",
    "brightYellow": "#FFD080", "brightBlue": "#88CCFF", "brightPurple": "#DDAAFF",
    "brightCyan": "#77EEFF", "brightWhite": "#FFFFFF"
}
```

---

## Zone Reference (1920x1080)

| # | Worker | X | Y | W | H |
|---|--------|---|---|---|---|
| 1 | AI_OS MAIN CONTROL | 0 | 0 | 960 | 1080 |
| 2 | CODEX BUILD LANE | 960 | 0 | 960 | 360 |
| 3 | CLAUDE REVIEWER | 960 | 360 | 480 | 360 |
| 4 | VALIDATOR WORKER | 1440 | 360 | 480 | 360 |
| 5 | APPROVAL INBOX | 960 | 720 | 960 | 360 |

Window snapping is manual. FancyZones configuration is deferred.

---

## Notes

- `guid` values above use placeholder UUIDs. Replace with real GUIDs before use.
  Generate: `[System.Guid]::NewGuid().ToString()` in PowerShell.
- Update `startingDirectory` in each profile to match your actual repo root.
- `tabTitle` is set as a default; it will be overridden by the banner script at runtime
  via `$Host.UI.RawUI.WindowTitle` when Windows Terminal tab title lock is off.

---

*AI_OS Windows Terminal Profiles Draft — v0.1*  
*Produced: 2026-05-18 | Mode: documentation only | No settings.json modified*
