+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# AI_OS Terminal Flair and Visual Language Spec

## Purpose

Terminal flair is not decoration only.

It exists to help the operator instantly identify:

- lane
- worker
- worktree
- branch
- repo
- mode
- task
- stop rule
- safety state

The visual language applies to:

- ChatGPT orchestrator guidance
- Codex prompts
- Claude review prompts
- operator runbooks
- PowerShell command blocks
- terminal/window flair
- worker HUDs
- future banner designs

## Core Rule

Every AI_OS terminal HUD or worker banner must show at minimum:

- LANE - current work lane
- WORKER - Codex / Claude / ChatGPT / Operator
- WORKTREE - local path
- BRANCH - current branch -> tracking remote
- REPO - remote authority
- MODE - READ ONLY / DRY RUN / APPLY
- TASK - active task description
- STOP - stop condition for this session

HUD first. Mascot second.

The design must improve safety clarity, not obscure it.

## Start Marker Rule

Major operator-facing text blocks should begin with a start marker.

The marker uses one row of plus signs across the block:

```text
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
```

Meaning:
- start of official AI_OS text block
- start of Codex prompt
- start of operator assignment
- start of terminal HUD / flair block
- start of important governance text

Marker color guidance:
- Use either the active theme accent or the shared Dark Tan / Bronze marker color when color is available.
- Shared marker color: Dark Tan / Bronze #B08A57.
- The marker color is a visual boundary cue, not a fifth active UI color.
- Plain text fallback is the one plus-sign row with no color.

Rules:
- The marker must appear at the very beginning of the block.
- The marker must not contain commands.
- The marker must not replace the title.
- The marker should be short and consistent.
- Do not overuse it inside the same document.
- Use it once at the start of a major block, not before every paragraph.
- Use it sparingly only at major block starts.

Example:

```text
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘  CODEX PROMPT  â—†  TERMINAL FLAIR RULE                    â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

## Operator Signal Vocabulary

Emoji signals go above command blocks.

Emoji signals must not be placed inside executable commands unless explicitly required.

Use these operator signals:

- ðŸ“‹ PASTE INTO POWERSHELL
- âœ… SUCCESS / CLEAN
- âš ï¸ REVIEW FIRST
- ðŸ›‘ STOP / BLOCKED / DESTRUCTIVE
- ðŸ”Ž INSPECT ONLY
- ðŸ§¹ CLEANUP
- ðŸ§­ DECISION
- ðŸ§© CODEX PROMPT
- ðŸ“ RECORDKEEPING
- [-_-] STOP POINT

Plain text fallback labels must exist for environments that render emoji as ??.

## PowerShell Command Block Rule

Commands intended for PowerShell must be clearly labeled:

ðŸ“‹ PASTE INTO POWERSHELL

Commands must be inside fenced code blocks.

Plain notes, explanations, status examples, and success descriptions must stay outside command blocks.

Do not make notes look like commands.

## Unicode-Safe Emoji Title Rule

Terminal tab titles may use emoji labels, but implementation must not depend on fragile raw emoji text.

Rules:
- Store or generate emoji labels using Unicode-safe code point handling when used in scripts, launchers, tab titles, or terminal profiles.
- Provide plain-text fallback titles for every emoji title.
- If an emoji renders as ??, falls back incorrectly, or breaks terminal title encoding, use the plain-text fallback.
- Do not place emoji inside executable commands unless explicitly required.
- Emoji in docs may remain visible as examples, but implementation should prefer code point mappings.

Example code point map:
- Crown / MAIN CONTROL: U+1F451
- Robot / CODEX: U+1F916
- Brain / CLAUDE: U+1F9E0
- Red Circle / SAFETY GATE: U+1F534
- Blue Circle / POWERSHELL ACTION: U+1F535
- Green Circle / CLEAN: U+1F7E2
- Yellow Circle / REVIEW: U+1F7E1
- Broom / CLEANUP: U+1F9F9
- Receipt / RECORDKEEPING: U+1F9FE
- Eyes / INSPECT: U+1F440
- Pushpin / STOP POINT: U+1F4CC

## AI_OS Role Marker and Worker Window Title Standard

Role markers, terminal titles, worker HUD labels, dashboard labels, and control-screen labels must use the same AI_OS role language.

The role marker is an identity cue only. It does not grant authority, approve work, bypass safety gates, or change the worker's assigned lane.

### Canonical Role Markers

Use these role markers whenever an AI_OS worker, control surface, terminal window, dashboard panel, or handoff packet identifies an actor:

| Actor | Canonical marker | Plain role | Authority |
|---|---|---|---|
| Operator | Operator - Commander | Commander / final authority | Final approval authority |
| ChatGPT | ChatGPT - Orchestrator | Orchestrator / squad lead | Task shaping and coordination |
| Claude | Claude - Inspector | Inspector / reviewer | Review, critique, instruction, risk inspection |
| Codex | Codex - Engineer | Engineer / builder | Scoped repo implementation when assigned |

Rules:
- Use the canonical marker in documentation, dashboard labels, worker banners, and structured handoff packets.
- Use the plain role when title width is limited.
- Do not invent new primary role names for these actors without updating this standard.
- Do not use a role marker to imply permission to stage, commit, push, merge, delete, move, rename, run automation, or bypass protected main.
- If a worker changes purpose inside a lane, update the purpose portion of the title, not the actor role.

### Window Title Pattern

Use this title pattern for terminal windows, tabs, worker HUDs, and control-screen headings:

```text
<ACTOR> - <ROLE OR PURPOSE>
```

For task-specific Codex windows, keep `CODEX` as the actor and put the lane purpose after the separator.

Canonical examples:

- AI_OS MAIN CONTROL
- CHATGPT - ORCHESTRATOR
- CLAUDE - INSPECTOR
- CODEX - ENGINEER
- CODEX - PR Lane Runner
- CODEX - Commit Gate
- CODEX - Handoff Exporter

Unicode display variants may use an em dash when rendering is reliable:

- CHATGPT — ORCHESTRATOR
- CLAUDE — INSPECTOR
- CODEX — ENGINEER
- CODEX — PR Lane Runner
- CODEX — Commit Gate
- CODEX — Handoff Exporter

Plain text fallback titles must always be valid. If the em dash, emoji, or other Unicode marker renders incorrectly, use the ASCII hyphen version.

### Dashboard and Control-Screen Labels

Dashboard panels and control screens should use the same role terms:

- `AI_OS MAIN CONTROL` for the operator-owned control lane.
- `CHATGPT - ORCHESTRATOR` for orchestration, prompt shaping, and next-step guidance.
- `CLAUDE - INSPECTOR` for review, critique, and quality-control lanes.
- `CODEX - ENGINEER` for implementation lanes.
- `CODEX - <lane purpose>` for scoped Codex tooling lanes such as PR Lane Runner, Commit Gate, or Handoff Exporter.

Labels must remain readable without color, emoji, or font-specific glyphs.

## Terminal Tab Title Convention

Working terminal titles should identify the role and purpose of the window.

Rules:
- Use `AI_OS MAIN CONTROL` for the operator-owned main control window.
- For worker windows, use the actor and role or lane purpose without repeating the repo path.
- Use role, mode, and lane or purpose instead.
- Keep repo path details in HUD fields such as `WORKTREE` or `REPO`, not in the window title.
- Automation and window matching should use stable plain-text role tokens, not emoji.
- Emoji is optional display flair and must have a plain-text fallback.

Use this pattern:

```text
<ROLE> | <MODE> | <LANE>
```

Examples:

- AI_OS MAIN CONTROL
- CHATGPT - ORCHESTRATOR
- CLAUDE - INSPECTOR
- CODEX - ENGINEER
- CODEX - PR Lane Runner
- CODEX - Commit Gate
- CODEX - Handoff Exporter

Expanded HUD/title examples:

- MAIN CONTROL | OPERATOR | DAILY
- CODEX | READ ONLY | BRANCH AUDIT
- CLAUDE | REVIEW ONLY | ARCHITECTURE
- SAFETY GATE | BLOCKED | BRANCH DELETE
- CLEANUP | REVIEW FIRST | TEMP FILES
- POWERSHELL ACTION | APPLY | APPROVED COMMAND

Emoji code point reference for tab titles:

| Emoji | Code point | Label | Plain fallback |
|---|---:|---|---|
| 👑 | U+1F451 | MAIN CONTROL | MAIN CONTROL |
| 🤖 | U+1F916 | CODEX | CODEX |
| 🧠 | U+1F9E0 | CLAUDE | CLAUDE |
| 🔴 | U+1F534 | SAFETY GATE / STOP | SAFETY GATE |
| 🔵 | U+1F535 | POWERSHELL ACTION | POWERSHELL ACTION |
| 🟢 | U+1F7E2 | CLEAN / SUCCESS | CLEAN |
| 🟡 | U+1F7E1 | REVIEW FIRST | REVIEW FIRST |
| 🧹 | U+1F9F9 | CLEANUP | CLEANUP |
| 🧾 | U+1F9FE | RECORDKEEPING | RECORDKEEPING |
| 👀 | U+1F440 | INSPECT | INSPECT |
| 📌 | U+1F4CC | STOP POINT | STOP POINT |

## Terminal Tab Color Convention

Tab colors must match the active HUD theme accent.

Tab color communicates safety state first, worker identity second.

Suggested mapping:

| State or worker | Tab color name | Hex |
|---|---|---:|
| MAIN CONTROL | Electric Blue | #4DA3FF |
| CODEX | Matrix Green | #39FF88 |
| CLAUDE | Ember Orange | #FF9A3D |
| CLAUDE alternate | Soft Violet | #B58CFF |
| SAFETY GATE | Signal Red | #FF4D4D |
| CLEANUP | Amber | #FFB84D |
| RECORDKEEPING | Steel White / Slate | #E6EDF3 |
| BLOCKED | Signal Red | #FF4D4D |
| REVIEW FIRST | Amber | #FFB84D |
| SUCCESS / CLEAN | Matrix Green | #39FF88 |
| START MARKER | Theme accent or Dark Tan / Bronze | #B08A57 |

If a destructive command is being discussed, use Safety Gate / Signal Red even if the worker is Codex.

## Four-Color Theme Rule

Each terminal theme uses four colors total:

1. Midnight base - background / frame
2. Secondary dark tone - panels / inactive areas
3. Readable text tone - labels and values
4. Accent color - worker identity, safety state, active lane

Avoid rainbow output.
Avoid excessive color noise.
Every color must have a job.

The start marker may use the active theme accent or the shared Dark Tan / Bronze marker color #B08A57. This marker color is a boundary cue only and does not count as a fifth active UI color.

The four theme colors still stay clean. The Dark Tan / Bronze marker is like tape on the floor: it marks the boundary of an important block, but it is not part of the active theme palette.

Bezel panels use the existing palette. They do not introduce a new theme color.
Use contrast, spacing, and placement to create screen depth instead of adding extra colors.

## Semantic Color Routing Rule

Every operator-facing AI_OS block must declare or infer its semantic state before choosing a color.

Color is state routing, not decoration.

A section's border, header, and background plate should communicate the highest attention state inside that section.

### Semantic States

#### NEUTRAL / NOTE / EXPLANATION

Purpose:

- normal explanation
- context
- summary
- stable values
- what this means

Foreground:

- white / gray

Background plate:

- charcoal / dark gray

Rules:

- must not look like a command
- must not steal attention from warnings or success
- use for plain notes and explanations

#### ACTION / INSPECT / COMMAND

Purpose:

- pasteable commands
- Codex prompts
- read-only inspection
- discovery
- operator action blocks

Foreground:

- blue / cyan

Background plate:

- dark navy / charcoal blue

Rules:

- should be obvious as actionable
- not the same as success
- examples: PASTE INTO POWERSHELL, CODEX PROMPT, INSPECT ONLY

#### SUCCESS / CLEAN / GOOD

Purpose:

- clean repo
- synced
- pass
- none
- done
- safe
- approved

Foreground:

- lime green / forest green / foliage

Background plate:

- dark forest green

Rules:

- use only for confirmed good states
- do not use green for a panel if unresolved amber or red state exists inside it

#### REVIEW / CAUTION / PENDING

Purpose:

- pending
- dirty
- stale
- uncertain
- partial success
- needs review
- needs decision

Foreground:

- amber / yellow

Background plate:

- dark bronze / dark amber

Rules:

- use when operator attention is needed
- not dangerous enough for red
- beats green in mixed-state panels

#### STOP / BLOCKED / DESTRUCTIVE / FAIL

Purpose:

- destructive actions
- blocked state
- failed validation
- merge conflict
- approval gates
- do not proceed

Foreground:

- red

Background plate:

- dark maroon / dark red

Rules:

- highest priority
- must be visually dominant
- commands must not be hidden inside the same block as inspection
- destructive actions require explicit approval flow

### Highest-Attention Panel State Priority

When a panel or section contains mixed states, route the panel border/header/background to the highest attention state present:

```text
RED > AMBER > GREEN > BLUE > NEUTRAL
```

Examples:

- Inbox has NONE, SYNCED, and 2 PENDING -> panel state is AMBER.
- Repo has CLEAN and SYNCED only -> panel state is GREEN.
- Any destructive/delete/blocked action -> panel state is RED.
- A command/paste section with no risk -> panel state is BLUE.
- A plain explanation -> panel state is NEUTRAL.

## Complementary Dark Background Plate Rule

Semantic panels should use a subtle complementary dark background when the terminal supports it.

Background color is not the same as the status accent. It is a darker supporting plate behind the text.

Recommended background mapping:

- ACTION / INSPECT / COMMAND: dark navy / charcoal blue plate
- SUCCESS / CLEAN / GOOD: dark forest plate
- REVIEW / CAUTION / PENDING: dark bronze / dark amber plate
- STOP / BLOCKED / DESTRUCTIVE: dark maroon / dark red plate
- NEUTRAL / NOTE: charcoal / dark gray plate

Rules:

- foreground text must remain readable
- do not use bright full-panel backgrounds
- do not let background color bleed into the prompt line
- if PowerShell background colors make spacing ugly, prefer foreground-only borders and document the limitation
- background fill is allowed for status plates and section headers, not every paragraph
- panel border still routes to the highest attention state
- panel background should support the state without overpowering the text
- background color must not be used as the only signal; labels and state words must remain explicit

## Main Control HUD Semantic Mapping

Rules:

- title/header: blue/white identity
- repo panel: green when clean/synced
- repo panel: amber when dirty/ahead/behind
- inbox panel: green only when all rows are clear
- inbox panel: amber when open PRs or feature lanes are pending
- future blocked/destructive panel: red
- labels: cyan
- normal values: white/gray
- individual status words: semantic colors

Panel examples:

- Repo panel with CLEAN + SYNCED -> green border/header/background plate
- Repo panel with DIRTY or AHEAD/BEHIND -> amber border/header/background plate
- Inbox panel with NONE + SYNCED + no pending lanes -> green panel
- Inbox panel with 2 PENDING -> amber panel

Important prohibition:

A green panel must not contain unresolved amber or red state. If any row inside a panel is pending, dirty, stale, or needs review, the panel escalates to amber. If any row is blocked, destructive, or failed, the panel escalates to red.

## Assistant and Codex Prompt Semantic Mapping

Rules:

- PASTE INTO POWERSHELL: blue/cyan action panel
- CODEX PROMPT: blue/cyan action panel
- INSPECT ONLY: blue/cyan action panel
- SUCCESS LOOKS LIKE: green success panel
- REVIEW FIRST / PENDING / DECISION / CAUTION: amber review panel
- STOP / BLOCKED / DESTRUCTIVE: red safety panel
- notes, explanations, and summaries: neutral white/gray text
- do not wrap every paragraph in the same color
- separate semantic sections should have separate visual identity
- command blocks must stay visually distinct from notes
- notes must not look like commands

## Semantic Color Routing Rollout

Recommended rollout:

1. Docs authority first: define semantic color and background plate rules.
2. Local Main Control HUD second: apply panel-state routing and optional background plate toggle.
3. Tracked launcher/template third: promote the proven local behavior into repo-owned source.

For the local HUD phase:

- add a red palette variable
- compute repo panel state
- compute inbox panel state
- route panel border/header/background by highest attention state
- add a toggle such as `$UsePanelBackground = $true`
- if background fill makes PowerShell output ugly, turn it off and keep semantic borders/headers

## Bezel Panel Rule

A bezel is an inner frame or rim around an important information area, like the frame around a monitor, instrument cluster, phone screen, cockpit display, or watch face.

In AI_OS terminal HUDs, a bezel panel is used to make important text feel intentionally mounted inside the dashboard instead of floating loosely in the terminal.

The bezel creates:

- visual boundary
- readable grouping
- depth
- separation from the outer frame
- operator focus
- command-center feel

The bezel must support safety clarity. It must never become messy decoration.

### HUD Layering Model

AI_OS terminal HUDs should use a layered screen model:

1. Terminal background - plain black or midnight base; lowest visual layer.
2. Outer frame - main dashboard shell; defines the full HUD boundary.
3. Bezel frame - inner rim around important information; separates status content from the outer frame.
4. Status plate - darker or contrasting text background area; holds high-value readable fields.
5. Accent/state text - clean, synced, warning, blocked, or destructive labels; colored only where status meaning matters.
6. Mascot/character - optional; never more important than status text.

### When To Use A Bezel Panel

Use bezel panels around grouped high-value information:

- repo path
- worktree
- branch
- sync status
- remote
- lane
- worker
- mode
- stop rule
- safety state
- inbox summary
- open PR count
- pending feature lanes
- approval gate status
- validator status

Do not use bezel panels around every paragraph.

### When Not To Use A Bezel Panel

Do not add a bezel panel when:

- the terminal is too narrow
- the panel causes wrapping
- the panel hides critical text
- the panel makes output harder to copy
- the output is a simple command result
- the content is a long log
- the section is temporary/debug output
- the decoration distracts from safety status

### Bezel Color Guidance

Use the existing four-color theme rule.

Recommended mapping:

- Terminal background: Midnight base
- Outer frame: Midnight base or secondary dark tone
- Bezel border: Accent color or soft steel/cyan edge
- Status plate background: Secondary dark tone
- Main text: Readable text tone
- State accents:
  - clean/synced: green
  - review/pending: amber
  - blocked/destructive: red
  - inspect/read-only: blue/cyan

The bezel should contrast enough to be visible, but not glow so hard that it steals focus.

### Bezel Shape Guidance

Preferred:

- one clean rectangular inner frame
- short labels aligned left
- values aligned after labels
- status words spaced with readable separators

Avoid:

- too many nested boxes
- broken borders
- wide ASCII art that wraps
- emoji inside border math
- long dynamic strings that push the right edge out

### Text Plate Layout

Preferred text plate style:

```text
PATH    C:\Dev\Ai.Os
BRANCH  main  >>  CLEAN  >>  SYNCED
REMOTE  ai-rtony91/Ai_Os
```

Rules:

- labels should be short and uppercase
- values should be readable
- status words should be visually distinct
- the plate should still make sense with no color
- do not rely on color alone for meaning

### Bezel Safety Rule

Safety state wins over aesthetics.

If a bezel panel makes a STOP, BLOCKED, DESTRUCTIVE, or REVIEW state harder to see, simplify the panel.

For destructive actions:

- use Safety Gate theme
- use red accent
- keep approval requirement plain text
- do not hide destructive state inside art

### Responsive Layout Rule

Use different layout levels depending on terminal width:

- Level 1 - narrow: no inner bezel; plain labeled rows only.
- Level 2 - normal: one bezel around the primary status plate.
- Level 3 - wide: two-panel HUD allowed; left status plate and right mascot/state plate.

If wrapping occurs, downgrade one level.

### Compact Bezel Example

```text
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ MAIN CONTROL | OPERATOR ------------------------------++
|                                                        |
|  +-- STATUS PLATE ----------------------------------+  |
|  | PATH    C:\Dev\Ai.Os                            |  |
|  | BRANCH  main  >>  CLEAN  >>  SYNCED             |  |
|  | REMOTE  ai-rtony91/Ai_Os                        |  |
|  | STOP    report only                             |  |
|  +--------------------------------------------------+  |
|                                                        |
+--------------------------------------------------------++
```

### Wide Two-Panel Bezel Example

```text
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ TERMINAL FLAIR GOVERNANCE ----------------------------++
|                                                        |
|  +-- STATUS PLATE ----------------+  +-- STATE ------+ |
|  | LANE    Terminal Flair Gov     |  | [o_o]        | |
|  | WORKER  CODEX                  |  | reading      | |
|  | MODE    APPLY - docs only      |  | no runtime   | |
|  | STOP    report only            |  | no push      | |
|  +--------------------------------+  +--------------+ |
|                                                        |
+--------------------------------------------------------++
```

### Safety Bezel Example

```text
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+ SAFETY GATE | BLOCKED --------------------------------++
|                                                        |
|  +-- REQUIRED STOP ---------------------------------+  |
|  | STATE   BLOCKED / DESTRUCTIVE                   |  |
|  | ACTION  branch deletion                         |  |
|  | NEEDS   explicit human approval                 |  |
|  | NEXT    inspect >> report >> decide >> approve  |  |
|  +--------------------------------------------------+  |
|                                                        |
+--------------------------------------------------------++
```

## Midnight Themes

### Theme A - Midnight Indigo / Steel

Use for MAIN CONTROL / Orchestrator.

- Base: Midnight Indigo #101626
- Panel: Deep Slate #1C2638
- Text: Steel White #E6EDF3
- Accent: Electric Blue #4DA3FF

### Theme B - Midnight Green / Matrix

Use for Codex / read-only repo inspection.

- Base: Black Midnight #050A08
- Panel: Deep Forest #0E1A13
- Text: Soft Mint #D8FFE3
- Accent: Matrix Green #39FF88

### Theme C - Midnight Violet / Ember

Use for Claude / review / architecture.

- Base: Deep Midnight #0D0B1F
- Panel: Royal Shadow #1A1233
- Text: Pale Lavender #ECE7FF
- Accent: Ember Orange #FF9A3D

### Theme D - Midnight Red / Safety

Use for blocked, destructive, or approval-required actions.

- Base: Charcoal Midnight #120A0A
- Panel: Deep Maroon #271111
- Text: Warm White #FFF1E8
- Accent: Signal Red #FF4D4D

## Pixel Worker Mascot States

Mascot is optional but allowed.

States:

- [o_o] reading / inspecting
- [^_^] clean / success
- [!_!] caution / blocked
- [-_-] done / stopped
- [x_x] error

Rules:

- HUD first, mascot second.
- Mascot must not make status harder to read.
- If the mascot causes wrapping, remove or simplify it.
- Mascot must never hide commands or imply approval.
- If emoji causes encoding problems, use ASCII mascot states only.
- Mascot may sit inside its own small bezel in wide layouts.
- Mascot panel should include state text such as reading, blocked, done, or error.
- Mascot must not compete with safety state.

## Compact HUD Layout

Use compact HUDs in docs, chat examples, or narrow terminals.

Use bezel panels for grouped status text only when terminal width supports it.
If the box wraps, remove the inner bezel before removing critical status fields.
Do not place emoji where it affects border alignment.
Prefer ASCII mascot states like [o_o] inside narrow fixed-width panels.

Example:

```text
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ ðŸ›‘ SAFETY GATE                 SIGNAL RED â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ Repo   C:\Dev\Ai.Os                       â•‘
â•‘ Branch main -> origin/main                â•‘
â•‘ Mode   destructive check                  â•‘
â•‘ Lane   branch deletion                    â•‘
â•‘ Stop   human approval                     â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ [!_!] BLOCKED                             â•‘
â•‘ /| |\ approval only                       â•‘
â•‘ / \   inspect -> report -> decide         â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

## Wide HUD Layout

Use wide HUDs only in real terminal windows with enough width.

Wide layouts may use two panels: a left status plate and a right mascot/state plate.
Use bezel panels for grouped status text only when terminal width supports it.
If the box wraps, remove the inner bezel before removing critical status fields.
Do not place emoji where it affects border alignment.
Prefer ASCII mascot states like [o_o] inside fixed-width panels.

Example:

```text
â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
â•‘ ðŸ›‘ SAFETY GATE                                                  SIGNAL RED  â•‘
â• â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•¦â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•£
â•‘ Repo   C:\Dev\Ai.Os         â•‘                    [!_!]                     â•‘
â•‘ Branch main -> origin/main  â•‘                   /|___|\      BLOCKED        â•‘
â•‘ Mode   DESTRUCTIVE CHECK    â•‘                   /     \      approval only  â•‘
â•‘ Lane   Branch Deletion      â•‘                                               â•‘
â•‘ Stop   Human approval       â•‘       inspect -> report -> decide -> approve  â•‘
â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•©â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
```

## Destructive Command Visual Safety

Destructive commands are armed/destructive and must never be mixed into inspection flows.

Examples:

- git push origin --delete <branch>
- gh pr merge <number> --delete-branch

Required sequence:

1. inspect
2. report
3. decide
4. explicit human approval
5. deletion command in a standalone separate step

Safety Gate theme must be used when discussing destructive actions.

## Implementation Boundary

This spec is design guidance only.

Terminal title implementation must be done in a separate approved APPLY task. This spec only defines the naming, fallback, and Unicode-safety rules.

Do not implement terminal rendering, tab color changes, launcher edits, runtime behavior, or worker banner output from this document without a separate approved APPLY task.



