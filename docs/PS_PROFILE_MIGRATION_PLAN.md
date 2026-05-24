# AI_OS PowerShell Profile Migration Plan

**Status:** PLANNING ONLY — Do NOT apply until explicitly approved  
**Date:** 2026-05-22  
**Author:** CTO Planning Layer  
**Scope:** Move canonical PS7 profile logic out of OneDrive into `D:\AIOS_TERMINAL\configs\powershell\`  

---

## Situation

The current PS7 profile lives inside OneDrive sync:

```
C:\Users\mylab\Documents\PowerShell\Microsoft.PowerShell_profile.ps1
```

Windows syncs `Documents\` to OneDrive. This means:
- Profile writes go through OneDrive sync — introduces latency and potential lock contention on shell startup
- Profile is tied to cloud sync availability
- No portable, drive-independent backup exists on D:
- If OneDrive pauses or signs out, the profile still loads (it's local-cache), but the source-of-truth is in the cloud layer — not ideal for a hardened workstation

**Target state:** canonical logic lives on `D:\AIOS_TERMINAL\configs\powershell\` (drive-local, no cloud sync). The original `$PROFILE` path keeps a lightweight loader stub that dot-sources the canonical file. Shell startup is unchanged. Rollback is a single file restore.

---

## Architecture: Loader/Stub Pattern

```
$PROFILE (unchanged path, unchanged role)
  └─ Loader stub
       └─ dot-sources ──► D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1
                               (canonical logic lives here)
```

The loader stub is the only thing at `$PROFILE`. It is intentionally minimal — its only job is to find and load the canonical file. If D: is unavailable (drive unplugged, letter changed), the stub catches the failure gracefully and falls back to an inline emergency bootstrap so the shell never breaks.

---

## 1. Canonical Profile File

**Target path:**
```
D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1
```

**Content — identical to current profile, plus header:**
```powershell
# ============================================================
#  AI_OS Canonical PowerShell 7 Profile
#  Location : D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1
#  Loaded by: $PROFILE loader stub (dot-source)
#  Rules    : No themes. No aliases. No modules.
#             AIOS_ROOT bootstrap only.
#             Additive visual layer appended below when ready.
# ============================================================

$env:AIOS_ROOT = "C:\Dev\Ai.Os"

if (Test-Path $env:AIOS_ROOT) {
    Set-Location $env:AIOS_ROOT
}

# ── VISUAL LAYER GATE (gated append — do not move above AIOS_ROOT block) ──
# When Oh My Posh is installed, append its init block here.
# Example (do not uncomment until Gate 2):
#
# if (Get-Command oh-my-posh -ErrorAction SilentlyContinue) {
#     oh-my-posh init pwsh --config "$env:POSH_THEMES_PATH\jandedobbeleer.omp.json" | Invoke-Expression
# }
```

**Why this location:**
- `D:\AIOS_TERMINAL\configs\` is the Layer 2 config root established in Gate 0
- Drive-local, no cloud sync, no latency
- Portable: can be copied to any machine running AI_OS by plugging in D: and running the loader install
- Readable and editable without OneDrive context

---

## 2. Loader Stub (at `$PROFILE`)

**Path (unchanged — Windows requires this):**
```
C:\Users\mylab\Documents\PowerShell\Microsoft.PowerShell_profile.ps1
```

**Content:**
```powershell
# ============================================================
#  AI_OS PowerShell 7 — Profile Loader Stub
#  Location : $PROFILE (CurrentUser / CurrentHost)
#  Purpose  : Dot-source canonical profile from D:\AIOS_TERMINAL
#  Rules    : THIS FILE IS A LOADER ONLY.
#             All logic lives in AIOS_profile.ps1.
#             Do NOT add logic here.
# ============================================================

$_canonicalProfile = "D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1"

if (Test-Path $_canonicalProfile) {
    # Normal path — D: drive present, load canonical profile
    . $_canonicalProfile
} else {
    # Fallback — D: unavailable (drive unplugged / letter changed)
    # Emergency inline bootstrap keeps shell functional
    Write-Warning "[AI_OS] Canonical profile not found at $_canonicalProfile"
    Write-Warning "[AI_OS] Running emergency inline bootstrap."
    $env:AIOS_ROOT = "C:\Dev\Ai.Os"
    if (Test-Path $env:AIOS_ROOT) {
        Set-Location $env:AIOS_ROOT
    }
}

Remove-Variable _canonicalProfile -ErrorAction SilentlyContinue
```

**Key design decisions:**

| Decision | Rationale |
|----------|-----------|
| Dot-source (`. `) not `& ` (call operator) | Dot-source runs in current scope — `$env:AIOS_ROOT` and `Set-Location` propagate to the shell session. Call operator runs in a child scope and variables do not survive. |
| `$_canonicalProfile` with underscore prefix | Avoids polluting the session namespace. Cleaned up with `Remove-Variable` after load. |
| Inline emergency fallback | D: may not always be plugged in. Shell must never hard-fail on startup. Warning is surfaced so the user knows the drive is missing. |
| No `$ErrorActionPreference = 'Stop'` in stub | Loader must be fault-tolerant. Errors in canonical profile should not abort the shell open. |
| `Test-Path` not `[System.IO.File]::Exists()` | PowerShell-native, works with drive letters and UNC paths. No .NET namespace import required. |

---

## 3. Backup Procedure

Before any apply, three backup copies must exist:

### Backup A — D: drive snapshot (primary)
```powershell
# Run ONLY after Gate 0 has created D:\AIOS_TERMINAL\backups\
$snap = "D:\AIOS_TERMINAL\backups\PRE_PROFILE_MIGRATION_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $snap -Force | Out-Null
Copy-Item "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1" "$snap\ORIGINAL_profile.ps1" -Force
Write-Host "Backup A written: $snap\ORIGINAL_profile.ps1"
```

### Backup B — Local OneDrive-adjacent backup (secondary, no sync dependency)
```powershell
$localSnap = "$HOME\Documents\PowerShell\PROFILE_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss').ps1"
Copy-Item "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1" $localSnap -Force
Write-Host "Backup B written: $localSnap"
```

### Backup C — AI-OS-Project docs folder (tertiary, version-controlled when committed)
```powershell
Copy-Item "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1" `
    "C:\Users\mylab\OneDrive\AI-OS-Project\docs\PROFILE_BACKUP_PRE_MIGRATION.ps1" -Force
Write-Host "Backup C written to AI-OS-Project\docs\"
```

**Three backups, three locations. All copies before any file is touched.**

---

## 4. Apply Sequence (when approved — DO NOT RUN NOW)

```
Step 1 — Run all three backups above
Step 2 — Create D:\AIOS_TERMINAL\configs\powershell\ if not already present
Step 3 — Write AIOS_profile.ps1 to D:\AIOS_TERMINAL\configs\powershell\
Step 4 — Overwrite $PROFILE with the loader stub
Step 5 — Open a NEW pwsh window (do not close the current one yet)
Step 6 — Run validation procedure in the new window
Step 7 — Only after validation passes: close original window
```

**Critical safety rule:** keep the original shell window open until the new one validates. If anything fails, the original window's environment is already functional for rollback.

---

## 5. Validation Procedure

Run these checks in a fresh `pwsh` window after apply:

```powershell
# ── VALIDATION SCRIPT ──────────────────────────────────────
# Run in a NEW pwsh window after loader stub is in place.

$pass = 0; $fail = 0

function V-Pass { param($m) $script:pass++; Write-Host "  [PASS] $m" -ForegroundColor Green }
function V-Fail { param($m) $script:fail++; Write-Host "  [FAIL] $m" -ForegroundColor Red }

# 1. Confirm $PROFILE path is correct
$expectedProfile = "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1"
if ($PROFILE -eq $expectedProfile) { V-Pass "`$PROFILE path unchanged: $PROFILE" }
else { V-Fail "`$PROFILE path changed unexpectedly: $PROFILE" }

# 2. Confirm loader stub is in place (not the canonical logic)
$profileContent = Get-Content $PROFILE -Raw
if ($profileContent -match 'AIOS_TERMINAL\\configs\\powershell\\AIOS_profile') {
    V-Pass "Loader stub detected at `$PROFILE"
} else {
    V-Fail "Loader stub NOT detected — profile may not have been updated"
}

# 3. Confirm canonical file exists on D:
$canonical = "D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1"
if (Test-Path $canonical) { V-Pass "Canonical profile exists: $canonical" }
else { V-Fail "Canonical profile NOT FOUND: $canonical" }

# 4. Confirm AIOS_ROOT was set (proves dot-source worked)
if ($env:AIOS_ROOT -eq "C:\Dev\Ai.Os") { V-Pass "AIOS_ROOT = $env:AIOS_ROOT" }
else { V-Fail "AIOS_ROOT not set correctly (got: '$env:AIOS_ROOT')" }

# 5. Confirm current location is C:\Dev\Ai.Os (or that it exists)
if (Test-Path "C:\Dev\Ai.Os") { V-Pass "C:\Dev\Ai.Os exists" }
else { V-Fail "C:\Dev\Ai.Os does not exist — Set-Location target missing" }

# 6. PS7 version check
if ($PSVersionTable.PSVersion.Major -ge 7) { V-Pass "PowerShell $($PSVersionTable.PSVersion)" }
else { V-Fail "Not running PS7" }

Write-Host ""
Write-Host "  PASSED: $pass   FAILED: $fail"
if ($fail -eq 0) {
    Write-Host "  STATUS: MIGRATION VALIDATED — safe to close original window" -ForegroundColor Cyan
} else {
    Write-Host "  STATUS: VALIDATION FAILED — DO NOT close original window. Run rollback." -ForegroundColor Red
}
```

---

## 6. Rollback Procedure

If validation fails, restore in under 30 seconds:

```powershell
# ── ROLLBACK ───────────────────────────────────────────────
# Run from the ORIGINAL pwsh window (the one open before apply).
# Or run from any pwsh — the backup files are the source of truth.

# Option A — Restore from Backup B (local, fastest)
$backupFile = Get-ChildItem "$HOME\Documents\PowerShell" -Filter 'PROFILE_BACKUP_*.ps1' |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($backupFile) {
    Copy-Item $backupFile.FullName "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1" -Force
    Write-Host "[ROLLBACK] Restored from: $($backupFile.FullName)"
} else {
    # Option B — Restore from Backup A on D:
    $snap = Get-ChildItem "D:\AIOS_TERMINAL\backups" -Filter 'PRE_PROFILE_MIGRATION_*' |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($snap) {
        Copy-Item (Join-Path $snap.FullName 'ORIGINAL_profile.ps1') `
            "$HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1" -Force
        Write-Host "[ROLLBACK] Restored from D: snapshot: $($snap.FullName)"
    } else {
        Write-Host "[ROLLBACK MANUAL] Write this content to $HOME\Documents\PowerShell\Microsoft.PowerShell_profile.ps1 :"
        Write-Host '---'
        Write-Host '$env:AIOS_ROOT = "C:\Dev\Ai.Os"'
        Write-Host 'if (Test-Path $env:AIOS_ROOT) { Set-Location $env:AIOS_ROOT }'
        Write-Host '---'
    }
}

Write-Host "[ROLLBACK] Open a new pwsh window to confirm profile loads correctly."
```

**After rollback:** open a new `pwsh` window and confirm `$env:AIOS_ROOT` is set. If it is, rollback succeeded.

---

## 7. Risk Register

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| R1 | D: drive not present at shell open | 🟡 Medium | Loader stub has inline emergency fallback — shell never hard-fails |
| R2 | D: drive letter changes (USB reassignment) | 🟡 Medium | Emergency fallback activates; update stub with new letter |
| R3 | Dot-source fails (syntax error in canonical file) | 🟡 Medium | Error surfaced but does not abort shell open; fallback not triggered (separate code path) |
| R4 | OneDrive de-syncs `$PROFILE` | 🟢 Low | Local cache always present; loader stub is tiny and stable |
| R5 | Backup files deleted before rollback needed | 🟢 Low | Three backup copies across three locations |
| R6 | Oh My Posh block added to wrong file | 🟢 Low | Visual layer gate comment in canonical file makes correct location explicit |

---

## 8. File Inventory (post-apply state)

| File | Role | Location | Synced to cloud? |
|------|------|----------|-----------------|
| `Microsoft.PowerShell_profile.ps1` | Loader stub only | `$HOME\Documents\PowerShell\` | Yes (OneDrive) — intentional, stub is safe to sync |
| `AIOS_profile.ps1` | Canonical logic | `D:\AIOS_TERMINAL\configs\powershell\` | No — drive-local |
| `ORIGINAL_profile.ps1` | Pre-migration backup A | `D:\AIOS_TERMINAL\backups\PRE_PROFILE_MIGRATION_*\` | No |
| `PROFILE_BACKUP_*.ps1` | Pre-migration backup B | `$HOME\Documents\PowerShell\` | Yes (OneDrive) |
| `PROFILE_BACKUP_PRE_MIGRATION.ps1` | Pre-migration backup C | `AI-OS-Project\docs\` | Yes (OneDrive) |

---

## Summary

```
BEFORE:
  $PROFILE  ──►  AIOS_ROOT logic (inline)   [OneDrive-synced]

AFTER:
  $PROFILE  ──►  Loader stub                [OneDrive-synced, safe]
                    └─ dot-sources ──►  D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1
                                            [drive-local, no sync, canonical]

FALLBACK (D: absent):
  $PROFILE  ──►  Loader stub
                    └─ Test-Path fails ──►  Inline emergency bootstrap
                                            [warning printed, shell stays functional]
```

**This plan requires zero destructive operations. Original file is copied, not moved. Rollback is a single `Copy-Item`. Shell startup behavior is identical in all paths.**

---

*PLANNING ONLY — apply only after explicit approval*  
*Generated: 2026-05-22 | AI_OS CTO Planning Layer*
