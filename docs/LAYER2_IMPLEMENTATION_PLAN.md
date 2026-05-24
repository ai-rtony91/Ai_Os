# AI_OS LAYER 2 — IMPLEMENTATION PLAN
**Document ID:** LAYER2-IMPL-001  
**Date:** 2026-05-22  
**Status:** PLANNING ONLY — Zero installs. Zero config writes. Zero file changes.  
**Scope:** JetBrainsMono Nerd Font · Lazygit · Yazi · WezTerm (secondary) · T:\AIOS_TERMINAL  
**Excluded this phase:** Oh My Posh (deferred)

---

## CRITICAL PRE-CONDITIONS

Before any step in this document is executed, all three gates must pass:

```
GATE 1: Layer 1 health check
  pwsh -Command "git -C $env:AIOS_ROOT status"
  Expected: clean git output from C:\Dev\Ai.Os
  If fail: STOP. Do not proceed.

GATE 2: T9 drive is connected and assigned letter T:
  Test-Path T:\
  Expected: True
  If fail: STOP. Assign drive letter before proceeding.

GATE 3: Pre-install backup is complete (Section 2)
  Expected: All backup files present at T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\
  If fail: STOP. Complete backup before proceeding.
```

---

## SECTION 1 — T:\AIOS_TERMINAL FOLDER STRUCTURE

This is the canonical config home. Every portable config lives here. Create this structure manually on the T9 before any installs.

```
T:\AIOS_TERMINAL\
│
├── _README.txt                          ← brief description of this drive structure
│
├── backups\
│   └── PRE_LAYER2_SNAPSHOT\
│       ├── PS7_profile.ps1              ← copy of Documents\PowerShell\Microsoft.PowerShell_profile.ps1
│       ├── Windows_Terminal_settings.json  ← copy of WT LocalState\settings.json
│       ├── winget_list_snapshot.txt     ← output of: winget list > this file
│       └── SNAPSHOT_DATE.txt            ← date/time of snapshot
│
├── configs\
│   ├── wezterm\
│   │   └── .wezterm.lua                 ← WezTerm full Lua config (written at Step 4)
│   │
│   ├── lazygit\
│   │   └── config.yml                   ← Lazygit YAML config (written at Step 2)
│   │
│   ├── yazi\
│   │   ├── yazi.toml                    ← Yazi main config
│   │   ├── keymap.toml                  ← Yazi key bindings
│   │   └── theme.toml                   ← Yazi color theme
│   │
│   └── windows-terminal\
│       └── settings.json                ← Windows Terminal backup + future edits
│
├── fonts\
│   └── JetBrainsMono\
│       ├── JetBrainsMonoNerdFont-Regular.ttf
│       ├── JetBrainsMonoNerdFont-Bold.ttf
│       ├── JetBrainsMonoNerdFont-Italic.ttf
│       ├── JetBrainsMonoNerdFont-BoldItalic.ttf
│       └── [all other variants from the release zip]
│
└── bootstrap\
    └── (future) New-AIOSTerminalBootstrap.ps1    ← not written yet
```

**Creation commands (run in PowerShell before any installs):**
```powershell
# Creates full T9 folder tree — safe to run, creates dirs only
$base = "T:\AIOS_TERMINAL"
@(
    "$base\backups\PRE_LAYER2_SNAPSHOT",
    "$base\configs\wezterm",
    "$base\configs\lazygit",
    "$base\configs\yazi",
    "$base\configs\windows-terminal",
    "$base\fonts\JetBrainsMono",
    "$base\bootstrap"
) | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }
Write-Host "T:\AIOS_TERMINAL structure created." -ForegroundColor Green
```

---

## SECTION 2 — PRE-INSTALL BACKUP STRATEGY

Run all backup commands before touching anything. This is the rollback foundation.

### 2.1 PS7 Profile Backup
```powershell
# Backup current PS7 profile to T9
$src  = "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
$dest = "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\PS7_profile.ps1"
Copy-Item -LiteralPath $src -Destination $dest -Force
Write-Host "PS7 profile backed up." -ForegroundColor Green
```

### 2.2 Windows Terminal Settings Backup
```powershell
# Find WT settings.json (works for both stable and preview)
$wtPkg = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "Microsoft.WindowsTerminal*" |
         Select-Object -First 1
if ($wtPkg) {
    $src  = Join-Path $wtPkg.FullName "LocalState\settings.json"
    $dest = "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\Windows_Terminal_settings.json"
    Copy-Item -LiteralPath $src -Destination $dest -Force
    Write-Host "Windows Terminal settings backed up." -ForegroundColor Green
} else {
    Write-Host "WARNING: Windows Terminal package not found." -ForegroundColor Yellow
}
```

### 2.3 Winget Installed Packages Snapshot
```powershell
# Record current installed package state for rollback reference
winget list | Out-File -FilePath "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\winget_list_snapshot.txt" -Encoding UTF8
Write-Host "Winget snapshot saved." -ForegroundColor Green
```

### 2.4 Snapshot Timestamp
```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss zzz" |
    Out-File "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\SNAPSHOT_DATE.txt" -Encoding UTF8
Write-Host "Snapshot timestamp recorded." -ForegroundColor Green
```

### 2.5 Backup Validation
```powershell
# Confirm all 4 backup files exist before proceeding
$backupFiles = @(
    "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\PS7_profile.ps1",
    "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\Windows_Terminal_settings.json",
    "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\winget_list_snapshot.txt",
    "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\SNAPSHOT_DATE.txt"
)
$allPresent = $true
foreach ($f in $backupFiles) {
    if (Test-Path $f) { Write-Host "  OK: $f" -ForegroundColor Green }
    else { Write-Host "  MISSING: $f" -ForegroundColor Red; $allPresent = $false }
}
if ($allPresent) { Write-Host "BACKUP COMPLETE. Safe to proceed." -ForegroundColor Cyan }
else             { Write-Host "BACKUP INCOMPLETE. Do NOT proceed." -ForegroundColor Red }
```

---

## SECTION 3 — MACHINE-BOUND vs PORTABLE SEPARATION

```
MACHINE-BOUND — must be reinstalled on any new workstation:
┌─────────────────────────────────────────────────────────────┐
│ JetBrainsMono Nerd Font  → C:\Windows\Fonts\                │
│ WezTerm binary           → %LOCALAPPDATA%\WezTerm\          │
│ Lazygit binary           → %LOCALAPPDATA%\Microsoft\WinGet\ │
│ Yazi binary              → %LOCALAPPDATA%\Microsoft\WinGet\ │
└─────────────────────────────────────────────────────────────┘

PORTABLE — lives on T9, survives machine wipe:
┌─────────────────────────────────────────────────────────────┐
│ .wezterm.lua             → T:\AIOS_TERMINAL\configs\wezterm\│
│ lazygit config.yml       → T:\AIOS_TERMINAL\configs\lazygit\│
│ yazi *.toml files        → T:\AIOS_TERMINAL\configs\yazi\   │
│ Font .ttf files (raw)    → T:\AIOS_TERMINAL\fonts\          │
│ WT settings.json backup  → T:\AIOS_TERMINAL\configs\        │
│ PS7 profile backup       → T:\AIOS_TERMINAL\backups\        │
└─────────────────────────────────────────────────────────────┘

SYMLINK BRIDGE — machine entry points that redirect to T9:
┌─────────────────────────────────────────────────────────────┐
│ %USERPROFILE%\.wezterm.lua          → (file symlink → T9)   │
│ %APPDATA%\lazygit\        (dir)     → (junction   → T9)     │
│ %APPDATA%\yazi\config\    (dir)     → (junction   → T9)     │
└─────────────────────────────────────────────────────────────┘
```

---

## SECTION 4 — SYMLINK STRATEGY

### 4.1 Symlink Type Decision

| Target | Type | Command flag | Admin needed? | Notes |
|--------|------|-------------|---------------|-------|
| `.wezterm.lua` (file) | File symlink | `mklink` (no flag) | Yes (or Dev Mode) | Single Lua file |
| `lazygit\` (directory) | Directory junction | `mklink /J` | **No** | Works on NTFS without elevation |
| `yazi\config\` (directory) | Directory junction | `mklink /J` | **No** | Works on NTFS without elevation |

Use **directory junctions** (`/J`) for folders — they work without admin rights on standard NTFS volumes.

For the `.wezterm.lua` file symlink: either enable Developer Mode (Settings → Privacy & Security → Developer Mode) or run the single `mklink` command once from an elevated prompt.

### 4.2 Symlink Creation Commands

**Pre-condition for all symlink commands:** The T9 target files/folders must already exist before the symlink points to them. Create the T9 folder structure (Section 1) first.

```cmd
REM === Run from an elevated CMD prompt ===
REM === Or enable Developer Mode and run from normal prompt ===

REM ── WezTerm .wezterm.lua file symlink ──
REM   (only needed if .wezterm.lua does not already exist at %USERPROFILE%\)
mklink "%USERPROFILE%\.wezterm.lua" "T:\AIOS_TERMINAL\configs\wezterm\.wezterm.lua"

REM ── Lazygit config directory junction ──
REM   (do NOT run if %APPDATA%\lazygit\ already exists — move contents to T9 first)
mklink /J "%APPDATA%\lazygit" "T:\AIOS_TERMINAL\configs\lazygit"

REM ── Yazi config directory junction ──
REM   (do NOT run if %APPDATA%\yazi\config\ already exists — move contents to T9 first)
mklink /J "%APPDATA%\yazi\config" "T:\AIOS_TERMINAL\configs\yazi"
```

### 4.3 Symlink Safety Rules

```
RULE 1: Never create a junction over an existing non-empty directory.
        If %APPDATA%\lazygit\ already exists after install,
        move its contents to T9 first, then delete the original dir,
        then create the junction.

RULE 2: Always verify the T9 target path exists before mklink.
        Test-Path "T:\AIOS_TERMINAL\configs\lazygit"  → must return True

RULE 3: Verify junction after creation:
        (Get-Item "%APPDATA%\lazygit").LinkType  → must return "Junction"

RULE 4: If T9 is not connected when a tool starts, it fails at the
        config layer only — the binary still runs. Lazygit launches
        with no config rather than crashing hard.
```

### 4.4 Symlink Verification Commands
```powershell
# Run after creating all symlinks to confirm they resolve correctly
$symlinks = @{
    "WezTerm config"    = "$HOME\.wezterm.lua"
    "Lazygit config"    = "$env:APPDATA\lazygit"
    "Yazi config"       = "$env:APPDATA\yazi\config"
}
foreach ($name in $symlinks.Keys) {
    $path = $symlinks[$name]
    $item = Get-Item $path -ErrorAction SilentlyContinue
    if ($item) {
        $type = if ($item.LinkType) { $item.LinkType } else { "Regular" }
        $target = if ($item.Target) { $item.Target } else { "N/A" }
        Write-Host "  OK  [$type] $name" -ForegroundColor Green
        Write-Host "       → $target" -ForegroundColor Gray
    } else {
        Write-Host "  MISSING: $name at $path" -ForegroundColor Red
    }
}
```

---

## SECTION 5 — INSTALL ORDER

```
ORDER     TOOL                    RATIONALE
──────────────────────────────────────────────────────────────────
STEP 0    T9 folder structure     Must exist before any symlinks
STEP 0    Pre-install backup      Must complete before any installs
──────────────────────────────────────────────────────────────────
STEP 1    JetBrainsMono NF        All visual tools need glyphs first
STEP 2    Lazygit                 Lowest risk — git-only dependency
STEP 3    Yazi                    Optional preview deps after binary
STEP 4    WezTerm                 Last — terminal host, test all tools inside it
──────────────────────────────────────────────────────────────────
Oh My Posh  DEFERRED              Not in this phase
──────────────────────────────────────────────────────────────────
```

---

## SECTION 6 — STEP 1: JetBrainsMono Nerd Font

### 6.1 Classification
```
Machine-bound : YES — installs into Windows Font registry (C:\Windows\Fonts\)
Portable      : PARTIAL — raw .ttf files stored on T9 for re-install on new machine
Config        : NONE — font has no config file
Rollback      : Control Panel → Fonts → delete JetBrainsMono entries
```

### 6.2 Winget Command
```powershell
# VERIFY THIS ID FIRST on workstation before running:
winget search "JetBrainsMono"
# Expected package: DEVCOM.JetBrainsMonoNerdFont
# If not found via winget, use the direct download method below.

# Install command (run after ID verified):
winget install --id DEVCOM.JetBrainsMonoNerdFont --source winget
```

> **⚠️ Verification required:** Run `winget search "JetBrainsMono"` first on the workstation to confirm the exact package ID. The ID above (`DEVCOM.JetBrainsMonoNerdFont`) is the current community repo ID but may differ on your machine's winget source configuration.

### 6.3 Manual Install Method (fallback if winget ID not found)
```
1. Navigate to: https://github.com/ryanoasis/nerd-fonts/releases/latest
2. Download: JetBrainsMono.zip
3. Extract to: T:\AIOS_TERMINAL\fonts\JetBrainsMono\  (portable copy)
4. In the extracted folder: select all .ttf files
5. Right-click → "Install for all users"  (installs to C:\Windows\Fonts\)
```

### 6.4 T9 Font Archive (portable copy — separate from install)
```powershell
# After install: copy raw .ttf files to T9 for future machine migrations
# Source: wherever the zip was extracted, or from C:\Windows\Fonts\ (filter by JetBrains*)
$fontDest = "T:\AIOS_TERMINAL\fonts\JetBrainsMono"
Get-Item "C:\Windows\Fonts\JetBrainsMono*" | Copy-Item -Destination $fontDest
Write-Host "Font files copied to T9." -ForegroundColor Green
```

### 6.5 Validation Checkpoint — Step 1
```powershell
# Test 1: Font is registered in Windows
$fontKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
$fonts   = Get-ItemProperty $fontKey
$jbm     = $fonts.PSObject.Properties | Where-Object { $_.Name -like "*JetBrainsMono*" }
if ($jbm) {
    Write-Host "PASS: JetBrainsMono Nerd Font registered ($($jbm.Count) variants)" -ForegroundColor Green
} else {
    Write-Host "FAIL: JetBrainsMono not found in font registry" -ForegroundColor Red
}

# Test 2: T9 font files present
$t9Fonts = Get-ChildItem "T:\AIOS_TERMINAL\fonts\JetBrainsMono" -Filter "*.ttf" -ErrorAction SilentlyContinue
Write-Host "T9 font files archived: $($t9Fonts.Count) .ttf files" -ForegroundColor Cyan
```

### 6.6 Rollback — Step 1
```
METHOD 1 (GUI):  Control Panel → Appearance → Fonts
                 Filter for "JetBrainsMono" → select all → Delete
METHOD 2 (CMD):  Requires elevation — not recommended for a single font uninstall
T9 portable copy: unaffected by uninstall — stays on T9
```

---

## SECTION 7 — STEP 2: Lazygit

### 7.1 Classification
```
Machine-bound : Binary only — %LOCALAPPDATA%\Microsoft\WinGet\Packages\
Portable      : Config (config.yml) → T:\AIOS_TERMINAL\configs\lazygit\
Rollback      : winget uninstall JesseDuffield.lazygit
Risk level    : LOWEST — standalone tool, no terminal integration, no profile touch
```

### 7.2 Winget Command
```powershell
# Verify ID first:
winget search "lazygit"
# Expected: JesseDuffield.lazygit

# Install:
winget install --id JesseDuffield.lazygit --source winget
```

### 7.3 Post-Install: Config Directory Handling

After install, Lazygit creates its config directory on first launch. The sequence:

```
A. Launch lazygit once (from C:\Dev\Ai.Os) to generate default config
B. Copy the generated config to T9:
   Copy-Item "$env:APPDATA\lazygit\config.yml" "T:\AIOS_TERMINAL\configs\lazygit\config.yml"
C. Delete the original directory:
   Remove-Item "$env:APPDATA\lazygit" -Recurse -Force
D. Create the junction:
   cmd /c mklink /J "%APPDATA%\lazygit" "T:\AIOS_TERMINAL\configs\lazygit"
E. Verify junction resolves:
   (Get-Item "$env:APPDATA\lazygit").LinkType   → should return "Junction"
```

> **Why this order matters:** Lazygit on first launch writes its default `config.yml`. If you create the junction before first launch, the junction already points to T9 — first launch writes directly to T9 (which is the desired end state). Either order works, but the sequence above ensures you capture the auto-generated defaults before they are overwritten.

### 7.4 Config File Location Map
```
Windows default  : C:\Users\mylab\AppData\Roaming\lazygit\config.yml
Symlink source   : C:\Users\mylab\AppData\Roaming\lazygit\          ← junction
Symlink target   : T:\AIOS_TERMINAL\configs\lazygit\                ← real location
Canonical file   : T:\AIOS_TERMINAL\configs\lazygit\config.yml
```

### 7.5 Validation Checkpoint — Step 2
```powershell
# Test 1: Binary on PATH
if (Get-Command lazygit -ErrorAction SilentlyContinue) {
    $v = lazygit --version
    Write-Host "PASS: lazygit found — $v" -ForegroundColor Green
} else {
    Write-Host "FAIL: lazygit not on PATH" -ForegroundColor Red
}

# Test 2: Junction resolves to T9
$lg = Get-Item "$env:APPDATA\lazygit" -ErrorAction SilentlyContinue
if ($lg -and $lg.LinkType -eq "Junction") {
    Write-Host "PASS: lazygit junction → $($lg.Target)" -ForegroundColor Green
} else {
    Write-Host "WARN: lazygit config path is not a junction" -ForegroundColor Yellow
}

# Test 3: Config file exists on T9
if (Test-Path "T:\AIOS_TERMINAL\configs\lazygit\config.yml") {
    Write-Host "PASS: config.yml present on T9" -ForegroundColor Green
} else {
    Write-Host "FAIL: config.yml missing from T9" -ForegroundColor Red
}

# Test 4: Functional launch from canonical repo
Set-Location $env:AIOS_ROOT
Write-Host "MANUAL TEST REQUIRED: run 'lazygit' and confirm:"
Write-Host "  - Opens in C:\Dev\Ai.Os"
Write-Host "  - Git branch and status visible"
Write-Host "  - No font glyph errors (arrows and diff symbols render)"
```

### 7.6 Rollback — Step 2
```powershell
# Step 1: Remove binary
winget uninstall JesseDuffield.lazygit

# Step 2: Remove junction (configs stay on T9 unaffected)
Remove-Item "$env:APPDATA\lazygit"   # removes junction only, not T9 contents

# Verify T9 config intact:
Test-Path "T:\AIOS_TERMINAL\configs\lazygit\config.yml"   # must return True
```

---

## SECTION 8 — STEP 3: Yazi

### 8.1 Classification
```
Machine-bound : Binary — winget install target
Portable      : Config (yazi.toml, keymap.toml, theme.toml) → T9
Rollback      : winget uninstall sxyazi.yazi
Risk level    : LOW — standalone file manager, no profile touch
```

### 8.2 Winget Command
```powershell
# Verify ID first:
winget search "yazi"
# Expected: sxyazi.yazi

# Install:
winget install --id sxyazi.yazi --source winget
```

### 8.3 Yazi Optional Preview Dependencies

Yazi's file preview engine hooks into external tools for richer previews. These are optional but significantly improve the experience for AI_OS file navigation (previewing `.ps1`, `.json`, `.lua`, `.md` files inline).

```
DEPENDENCY    WINGET ID                    PURPOSE                  PRIORITY
──────────────────────────────────────────────────────────────────────────────
bat           sharkdp.bat                  Syntax-highlighted        HIGH
                                           preview of .ps1 .json
                                           .lua .md files
fd            sharkdp.fd                   Fast file search          MEDIUM
                                           (replaces find/dir)
ripgrep       BurntSushi.ripgrep.MSVC      Content search in Yazi    MEDIUM
                                           (likely already installed)
7-Zip         7zip.7zip                    Archive preview           LOW
                                           (likely already installed)
jq            jqlang.jq                    JSON preview/query        LOW
                                           (likely already installed)
```

```powershell
# Check which are already installed before adding:
@("bat","fd","rg","7z","jq") | ForEach-Object {
    $found = Get-Command $_ -ErrorAction SilentlyContinue
    if ($found) { Write-Host "  PRESENT: $_" -ForegroundColor Green }
    else         { Write-Host "  MISSING: $_" -ForegroundColor Yellow }
}
```

```powershell
# Install only what is missing (run selectively):
winget install --id sharkdp.bat           --source winget   # HIGH priority
winget install --id sharkdp.fd            --source winget   # MEDIUM
winget install --id BurntSushi.ripgrep.MSVC --source winget # MEDIUM (if not present)
```

### 8.4 Post-Install: Config Directory Handling

Yazi creates its config directory on first launch or when you run `yazi --config-dir`.

```
A. Run: yazi --config-dir
   Output will show: C:\Users\mylab\AppData\Roaming\yazi\config
B. If config dir exists: copy its contents to T9 first
C. If config dir does not exist: create T9 target files first, then create junction
D. Create junction:
   cmd /c mklink /J "%APPDATA%\yazi\config" "T:\AIOS_TERMINAL\configs\yazi"
E. Verify: (Get-Item "$env:APPDATA\yazi\config").LinkType → "Junction"
```

### 8.5 Config File Location Map
```
Windows default  : C:\Users\mylab\AppData\Roaming\yazi\config\
                   ├── yazi.toml
                   ├── keymap.toml
                   └── theme.toml
Symlink source   : C:\Users\mylab\AppData\Roaming\yazi\config\    ← junction
Symlink target   : T:\AIOS_TERMINAL\configs\yazi\                 ← real location
Canonical files  : T:\AIOS_TERMINAL\configs\yazi\yazi.toml
                   T:\AIOS_TERMINAL\configs\yazi\keymap.toml
                   T:\AIOS_TERMINAL\configs\yazi\theme.toml
```

### 8.6 Validation Checkpoint — Step 3
```powershell
# Test 1: Binary on PATH
if (Get-Command yazi -ErrorAction SilentlyContinue) {
    $v = yazi --version
    Write-Host "PASS: yazi found — $v" -ForegroundColor Green
} else {
    Write-Host "FAIL: yazi not on PATH" -ForegroundColor Red
}

# Test 2: Junction resolves
$yc = Get-Item "$env:APPDATA\yazi\config" -ErrorAction SilentlyContinue
if ($yc -and $yc.LinkType -eq "Junction") {
    Write-Host "PASS: yazi config junction → $($yc.Target)" -ForegroundColor Green
} else {
    Write-Host "WARN: yazi config path is not a junction" -ForegroundColor Yellow
}

# Test 3: Config files on T9
@("yazi.toml","keymap.toml","theme.toml") | ForEach-Object {
    $p = "T:\AIOS_TERMINAL\configs\yazi\$_"
    if (Test-Path $p) { Write-Host "PASS: $_ on T9" -ForegroundColor Green }
    else               { Write-Host "INFO: $_ not yet on T9 (written at config phase)" -ForegroundColor Cyan }
}

# Test 4: Functional launch
Write-Host ""
Write-Host "MANUAL TEST REQUIRED: run 'yazi C:\Dev\Ai.Os' and confirm:"
Write-Host "  - File tree renders with JetBrainsMono icons"
Write-Host "  - .ps1 and .json files show syntax-highlighted preview (requires bat)"
Write-Host "  - hjkl navigation works"
Write-Host "  - q exits cleanly"
```

### 8.7 Rollback — Step 3
```powershell
# Step 1: Remove binary and optional deps if installed
winget uninstall sxyazi.yazi
# winget uninstall sharkdp.bat   (only if it was installed for Yazi and not used elsewhere)
# winget uninstall sharkdp.fd    (same caveat)

# Step 2: Remove junction (T9 configs unaffected)
Remove-Item "$env:APPDATA\yazi\config"   # removes junction only

# Verify T9 intact:
Test-Path "T:\AIOS_TERMINAL\configs\yazi"   # must return True
```

---

## SECTION 9 — STEP 4: WezTerm (Secondary Terminal)

### 9.1 Classification
```
Machine-bound : Binary — winget install target
Portable      : .wezterm.lua → T:\AIOS_TERMINAL\configs\wezterm\
Role          : SECONDARY — Windows Terminal remains primary and untouched
Rollback      : winget uninstall wez.wezterm
Risk level    : MEDIUM — introduces new terminal host, must validate PS7 + AIOS_ROOT work inside it
```

**Secondary terminal means:** WezTerm is an additional option, not a replacement. Windows Terminal settings.json is not modified during this step. Both terminals will work independently.

### 9.2 Winget Command
```powershell
# Verify ID first:
winget search "wezterm"
# Expected: wez.wezterm

# Install (stable release):
winget install --id wez.wezterm --source winget
```

> **Two WezTerm release channels exist:** stable (`wez.wezterm`) and nightly (`wez.wezterm.nightly`). Use stable only.

### 9.3 Config File Location and Strategy

WezTerm checks for its config in this order on Windows:
```
1. %USERPROFILE%\.wezterm.lua               ← PRIMARY — use this one
2. %USERPROFILE%\.config\wezterm\wezterm.lua
3. %APPDATA%\wezterm\wezterm.lua
```

**Strategy:** `.wezterm.lua` at `%USERPROFILE%\` is the target. It will be a file symlink pointing to `T:\AIOS_TERMINAL\configs\wezterm\.wezterm.lua`.

### 9.4 Symlink — .wezterm.lua (file, not directory)
```cmd
REM Requires elevation OR Developer Mode enabled
REM Run from elevated CMD:

mklink "%USERPROFILE%\.wezterm.lua" "T:\AIOS_TERMINAL\configs\wezterm\.wezterm.lua"
```

```powershell
# Verify:
$wt = Get-Item "$HOME\.wezterm.lua" -ErrorAction SilentlyContinue
if ($wt -and $wt.LinkType -eq "SymbolicLink") {
    Write-Host "PASS: .wezterm.lua → $($wt.Target)" -ForegroundColor Green
} else {
    Write-Host "INFO: .wezterm.lua is not a symlink — may be a direct file or missing" -ForegroundColor Yellow
}
```

### 9.5 Planned .wezterm.lua Content (to be written at config phase — NOT NOW)

The config file does not exist yet on T9. This is a description of what it will contain when written:

```
PLANNED CONTENT — NOT WRITTEN YET:
  default_prog          = { 'pwsh', '-NoLogo' }
  font                  = JetBrainsMono Nerd Font
  font_size             = 12.0
  color_scheme          = (TBD — dark, low fatigue)
  tab_bar_at_bottom     = true
  use_fancy_tab_bar     = false
  audible_bell          = Disabled
  scrollback_lines      = 10000
  default_cwd           = C:\Dev\Ai.Os (fallback only — profile handles this)
  window_decorations    = RESIZE | TITLE
```

The full `.wezterm.lua` will be a separate implementation task once this plan is approved.

### 9.6 Config File Location Map
```
Symlink source   : C:\Users\mylab\.wezterm.lua               ← file symlink
Symlink target   : T:\AIOS_TERMINAL\configs\wezterm\.wezterm.lua  ← real file
Canonical file   : T:\AIOS_TERMINAL\configs\wezterm\.wezterm.lua
```

### 9.7 Validation Checkpoint — Step 4
```powershell
# Test 1: Binary exists
if (Get-Command wezterm -ErrorAction SilentlyContinue) {
    $v = wezterm --version
    Write-Host "PASS: wezterm found — $v" -ForegroundColor Green
} else {
    Write-Host "FAIL: wezterm not on PATH" -ForegroundColor Red
}

# Test 2: Symlink resolves
$wz = Get-Item "$HOME\.wezterm.lua" -ErrorAction SilentlyContinue
if ($wz) {
    Write-Host "PASS: .wezterm.lua present (LinkType: $($wz.LinkType))" -ForegroundColor Green
} else {
    Write-Host "INFO: .wezterm.lua does not exist yet (written at config phase)" -ForegroundColor Cyan
}

# Test 3: Windows Terminal unaffected (manual)
Write-Host ""
Write-Host "MANUAL TESTS REQUIRED after first WezTerm launch:"
Write-Host "  1. WezTerm opens → default shell is pwsh (not cmd)"
Write-Host "  2. PS7 profile fires → AIOS_ROOT set → location = C:\Dev\Ai.Os"
Write-Host "  3. 'git status' works in WezTerm session"
Write-Host "  4. JetBrainsMono glyphs render correctly in WezTerm"
Write-Host "  5. Open Windows Terminal separately → still works independently"
Write-Host "  6. Layer 1 health check passes from Windows Terminal:"
Write-Host "     git -C `$env:AIOS_ROOT status"
```

### 9.8 Rollback — Step 4
```powershell
# Step 1: Remove binary
winget uninstall wez.wezterm

# Step 2: Remove .wezterm.lua symlink (T9 config file unaffected)
Remove-Item "$HOME\.wezterm.lua"   # removes symlink only, not T9 file

# Step 3: Confirm Windows Terminal unchanged
# (Nothing was ever modified in WT settings — no rollback needed there)

# Verify T9 config intact:
Test-Path "T:\AIOS_TERMINAL\configs\wezterm\.wezterm.lua"   # True if file was written; False if not yet written
```

---

## SECTION 10 — FULL STACK VALIDATION (Post All Steps)

Run after all four steps complete. All must pass before this phase is considered done.

```powershell
Write-Host "===== AI_OS LAYER 2 FULL VALIDATION =====" -ForegroundColor Cyan
Write-Host ""

$pass = 0
$fail = 0

function Test-Item {
    param([string]$Label, [scriptblock]$Test, [string]$Manual = "")
    $result = try { & $Test } catch { $false }
    if ($result) {
        Write-Host "  PASS  $Label" -ForegroundColor Green
        $script:pass++
    } elseif ($Manual) {
        Write-Host "  MANUAL $Label" -ForegroundColor Yellow
        Write-Host "         $Manual"
    } else {
        Write-Host "  FAIL  $Label" -ForegroundColor Red
        $script:fail++
    }
}

# Layer 1 still intact
Test-Item "Layer 1: AIOS_ROOT set" { [bool]$env:AIOS_ROOT }
Test-Item "Layer 1: Repo resolves" { (git -C $env:AIOS_ROOT status 2>&1) -notmatch "fatal" }

# Fonts
Test-Item "JetBrainsMono in font registry" {
    $k = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
    [bool]($k.PSObject.Properties | Where-Object { $_.Name -like "*JetBrainsMono*" })
}
Test-Item "JetBrainsMono on T9" {
    (Get-ChildItem "T:\AIOS_TERMINAL\fonts\JetBrainsMono" -Filter "*.ttf" -EA SilentlyContinue).Count -gt 0
}

# Lazygit
Test-Item "Lazygit binary on PATH"  { [bool](Get-Command lazygit -EA SilentlyContinue) }
Test-Item "Lazygit junction valid"  { (Get-Item "$env:APPDATA\lazygit" -EA SilentlyContinue).LinkType -eq "Junction" }
Test-Item "Lazygit config on T9"    { Test-Path "T:\AIOS_TERMINAL\configs\lazygit\config.yml" }

# Yazi
Test-Item "Yazi binary on PATH"     { [bool](Get-Command yazi -EA SilentlyContinue) }
Test-Item "Yazi junction valid"     { (Get-Item "$env:APPDATA\yazi\config" -EA SilentlyContinue).LinkType -eq "Junction" }

# WezTerm
Test-Item "WezTerm binary on PATH"  { [bool](Get-Command wezterm -EA SilentlyContinue) }
Test-Item ".wezterm.lua symlink"    { [bool](Get-Item "$HOME\.wezterm.lua" -EA SilentlyContinue) }

# T9 structure
Test-Item "T9 backups present" {
    Test-Path "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\PS7_profile.ps1"
}
Test-Item "T9 folder structure intact" { Test-Path "T:\AIOS_TERMINAL\configs" }

Write-Host ""
Write-Host "  Results: $pass PASS  /  $fail FAIL" -ForegroundColor Cyan
Write-Host ""
Write-Host "MANUAL TESTS (cannot be scripted):"
Write-Host "  M1. WezTerm launches → pwsh opens → AIOS_ROOT set → git status works"
Write-Host "  M2. Lazygit opens in C:\Dev\Ai.Os → glyphs render"
Write-Host "  M3. Yazi navigates C:\Dev\Ai.Os → file icons render"
Write-Host "  M4. Windows Terminal still works independently — unchanged"
Write-Host "  M5. Layer 1 health check passes from both terminals"
```

---

## SECTION 11 — COMPLETE ROLLBACK REFERENCE

### 11.1 Nuclear Rollback (all Layer 2 tools, in reverse order)

```powershell
# Run from elevated PowerShell — removes everything added in this plan
# T9 configs are NOT touched — they survive this rollback

# Step 4 rollback: WezTerm
winget uninstall --id wez.wezterm
Remove-Item "$HOME\.wezterm.lua" -ErrorAction SilentlyContinue

# Step 3 rollback: Yazi
winget uninstall --id sxyazi.yazi
Remove-Item "$env:APPDATA\yazi\config" -ErrorAction SilentlyContinue

# Step 2 rollback: Lazygit
winget uninstall --id JesseDuffield.lazygit
Remove-Item "$env:APPDATA\lazygit" -ErrorAction SilentlyContinue

# Step 1 rollback: JetBrainsMono Nerd Font
# GUI only: Control Panel → Fonts → filter "JetBrainsMono" → Delete

Write-Host "Layer 2 rollback complete." -ForegroundColor Yellow
Write-Host "T9 configs preserved at T:\AIOS_TERMINAL\configs\" -ForegroundColor Green
Write-Host "Layer 1 (AIOS_ROOT, PS7 profile) unaffected." -ForegroundColor Green
```

### 11.2 Post-Rollback Layer 1 Verification
```powershell
# After any rollback — confirm Layer 1 still operational
pwsh -NoProfile -Command {
    $env:AIOS_ROOT = "C:\Dev\Ai.Os"
    $status = git -C $env:AIOS_ROOT status 2>&1
    if ($status -notmatch "fatal") { Write-Host "LAYER 1 OK" -ForegroundColor Green }
    else { Write-Host "LAYER 1 ISSUE: $status" -ForegroundColor Red }
}
```

### 11.3 Restore from T9 Backup (if something goes wrong)
```powershell
# Restore PS7 profile from T9 backup
Copy-Item "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\PS7_profile.ps1" `
    "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1" -Force

# Restore Windows Terminal settings from T9 backup
$wtPkg = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Filter "Microsoft.WindowsTerminal*" | Select-Object -First 1
if ($wtPkg) {
    Copy-Item "T:\AIOS_TERMINAL\backups\PRE_LAYER2_SNAPSHOT\Windows_Terminal_settings.json" `
        (Join-Path $wtPkg.FullName "LocalState\settings.json") -Force
    Write-Host "Windows Terminal settings restored." -ForegroundColor Green
}
```

---

## SECTION 12 — OPEN ITEMS BEFORE IMPLEMENTATION

| # | Item | Needed Before |
|---|------|---------------|
| I1 | Confirm T9 is assigned drive letter `T:` — if not, note actual letter and update all paths in this document | Step 0 |
| I2 | Run `winget search "JetBrainsMono"` on workstation and confirm exact package ID | Step 1 |
| I3 | Run `winget search "lazygit"` — confirm `JesseDuffield.lazygit` | Step 2 |
| I4 | Run `winget search "yazi"` — confirm `sxyazi.yazi` | Step 3 |
| I5 | Run `winget search "wezterm"` — confirm `wez.wezterm` | Step 4 |
| I6 | Confirm Developer Mode is enabled (Settings → Privacy & Security → Developer Mode) OR note that `.wezterm.lua` symlink will need elevated CMD | Step 4 |
| I7 | Decision: install Yazi optional deps (`bat`, `fd`) as part of this phase? | Step 3 |
| I8 | Confirm `C:\Dev\Ai.Os` exists and passes git health check | Gate 0 |

---

## SECTION 13 — DEPENDENCY MAP (final)

```
                    ┌─────────────────────────────────────────┐
                    │       GATE 0: Layer 1 healthy            │
                    │       T9 connected at T:\                │
                    │       Pre-install backup complete        │
                    └─────────────┬───────────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────────┐
                    │  STEP 1: JetBrainsMono Nerd Font         │
                    │  Provides: glyph rendering               │
                    │  Required by: Lazygit icons, Yazi icons, │
                    │  WezTerm font config                     │
                    └──┬──────────────────────────────────────┘
                       │
          ┌────────────┼────────────────────┐
          │            │                    │
    ┌─────▼──────┐ ┌───▼──────┐      ┌─────▼──────┐
    │  STEP 2     │ │  STEP 3  │      │   STEP 4   │
    │  Lazygit    │ │  Yazi    │      │  WezTerm   │
    │  (git UI)   │ │  (files) │      │  (terminal)│
    │             │ │          │      │            │
    │ Needs:      │ │ Needs:   │      │ Needs:     │
    │  - git      │ │  - NF    │      │  - PS7     │
    │  - NF icons │ │  - bat*  │      │  - NF font │
    │             │ │  - fd*   │      │  - config  │
    └─────────────┘ └──────────┘      └────────────┘
                                              │
                            ┌─────────────────▼───────────────┐
                            │   FULL STACK VALIDATION         │
                            │   All tools tested from WezTerm  │
                            │   AND from Windows Terminal      │
                            └─────────────────────────────────┘

  * = optional Yazi preview dependencies
```

---

*Document status: PLANNING ONLY — No installs performed — No configs written — No files changed*  
*All commands in this document are plans pending operator approval and Gate 0 confirmation*  
*Next action: Operator confirms open items (Section 12), then approves Step 0 (T9 folder creation + backup)*
