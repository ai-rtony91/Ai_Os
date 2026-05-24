# AI_OS TERMINAL ARCHITECTURE PLAN
**Document ID:** TERMINAL-ARCH-001  
**Date:** 2026-05-22  
**Status:** PLANNING ONLY — No installs performed  
**Author:** Operator (Tony) / Claude  
**Scope:** Layered terminal environment for AI_OS Trading Lab workstation  
**Portability target:** Samsung T9 portable SSD

---

## OVERVIEW

This document defines a two-layer terminal architecture for the AI_OS development and trading workstation. The design principle is strict separation: the stable base layer runs independently of the visual layer. The visual layer is entirely additive and reversible. Neither layer contaminates the other.

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2 — OPTIONAL VISUAL LAYER  (additive, reversible)    │
│  WezTerm · Oh My Posh · Nerd Fonts · Yazi · Lazygit         │
├─────────────────────────────────────────────────────────────┤
│  LAYER 1 — STABLE BASE LAYER  (operational today)           │
│  Windows Terminal · PowerShell 7 · AIOS_ROOT profile        │
│  C:\Dev\Ai.Os canonical repo root                           │
└─────────────────────────────────────────────────────────────┘
```

**Golden rule:** Layer 1 must always be fully operational regardless of Layer 2 state. If every visual tool is uninstalled tomorrow, the AI_OS environment continues functioning without interruption.

---

## PART 1 — STABLE BASE LAYER (Layer 1)

### 1.1 Components

| Component | Status | Path |
|-----------|--------|------|
| Windows Terminal | Installed | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_*` |
| PowerShell 7.6.2 | Installed | `C:\Program Files\WindowsApps\Microsoft.PowerShell_7.6.2.0_x64__8` |
| AIOS_ROOT profile | Created 2026-05-22 | `%USERPROFILE%\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` |
| Canonical repo root | Pending confirmation | `C:\Dev\Ai.Os` |

### 1.2 Current PS7 Profile (locked — do not modify for visual tooling)

```powershell
# Documents\PowerShell\Microsoft.PowerShell_profile.ps1
$env:AIOS_ROOT = "C:\Dev\Ai.Os"
if (Test-Path $env:AIOS_ROOT) {
    Set-Location $env:AIOS_ROOT
}
```

This profile is **sealed**. Visual layer tooling gets its own separate profile mechanism. See Section 3.3.

### 1.3 Layer 1 Health Check Commands

Run these to confirm base layer is operational before touching Layer 2:

```powershell
# Confirm PS7 is running
$PSVersionTable.PSVersion

# Confirm AIOS_ROOT is set
$env:AIOS_ROOT

# Confirm repo resolves
git -C $env:AIOS_ROOT status
git -C $env:AIOS_ROOT remote -v

# Confirm Windows Terminal launches pwsh correctly
# (visual check — open Windows Terminal, verify it opens PS7 not PS5)
```

---

## PART 2 — OPTIONAL VISUAL LAYER (Layer 2)

### 2.1 Component Registry

| Tool | Role | Config format | Machine-bound? | Portable? |
|------|------|---------------|----------------|-----------|
| **Nerd Fonts** | Glyph/icon rendering for all visual tools | Windows font install | ✅ Yes (font registry) | Partial — font files portable, install is not |
| **WezTerm** | Alternative GPU-accelerated terminal emulator | Lua (`.wezterm.lua`) | Binary only | ✅ Config fully portable |
| **Oh My Posh** | PS7 prompt theming engine | JSON/YAML theme file | Binary only | ✅ Theme file fully portable |
| **Yazi** | Terminal file manager (replaces `cd` + `ls` workflow) | TOML (`yazi.toml`, `keymap.toml`, `theme.toml`) | Binary only | ✅ Config fully portable |
| **Lazygit** | Terminal git UI (replaces raw `git` commands) | YAML (`config.yml`) | Binary only | ✅ Config fully portable |

### 2.2 What Each Tool Does for the AI_OS Workflow

**Nerd Fonts**  
Prerequisite for everything else. Renders the patched glyphs (arrows, git branch icons, file type icons, status dots) that Oh My Posh, Yazi, and Lazygit use for their UIs. Without a Nerd Font set in the terminal, all other tools render broken box characters.

Recommended font: **CaskaydiaCove Nerd Font** (based on Cascadia Code — Microsoft's own monospace, matches the Windows Terminal default feel, includes all required glyphs).  
Alternative: **JetBrainsMono Nerd Font** (heavier weight, very readable on ultrawide).

**WezTerm**  
A Lua-configured GPU terminal. Its value over Windows Terminal for the AI_OS use case: multiplexed panes without a mouse, tab bar configuration in code, per-pane color rules (e.g. Trading Lab pane = different background), and a single `.wezterm.lua` file that travels everywhere. WezTerm does NOT replace Windows Terminal — it runs alongside it. Use whichever fits the session.

**Oh My Posh**  
Renders a structured prompt in PS7 showing: git branch, git dirty/clean state, current path, execution time of last command, and a right-side clock. For an 8-hour trading session this eliminates cognitive overhead of constantly running `git status` just to know what branch you are on.

**Yazi**  
Terminal file manager. Replaces `explorer.exe` browsing during AI_OS work. Renders file trees with icons, previews markdown/JSON files inline, navigates with `hjkl` vim keys. Critical benefit for AI_OS: when reviewing 40+ automation scripts, Yazi lets you navigate the tree and preview file content without opening VSCode or running `cat` repeatedly.

**Lazygit**  
Full-screen terminal git UI. Shows staged/unstaged changes, branch list, commit log, diff view, and stash — all in one window. For AI_OS's strict DRY_RUN → APPLY → selective commit workflow, Lazygit makes selective staging visual and auditable. Eliminates the risk of accidental `git add .` by making file-by-file staging the default UX.

---

## PART 3 — DEPENDENCY MAP

```
INSTALLATION DEPENDENCY CHAIN
══════════════════════════════

[Nerd Fonts] ──────────────────────────────────────────────────┐
     │                                                         │
     ├──▶ [WezTerm]          (font must exist before launch)   │
     │         │                                               │
     │         └──▶ set font_size + font_family in .wezterm.lua│
     │                                                         │
     ├──▶ [Oh My Posh]       (glyphs needed for prompt icons)  │
     │         │                                               │
     │         └──▶ requires PS7 already operational           │
     │                   │                                     │
     │                   └──▶ Layer 1 must pass health check   │
     │                                                         │
     └──▶ [Yazi]             (icons need Nerd Font glyphs)     │
               │                                               │
               └──▶ independent of Oh My Posh / WezTerm       │
                                                               │
[Lazygit] ─────────────────────────────────────────────────────┘
     │     (standalone — only needs git on PATH)
     │
     └──▶ No glyph dependency — works without Nerd Fonts
          (but looks better with them for diff symbols)


STRICT DEPENDENCY ORDER:
  1. Nerd Fonts     ← nothing else works correctly without this
  2. WezTerm        ← terminal host (independent of PS7 config)
  3. Lazygit        ← no deps beyond git
  4. Yazi           ← no deps beyond Nerd Font for icons
  5. Oh My Posh     ← requires PS7 + Nerd Font; wired last
```

---

## PART 4 — INSTALLATION ORDER (when approved)

> **Status: PLANNED ONLY. Do not execute until operator gives explicit written approval per step.**

### Step 1 — Nerd Fonts *(machine-bound)*
```
Tool     : CaskaydiaCove Nerd Font (recommended) or JetBrainsMono Nerd Font
Source   : https://github.com/ryanoasis/nerd-fonts/releases
Installer: Download .zip → extract → right-click .ttf → Install for all users
Machine  : WORKSTATION only (must reinstall on any new machine)
T9 action: Copy raw .ttf font files to T9:\AIOS_TERMINAL\fonts\ for portability
Validation: Open Character Map → search "CaskaydiaCove" → glyphs visible
Rollback : Control Panel → Fonts → uninstall
```

### Step 2 — WezTerm *(binary machine-bound, config portable)*
```
Tool     : WezTerm (stable release)
Source   : https://wezfurlong.org/wezterm/installation.html
Installer: winget install --id wez.wezterm  (or .exe installer)
Config   : %USERPROFILE%\.wezterm.lua
T9 action: Canonical .wezterm.lua lives on T9:\AIOS_TERMINAL\configs\
           Symlink on machine: mklink %USERPROFILE%\.wezterm.lua T9:\AIOS_TERMINAL\configs\.wezterm.lua
Validation: Launch WezTerm → confirm Nerd Font renders → confirm pwsh launches → confirm AIOS_ROOT sets
Rollback : Uninstall via winget remove wez.wezterm — config file unaffected
```

### Step 3 — Lazygit *(binary machine-bound, config portable)*
```
Tool     : Lazygit latest
Source   : https://github.com/jesseduffield/lazygit/releases
Installer: winget install --id JesseDuffield.lazygit
Config   : %APPDATA%\lazygit\config.yml
T9 action: Canonical config.yml lives on T9:\AIOS_TERMINAL\configs\lazygit\
           Symlink: mklink /D %APPDATA%\lazygit T9:\AIOS_TERMINAL\configs\lazygit
Validation: cd C:\Dev\Ai.Os → lazygit → UI opens → branch visible → no git errors
Rollback : winget remove JesseDuffield.lazygit — config on T9 unaffected
```

### Step 4 — Yazi *(binary machine-bound, config portable)*
```
Tool     : Yazi latest stable
Source   : https://github.com/sxyazi/yazi/releases
Installer: winget install --id sxyazi.yazi
Config   : %APPDATA%\yazi\config\  (yazi.toml, keymap.toml, theme.toml)
T9 action: Canonical configs live on T9:\AIOS_TERMINAL\configs\yazi\
           Symlink: mklink /D %APPDATA%\yazi\config T9:\AIOS_TERMINAL\configs\yazi
Validation: Open pwsh → yazi → navigates to C:\Dev\Ai.Os → file icons render with glyphs
Rollback : winget remove sxyazi.yazi — config on T9 unaffected
```

### Step 5 — Oh My Posh *(binary machine-bound, theme file portable)*
```
Tool     : Oh My Posh latest
Source   : https://ohmyposh.dev/docs/installation/windows
Installer: winget install JanDeDobbeleer.OhMyPosh
Theme    : Custom AI_OS theme file → T9:\AIOS_TERMINAL\configs\ohmyposh\aios.omp.json
Machine  : Theme referenced by path from the VISUAL layer profile (not the AIOS_ROOT profile)
Validation: . $PROFILE.CurrentUserCurrentHost → prompt renders with git branch + icons
Rollback : Remove Oh My Posh init line from visual profile — base profile unaffected
```

---

## PART 5 — PROFILE LAYERING STRATEGY

The base PS7 profile is sealed. Oh My Posh gets wired into a **separate profile mechanism** to preserve that isolation.

### 5.1 Profile File Map

```
%USERPROFILE%\Documents\PowerShell\
├── Microsoft.PowerShell_profile.ps1     ← LAYER 1 (sealed — AIOS_ROOT only)
└── (no other files)

%USERPROFILE%\Documents\PowerShell\          ← same folder
    Microsoft.PowerShell_profile.ps1          ← Layer 1 stays here
```

**The visual layer uses an environment variable gate inside the base profile** — not a second profile file. When Oh My Posh is ready to activate, a single guarded block is appended to the base profile:

```powershell
# LAYER 2 VISUAL BLOCK — append to base profile when approved
# Gated: only loads if Oh My Posh binary exists on this machine
# Does NOT break Layer 1 if Oh My Posh is absent
if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
    $env:POSH_THEME = "T:\AIOS_TERMINAL\configs\ohmyposh\aios.omp.json"
    oh-my-posh init pwsh --config $env:POSH_THEME | Invoke-Expression
}
```

Key properties of this design:
- If Oh My Posh is not installed, the block silently skips — Layer 1 is unaffected
- If the T9 is not connected, `$env:POSH_THEME` path fails gracefully — Layer 1 is unaffected
- Removing the visual layer = deleting these three lines, nothing else
- The base AIOS_ROOT bootstrap runs before this block, so `$env:AIOS_ROOT` and `Set-Location` always execute regardless of Oh My Posh state

### 5.2 WezTerm Shell Launch Config

WezTerm must be configured to launch `pwsh` (not `cmd` or `powershell.exe`) so it inherits the PS7 profile and AIOS_ROOT.

```lua
-- .wezterm.lua — relevant section only
config.default_prog = { 'pwsh', '-NoLogo' }
```

This ensures WezTerm sessions automatically land in `C:\Dev\Ai.Os` via the base profile, identical to Windows Terminal behavior.

---

## PART 6 — CONFIG LOCATIONS MASTER TABLE

| Tool | Windows default config path | Portable? | T9 target path | Symlink strategy |
|------|----------------------------|-----------|----------------|------------------|
| PS7 base profile | `%USERPROFILE%\Documents\PowerShell\Microsoft.PowerShell_profile.ps1` | Manual copy | `T:\AIOS_TERMINAL\configs\powershell\` | Copy on migration |
| WezTerm | `%USERPROFILE%\.wezterm.lua` | ✅ Full | `T:\AIOS_TERMINAL\configs\.wezterm.lua` | `mklink` file junction |
| Oh My Posh theme | Operator-defined path | ✅ Full | `T:\AIOS_TERMINAL\configs\ohmyposh\aios.omp.json` | Direct path reference |
| Lazygit | `%APPDATA%\lazygit\config.yml` | ✅ Full | `T:\AIOS_TERMINAL\configs\lazygit\config.yml` | `mklink /D` directory junction |
| Yazi | `%APPDATA%\yazi\config\` | ✅ Full | `T:\AIOS_TERMINAL\configs\yazi\` | `mklink /D` directory junction |
| Nerd Fonts | `C:\Windows\Fonts\` | ⚠️ Partial | `T:\AIOS_TERMINAL\fonts\` (raw .ttf files) | No symlink — must reinstall per machine |
| Windows Terminal | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_*\LocalState\settings.json` | ✅ Full | `T:\AIOS_TERMINAL\configs\windows-terminal\settings.json` | Copy on migration |

---

## PART 7 — SAMSUNG T9 PORTABILITY STRATEGY

### 7.1 T9 Folder Structure (proposed)

```
T:\AIOS_TERMINAL\
├── configs\
│   ├── .wezterm.lua                    ← WezTerm full config
│   ├── powershell\
│   │   └── Microsoft.PowerShell_profile.ps1   ← backup of base profile
│   ├── ohmyposh\
│   │   └── aios.omp.json              ← AI_OS Oh My Posh theme
│   ├── lazygit\
│   │   └── config.yml                 ← Lazygit config
│   ├── yazi\
│   │   ├── yazi.toml
│   │   ├── keymap.toml
│   │   └── theme.toml
│   └── windows-terminal\
│       └── settings.json              ← Windows Terminal profile backup
├── fonts\
│   ├── CaskaydiaCoveNerdFont-Regular.ttf
│   ├── CaskaydiaCoveNerdFont-Bold.ttf
│   └── CaskaydiaCoveNerdFont-Italic.ttf
└── bootstrap\
    └── New-AIOSTerminalBootstrap.ps1  ← future: one-script machine setup
```

### 7.2 Portable vs Machine-Bound Separation

```
PORTABLE (travels with T9 — survives machine wipe):
  ✅ .wezterm.lua            — full WezTerm environment in one Lua file
  ✅ aios.omp.json           — full prompt theme
  ✅ lazygit config.yml      — key bindings, diff pager, git hooks
  ✅ yazi toml configs       — file manager layout, keymaps, icons
  ✅ PS7 profile backup      — AIOS_ROOT + visual block
  ✅ Windows Terminal JSON   — profile definitions, color schemes, keybindings
  ✅ Font .ttf files         — raw font files for reinstall

MACHINE-BOUND (must reinstall per workstation):
  ⚠️ Nerd Font install       — goes into Windows Font registry
  ⚠️ WezTerm binary          — installed to %LOCALAPPDATA% or Program Files
  ⚠️ Oh My Posh binary       — installed via winget or %LOCALAPPDATA%
  ⚠️ Lazygit binary          — winget install
  ⚠️ Yazi binary             — winget install
  ⚠️ PS7 itself              — installed via WindowsApps or winget
```

### 7.3 New Machine Bootstrap Sequence (future script — not yet written)

When moving to a new workstation with the T9 connected:

```
1. Install PS7             (winget install Microsoft.PowerShell)
2. Install Nerd Fonts      (copy from T:\AIOS_TERMINAL\fonts\ → Install for all users)
3. Install WezTerm         (winget install wez.wezterm)
4. Install Lazygit         (winget install JesseDuffield.lazygit)
5. Install Yazi            (winget install sxyazi.yazi)
6. Install Oh My Posh      (winget install JanDeDobbeleer.OhMyPosh)
7. Create symlinks         (mklink commands pointing AppData → T:\AIOS_TERMINAL\configs\)
8. Copy/write PS7 profile  (copy from T:\AIOS_TERMINAL\configs\powershell\)
9. Clone or copy C:\Dev\Ai.Os from T9 or GitHub remote
10. Validate               (run Layer 1 health check commands)
```

This sequence is idempotent — running it twice on the same machine is safe.

---

## PART 8 — ROLLBACK PLAN

Each layer rolls back independently. No rollback of Layer 2 ever touches Layer 1.

### Rollback: Oh My Posh only
```powershell
# Remove 3-line visual block from PS7 profile
# Layer 1 AIOS_ROOT bootstrap continues unaffected
# Oh My Posh binary can remain installed — it simply won't be called
```

### Rollback: WezTerm only
```
1. Close WezTerm
2. Continue using Windows Terminal (unchanged)
3. winget remove wez.wezterm   (optional — leaving it installed is harmless)
4. .wezterm.lua on T9 unaffected
```

### Rollback: Lazygit only
```
1. winget remove JesseDuffield.lazygit
2. Continue using raw git commands
3. Config on T9 unaffected
```

### Rollback: Yazi only
```
1. winget remove sxyazi.yazi
2. Continue using cd + dir or Explorer
3. Config on T9 unaffected
```

### Rollback: Nerd Fonts only
```
1. Control Panel → Fonts → delete CaskaydiaCove (or JetBrainsMono) entries
2. Oh My Posh prompt degrades to text-only (no glyphs) — still functional
3. Yazi still works — file icons render as fallback text characters
4. Layer 1 completely unaffected
```

### Full Layer 2 rollback (nuclear)
```
1. winget remove wez.wezterm JesseDuffield.lazygit sxyazi.yazi JanDeDobbeleer.OhMyPosh
2. Uninstall Nerd Fonts via Control Panel
3. Remove visual block from PS7 profile (3 lines)
4. Layer 1 is exactly as it was before any Layer 2 work
```

---

## PART 9 — SAFEST IMPLEMENTATION SEQUENCE

When the operator approves implementation, follow this sequence. Each step is independently testable with a clear pass/fail before proceeding.

```
┌─────────────────────────────────────────────────────────────────┐
│  GATE 0: Confirm Layer 1 operational                            │
│  Test: git -C $env:AIOS_ROOT status → must return clean output  │
│  If fail: DO NOT PROCEED. Fix Layer 1 first.                    │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Install Nerd Fonts                                     │
│  Test: Open Character Map → search glyph → visible              │
│  Rollback: Uninstall from Fonts control panel                   │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Install Lazygit (lowest risk — no terminal dependency) │
│  Test: cd C:\Dev\Ai.Os → lazygit → UI opens                     │
│  Rollback: winget remove lazygit                                │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Install Yazi                                           │
│  Test: yazi C:\Dev\Ai.Os → tree renders with icons             │
│  Rollback: winget remove yazi                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Install WezTerm + write .wezterm.lua config            │
│  Test: Launch WezTerm → pwsh opens → AIOS_ROOT sets → git works │
│  STOP CHECK: Windows Terminal still works independently         │
│  Rollback: winget remove wezterm                                │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Create T9 folder structure + symlinks                  │
│  Test: All config paths resolve through T9 symlinks             │
│  Rollback: Delete symlinks → configs revert to AppData defaults │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Install Oh My Posh + write aios.omp.json theme         │
│  Test: In WezTerm AND Windows Terminal → prompt renders         │
│  STOP CHECK: PS7 base profile still intact (AIOS_ROOT loads)   │
│  Rollback: Remove 3-line visual block from profile              │
└────────────────────────┬────────────────────────────────────────┘
                         │ PASS
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  FINAL VALIDATION: Full stack test                              │
│  1. Open WezTerm → PS7 → AIOS_ROOT → Oh My Posh prompt renders │
│  2. git status shows in prompt automatically                    │
│  3. lazygit opens in C:\Dev\Ai.Os cleanly                       │
│  4. yazi navigates repo tree with icons                         │
│  5. Close WezTerm → open Windows Terminal → Layer 1 still works │
└─────────────────────────────────────────────────────────────────┘
```

---

## PART 10 — AI_OS THEME DESIGN NOTES (Oh My Posh)

The `aios.omp.json` theme file will be built from scratch (not based on an existing community theme) to match the AI_OS trading terminal aesthetic. Design targets:

```
Prompt segments (left side, left-to-right):
  [AIOS_ROOT shortpath]  [git branch]  [git dirty indicator]  [venv if active]

Prompt segments (right side):
  [last command exit status]  [execution time]  [24h clock HH:MM]

Color palette:
  Background    : #0D1117  (near-black — low fatigue for 8hr sessions)
  Primary text  : #E6EDF3  (off-white)
  Branch color  : #2563EB  (blue — matches MAIN CONTROL lane color in registry)
  Dirty/warning : #F59E0B  (amber — matches trading caution color)
  Error/blocked : #EF4444  (red — matches recovery lane color in registry)
  Clean/pass    : #22C55E  (green — matches save/git lane color)
  Clock         : #64748B  (muted slate — peripheral info, low visual weight)

Typography:
  Font          : CaskaydiaCove Nerd Font Regular
  Size          : 12pt (workstation) / 11pt (if used in smaller pane)
```

This palette is intentionally borrowed from the `AIOS_WORKTREE_LANE_REGISTRY.json` tab colors so that the prompt color language matches the terminal lane color language — reducing cognitive load when reading across panes.

---

## PART 11 — WEZTERM CONFIG DESIGN NOTES

The `.wezterm.lua` will be minimal and AI_OS-specific. Key behaviors:

```lua
-- Launch PS7, never cmd or PS5
config.default_prog = { 'pwsh', '-NoLogo' }

-- Font matches Oh My Posh theme
config.font = wezterm.font('CaskaydiaCove Nerd Font')
config.font_size = 12.0

-- Color scheme aligned with AIOS lane palette
config.color_scheme = 'Tokyo Night'  -- or custom AIOS scheme

-- Tab bar shows lane identity
config.use_fancy_tab_bar = false
config.tab_bar_at_bottom = true

-- No bell — never during a trading session
config.audible_bell = 'Disabled'

-- Scrollback — generous for long DRY_RUN outputs
config.scrollback_lines = 10000

-- Pane split keys — replicate the 5-lane worker layout
-- (keybindings TBD at implementation time)
```

Full `.wezterm.lua` will be written as a separate implementation file when Step 4 is approved.

---

## APPENDIX A — TOOL REFERENCE LINKS

| Tool | Repo / Docs | Latest stable |
|------|-------------|---------------|
| Nerd Fonts | https://github.com/ryanoasis/nerd-fonts | v3.x |
| WezTerm | https://wezfurlong.org/wezterm/ | Latest stable channel |
| Oh My Posh | https://ohmyposh.dev/ | Latest via winget |
| Yazi | https://github.com/sxyazi/yazi | Latest stable |
| Lazygit | https://github.com/jesseduffield/lazygit | Latest stable |
| CaskaydiaCove NF | https://github.com/ryanoasis/nerd-fonts/releases | Included in NF v3.x |

---

## APPENDIX B — OPEN DECISIONS (requires operator input before implementation)

| # | Decision | Options |
|---|----------|---------|
| D1 | Nerd Font choice | CaskaydiaCove (recommended) vs JetBrainsMono vs Other |
| D2 | WezTerm as primary or secondary terminal | Primary (replace WT) vs Secondary (run alongside) |
| D3 | Oh My Posh theme color scheme | Use AIOS lane palette (recommended) vs community theme |
| D4 | T9 drive letter | T: (proposed) vs whatever letter Windows assigns |
| D5 | Symlink strategy | mklink (file) / mklink /D (dir) vs manual copy on migration |
| D6 | Yazi as default file navigator | Replace `cd`+`ls` habit vs keep as optional overlay |

---

*Document status: PLANNING ONLY — No installs performed — No files changed outside this document*  
*Next action: Operator reviews and approves implementation gating sequence (Part 9)*
