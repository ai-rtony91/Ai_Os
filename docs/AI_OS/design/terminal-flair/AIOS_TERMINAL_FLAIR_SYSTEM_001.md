# AI_OS Terminal Flair System 001

## Purpose

Terminal flair is a readability and safety layer for AI_OS worker terminals. It helps Anthony identify which worker profile, lane type, and safety posture a terminal belongs to before reading or running commands.

This system is repo-contained preview material only. It does not edit Windows Terminal, PowerShell profiles, fonts, registry settings, startup tasks, or operating system configuration.

The parent visual language authority is `docs/AI_OS/design/AI_OS_TERMINAL_FLAIR_SPEC.md`. This file defines the worker-profile preview kit and theme registry for terminal profile identity.

## Why Worker Terminals Need Visual IDs

AI_OS can use multiple terminals for operator control, temporary OCC workers, validators, dispatch lanes, approval lanes, shell helpers, and telemetry views. Without strong visual IDs, terminals can look interchangeable, increasing the risk of:

- running a command in the wrong lane
- confusing inspection work with APPLY work
- mistaking validator evidence for approval
- losing track of commit and push boundaries
- mixing runtime, telemetry, or trading safety surfaces into general work

Visual IDs reduce that friction by making the terminal state obvious at a glance.

## Temporary OCC Workers vs Future Permanent Workers

Temporary OCC workers are packet-scoped execution identities such as `EAST_OCC_01` or `WEST_OCC_02`. Their identity is tied to one lane, one task, one worktree or branch, and one stop condition. Their flair should emphasize task scope, write boundary, and "no commit / no push unless approved."

Permanent future workers may become stable role profiles with recurring jobs, dashboards, launch scripts, or policy integrations. Their flair can remain recognizable across sessions, but it must still show current lane, authority, and stop rules. Permanent styling must not imply permanent permission.

In both cases, the visual identity is a cue, not authority. Approval, validation, branch rules, and protected paths still govern execution.

## Visual Layers

1. Base terminal theme
   - Dark gamer terminal base.
   - High-contrast text.
   - Neon accents only where they improve scanning.
   - AIOS dashboard-aligned palette:
     - base dark: `#05070b`
     - text: `#e5f6ff`
     - cyan action accent: `#38bdf8`
     - blue glow: `#00a3ff`
     - OCC/pass/activity green: `#37ff88`
     - orchestration violet/magenta: `#a855f7`
     - danger red: `#ff5f7a`
     - warning amber: `#ffd166`
   - Font guidance: Cascadia Mono or Cascadia Code first; MesloLGS Nerd Font Mono is optional only for Oh My Posh previews.

2. Worker identity badge
   - Short profile badge such as `MC`, `EAST`, or `VAL`.
   - Optional emoji badge for fast recognition.
   - Plain-text fallback must work when emoji render poorly.

3. Status strip
   - Shows profile, mode, lane type, and current safety state.
   - Must remain readable without color.

4. Lane/role banner
   - Names the worker profile and role.
   - May use CLEAN, HYPE, or BOSS mode styling.
   - Must avoid clutter that hides commands or warnings.
   - MAIN CONTROL may use ANSI background color blocks behind major headings when readable.

5. Command safety reminder
   - Shows the safe command hint.
   - Shows the forbidden action hint.
   - Always includes repo path context when used in the preview scripts.

6. Validation/result strip
   - Reserved for validation status, parse results, diff status, or blocked state.
   - Validator output is evidence only and does not approve APPLY, commit, push, or merge.

7. Optional boss-mode flair
   - Extra border weight, stronger accent labels, and a mission-HUD feel.
   - Must still fit in ordinary terminals.
   - Must not add loops, animation, sound, network calls, or automation triggers.

## Intensity Modes

`CLEAN` is compact and calm. Use it for routine work, narrow terminals, or screens where output density matters.

`HYPE` is the default operator preview mode. It adds stronger visual separation and role flavor while keeping commands easy to read.

`BOSS` is the maximum visual style. Use it when a worker terminal needs strong identity, such as a focused APPLY lane, validation bay, or main-control command deck. BOSS mode must remain readable and must not become random clutter.

## Readability Rules

- Text must be useful without color.
- Keep safety warnings plain and direct.
- Do not hide command warnings inside decorative text.
- Do not depend on Nerd Fonts, Oh My Posh, or external modules.
- Do not assume emoji render correctly.
- Use ANSI color only as enhancement.
- Use plain ASCII fallback when ANSI is unavailable.
- Keep banners short enough for normal terminal widths.
- Avoid fake metrics, fake trading status, fake broker signals, or fake live automation claims.

## Emoji Rules

Use emoji when:

- the output is a visual banner, profile list, or preview
- the emoji improves quick recognition
- the emoji identifies a deck or worker profile
- a `-NoEmoji` or plain-text fallback exists
- the emoji is not inside an executable command

Do not use emoji when:

- it repeats on every command
- it appears inside a command to be copied
- it could break title matching or automation
- the terminal renders it as broken replacement characters
- the output is safety-critical and the emoji makes it harder to read

## Persistent Decks and Temporary OCC Workers

Persistent command-deck windows may stay open all day for operator orientation. Their visual identity should remain stable:

- `MAIN CONTROL · COMMAND THRONE`
- `QUEUE CONTROL / SIGNAL ROUTER`
- `VALIDATION DECK / EVIDENCE SHIELD`
- `TELEMETRY DECK / DATA PULSE`
- `SAFETY DECK / VAULT GATE`
- `RECOVERY DECK / RESTORE BAY`
- `BUILD ENGINE / BUILDER FORGE`

Temporary OCC workers remain packet-scoped. Their banners must show the worker lane and one of these plain states when lifecycle state is displayed: `IDLE`, `COMPLETE`, `BLOCKED`, or `CLOSED`. Temporary worker flair must not imply permanent authority.

MAIN CONTROL identity stack:

- `👑 MAIN CONTROL · COMMAND THRONE`
- `🧭 ORCHESTRATOR`
- `🛡️ HUMAN-GATED`
- `📡 WORKER ROUTING`
- `⚡ NEXT SAFE ACTION`

MAIN CONTROL uses cyan, violet, blue-glow, and gold accents. Green remains reserved for safe/pass/OCC activity, amber for warning or dirty state, and red for blocked/danger.

## Transparent/Acrylic Template Guidance

Transparent or acrylic terminal appearance is allowed only as documentation or template guidance. Repo scripts must not edit Windows Terminal settings, PowerShell profiles, registry keys, fonts, startup tasks, or scheduled tasks.

Suggested Windows Terminal template-only settings for MAIN CONTROL:

```json
{
  "name": "AI_OS MAIN CONTROL",
  "tabTitle": "MAIN CONTROL · COMMAND THRONE",
  "colorScheme": "AIOS Command Throne",
  "opacity": 88,
  "useAcrylic": true,
  "acrylicOpacity": 0.84,
  "font": {
    "face": "Cascadia Mono"
  },
  "notes": "template only, not applied automatically"
}
```

## Animation Limits

Animations are not part of this preview kit. Do not add spinners, timers, loops, blinking output, sound, or repeated redraws.

Future animation experiments require separate human approval and must include stop controls, timeout behavior, and a no-persistence guarantee.

## Safety Boundaries

- No infinite loops.
- No auto-running commands.
- No installs.
- No network calls.
- No startup persistence.
- No scheduled tasks.
- No background workers.
- No Windows Terminal settings edits.
- No PowerShell profile edits.
- No registry edits.
- No font directory edits.
- No broker, trading, credential, or live execution paths.
- No profile edits without later human approval.

## Worker Profile Meanings

| Profile | Plain-English meaning |
|---|---|
| `MAIN_CONTROL` | Anthony's command throne: final direction, approval, and mission control. |
| `EAST_OCC` | East temporary builder lane: scoped Codex implementation work. |
| `WEST_OCC` | West temporary strategy lane: inspection, refinement, and bounded support. |
| `VALIDATOR` | Evidence shield: parse, test, audit, and validation result review. |
| `DISPATCHER` | Signal tower: queue routing, task movement, and lane coordination. |
| `APPROVAL` | Vault gate: human approval checkpoints and blocked-action review. |
| `SHELL` | Mechanic bay: local command help, repo inspection, and operator support. |
| `TELEMETRY` | Data pulse: runtime visibility, state review, and evidence surfaces. |

## Future Integration Rule

This kit is preview-only. A later APPLY packet may wire these banners into launch scripts, worker windows, or terminal profile generation after human approval and validation. Until then, these files are design/spec and no-write preview helpers only.

The repo-owned Oh My Posh template at `AIOS_OMP_THEME_TEMPLATE_001.json` is a template only. It is not applied automatically, does not install Oh My Posh, does not install fonts, and does not edit Windows Terminal or PowerShell profiles.
