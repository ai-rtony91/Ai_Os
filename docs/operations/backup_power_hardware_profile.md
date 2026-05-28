# AI_OS Backup / Power / Hardware Profile

## 1. Purpose

This file stores current known facts and constraints for:

- AI_OS Backup Officer
- AI_OS Maintenance Officer
- T9 backup planning
- Wake / sleep / restart planning
- Future Backup Officer status window
- Future Task Scheduler / Wake-on-LAN decisions

This document is reference context only. It does not approve implementation, power setting changes, BIOS changes, Task Scheduler setup, VPN changes, adapter changes, backup execution, or restart policy changes.

## 2. Current Machine Identity

- Machine family: HP OMEN 16L Gaming Desktop TG03-0xxx
- Monitor: AOC gaming monitor
- Repo path: `C:\Dev\Ai.Os`
- T9 target: `D:\T9_FOB`
- User workflow: ChatGPT, Claude, Codex, CLI terminal, VS Code / coding environment
- Main issue: system can slow mid-day during heavy AI/dev sessions
- Desired behavior: safe daily maintenance/restart/backup behavior without disrupting active development

## 3. Known Power-State Facts From Claude-West Recon

- System does not have traditional S3 sleep.
- System uses S0 Modern Standby / S0 Low Power Idle.
- Hibernate S4 is available.
- Fast Startup is available.
- Task Scheduler wake timers appear viable on AC.
- Fully-off S5 automatic power-on is not confirmed.
- BIOS support for S5 Wake-on-LAN or RTC scheduled power-on is unknown until manual BIOS inspection.
- Modern Standby changes how sleep/wake should be interpreted.

Modern Standby means the system is semi-on rather than traditional S3 sleep. Therefore, backup and maintenance automation should prefer guarded restart, Modern Standby, wake timers, and hibernate testing before relying on full shutdown automation.

## 4. Backup Lanes

### Lane 1 - Scheduled Backup

- Runs three times per day.
- Purpose: routine safety snapshot.
- Should eventually use Task Scheduler / Backup Officer.
- Must verify T9 is connected before backing up.

### Lane 2 - Post-Push / Post-Progress Backup

- Runs after major work, commit, push, or milestone.
- Purpose: preserve exact milestone state.
- Preferred sequence:

```text
commit -> push -> T9 backup -> verify backup report -> optional guarded restart / sleep
```

### Lane 3 - Manual Emergency Backup

- Human Owner can trigger manually after large work.
- Should not depend on automatic wake logic.

## 5. T9 Backup Doctrine

- T9 destination: `D:\T9_FOB`
- Backup must copy repo/state to T9.
- Backup Officer must write a report.
- Backup must not delete source files.
- Backup must not use destructive mirror/delete mode unless separately approved.
- Backup must not commit, push, merge, or edit repo files.
- Backup must skip if T9 is missing.
- Backup must separate source/schema/test files from telemetry runtime outputs.
- Backup must identify generated/runtime files clearly.

Existing workflow context: `docs/workflows/AI_OS_T9_BACKUP_WORKFLOW.md` owns the detailed T9 backup workflow specification. This profile records cross-cutting hardware, power, and operator context only.

## 6. Maintenance Officer Doctrine

AI_OS Maintenance Officer should eventually handle:

- daily guarded restart
- cache/session refresh
- restart-window checks
- active-work protection
- post-restart health check

Safe restart rules:

Maintenance Officer may restart only when:

- no backup is running
- no Codex task is working
- no Claude task is working
- no terminal command is active
- no git operation is active
- no `AIOS_NO_RESTART.lock` exists
- no uncommitted high-value work is at risk
- Human Owner has not disabled maintenance
- T9 backup is complete or not required

Suggested lock file:

```text
automation/orchestration/runtime/AIOS_NO_RESTART.lock
```

Do not create the lock file from this document. Only document it.

## 7. Ethernet / Adapter / VPN Facts

- Machine is Ethernet-capable through an external USB-C hub / adapter.
- Ethernet is not confirmed as a direct motherboard Ethernet connection.
- Hardware link provided by Human Owner: https://www.amazon.com/dp/B0CQSZYWT8?ref=ppx_yo2ov_dt_b_fed_asin_title
- Product appears to be an Acer USB-C hub / 9-in-1 USB-C-to-Ethernet adapter with RJ45/Ethernet support.
- Wake-on-LAN behavior through adapters/docks can differ from built-in Ethernet.
- Do not assume S5 Wake-on-LAN works through this adapter until tested.
- ProtonVPN is used.
- ProtonVPN may affect network routing, local discovery, remote wake helpers, or status checks.
- Do not modify ProtonVPN configuration without explicit Human Owner approval.
- Network adapter details must be treated as operational context, not as permission to change network settings.

## 8. Samsung Fold 6 Role

- Human Owner uses Samsung Fold 6.
- Fold 6 may be relevant as a possible operator device, wake trigger helper, status viewer, or manual backup companion.
- Fold 6 must not be treated as a required dependency unless future testing proves it is necessary.
- Do not design a system that requires the Fold 6 to be plugged in unless Human Owner explicitly approves that route.
- If used, Fold 6 should be treated as optional support hardware, not primary backup authority.

## 9. External Hardware Options

### Option A - Windows Task Scheduler + Modern Standby

- Primary recommendation.
- Least hardware complexity.

### Option B - Hibernate + Wake Timers

- Good fallback if Modern Standby timing is unreliable.

### Option C - BIOS Scheduled Power-On

- Only possible if OMEN BIOS supports RTC / BIOS Power-On.
- Requires manual BIOS verification.

### Option D - Ethernet Wake-on-LAN

- Requires Ethernet path, adapter/NIC support, BIOS support, Windows support, and a wake packet sender.
- More reliable with wired Ethernet than Wi-Fi.
- Adapter-based Ethernet must be tested before relying on it.

### Option E - Raspberry Pi Or Router As WOL Sender

- Good future option if external wake commander is needed.
- Should be considered cleaner than unsafe power-cut methods.

### Option F - Smart Plug

- Last resort only.
- Must not cut power while Windows is running.
- Only useful if BIOS supports restore-after-power-loss behavior.
- Not recommended as primary maintenance strategy.

## 10. Backup Officer Status Window Concept

Desired future small window:

```text
AI_OS Backup / Maintenance Status Window
```

Must show:

- T9 connected: YES/NO
- current branch
- latest commit
- GitHub sync status
- last backup time
- backup running: YES/NO
- copied file count
- error count
- next scheduled backup
- next maintenance window
- restart blocked: YES/NO
- block reason
- Codex active: YES/NO
- Claude active: YES/NO
- terminal active: YES/NO
- RAM usage
- CPU usage
- ProtonVPN detected: YES/NO
- network mode: Wi-Fi / Ethernet adapter / unknown
- last maintenance result

## 11. BIOS Manual Inspection Checklist

Human Owner must manually inspect BIOS before full-off automation can be trusted.

BIOS entry:

- Restart OMEN
- Tap Esc repeatedly
- Press F10 for BIOS setup

Look for:

- S5 Wake on LAN
- Wake on LAN
- Scheduled Power On
- RTC Wake
- BIOS Power-On
- After Power Loss
- ErP / Deep Sleep / S5 Maximum Power Savings

Record:

- Do not change settings during inspection.
- Only document what exists.
- Full-off wake remains UNKNOWN until BIOS inspection is completed.

## 12. Recommended Current Doctrine

Primary:

- Keep OMEN available using Windows / Modern Standby.
- Use Task Scheduler wake timers and guarded restart.
- Use post-push T9 backup after major work.

Secondary:

- Test Hibernate wake.

Advanced:

- Test Ethernet/WOL only after adapter, BIOS, and Windows support are verified.

Avoid:

- Smart plug power cutting.
- Full-off automation before BIOS evidence.
- VPN/network modification without approval.
- Making Fold 6 mandatory unless explicitly approved.

## 13. Unknowns / Evidence Still Needed

- Exact OMEN TG03 sub-model number.
- BIOS setting availability for S5 WOL.
- BIOS setting availability for RTC scheduled power-on.
- Whether the USB-C Ethernet adapter supports wake behavior in required power states.
- Whether ProtonVPN affects local wake/backup status checks.
- Whether Fold 6 is needed only for manual support or also for wake/status workflow.
- Whether Task Scheduler wake from Modern Standby succeeds consistently.
- Whether Hibernate wake works consistently.
- Whether T9 is always mounted as `D:\T9_FOB`.

## 14. Safe Next Milestones

Milestone 1:
Backup Officer design DRY_RUN

Milestone 2:
Maintenance Officer design DRY_RUN

Milestone 3:
Task Scheduler dry-run plan

Milestone 4:
Modern Standby wake test

Milestone 5:
Hibernate wake test

Milestone 6:
BIOS inspection result capture

Milestone 7:
Ethernet adapter WOL feasibility test

Milestone 8:
Optional Raspberry Pi wake commander evaluation

## 15. Hard Safety Rule

"No future worker may change power settings, VPN settings, network adapter settings, BIOS settings, Task Scheduler tasks, robocopy delete/mirror behavior, or restart policy based only on this document. This document is reference context. Any implementation requires a separate explicit Human Owner APPLY prompt."

## 16. Raspberry Pi / External Wake Commander Preference

Human Owner likes the Raspberry Pi / small external helper device idea if the OMEN cannot reliably wake itself.

Raspberry Pi should be treated as an optional future "external wake commander," not as the main AI_OS machine.

Possible future Raspberry Pi roles:

- send Wake-on-LAN packet to OMEN
- check whether OMEN is online
- check whether T9 backup window is due
- display or relay backup status
- help trigger scheduled wake around Human Owner sleep schedule
- act as a low-power always-on coordinator if OMEN is asleep/hibernating/off

Raspberry Pi must not:

- replace AI_OS main repo authority
- own commits
- own pushes
- store secrets unless separately approved
- run destructive backup commands
- cut power to OMEN
- bypass Human Owner approval
- become redundant with Backup Officer unless architecture requires it

Preferred doctrine:

Use Raspberry Pi only if Windows Task Scheduler / Modern Standby / Hibernate wake is unreliable, or if external wake coordination becomes operationally useful.

Treat Raspberry Pi as:

- optional support hardware
- not required dependency
- not primary backup authority
- not primary AI_OS worker

## 17. Future AI_OS Asset Classification: Infrastructure Support Node

Raspberry Pi / external helper hardware should be treated as an optional future AI_OS infrastructure support node.

Potential roles:

- Wake Commander
- Backup Observer
- Health Beacon
- Recovery Assistant
- Notification Relay
- Maintenance Window Coordinator

Authority:

- Support infrastructure only.
- Never primary AI_OS authority.
- Never repository authority.
- Never trading authority.
- Never approval authority.
- Never commit authority.
- Never push authority.
- Never broker or execution authority.

Doctrine:

The Raspberry Pi may become a useful AI_OS asset if Windows Task Scheduler, Modern Standby, Hibernate wake, or adapter-based Wake-on-LAN proves unreliable. It may help wake the OMEN, observe whether the OMEN is online, relay status, or coordinate a maintenance window around Human Owner sleep schedule.

It must not replace the OMEN as the main AI_OS machine.
It must not own the AI_OS repo.
It must not store secrets unless separately approved.
It must not run destructive backup commands.
It must not cut power to the OMEN.
It must not bypass Human Owner approval.
