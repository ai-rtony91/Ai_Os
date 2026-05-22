+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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

The marker uses two rows of plus signs:

```text
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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
- Plain text fallback is the two plus-sign rows with no color.

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

## Terminal Tab Title Convention

Use this pattern:

```text
<emoji> <WORKER> | <MODE> | <LANE>
```

Examples:

- ðŸ§­ MAIN CONTROL | OPERATOR | DAILY
- ðŸ§© CODEX | READ ONLY | BRANCH AUDIT
- ðŸŸ£ CLAUDE | REVIEW ONLY | ARCHITECTURE
- ðŸ›‘ SAFETY GATE | BLOCKED | BRANCH DELETE
- ðŸ§¹ CLEANUP | REVIEW FIRST | TEMP FILES
- ðŸ“‹ POWERSHELL ACTION | APPLY | APPROVED COMMAND

Plain text fallbacks:

- MAIN CONTROL | OPERATOR | DAILY
- CODEX | READ ONLY | BRANCH AUDIT
- CLAUDE | REVIEW ONLY | ARCHITECTURE
- SAFETY GATE | BLOCKED | BRANCH DELETE
- CLEANUP | REVIEW FIRST | TEMP FILES
- POWERSHELL ACTION | APPLY | APPROVED COMMAND

Emoji code point reference for tab titles:

| Emoji | Code point | Label | Plain fallback |
|---|---:|---|---|
| ðŸ§­ | U+1F9ED | MAIN CONTROL / DECISION | MAIN CONTROL |
| ðŸ§© | U+1F9E9 | CODEX / CODEX PROMPT | CODEX |
| ðŸŸ£ | U+1F7E3 | CLAUDE | CLAUDE |
| ðŸ›‘ | U+1F6D1 | SAFETY GATE / STOP | SAFETY GATE |
| ðŸ”Ž | U+1F50E | INSPECT | INSPECT |
| ðŸ§¹ | U+1F9F9 | CLEANUP | CLEANUP |
| ðŸ“ | U+1F4DD | RECORDKEEPING | RECORDKEEPING |
| âœ… | U+2705 | CLEAN / SUCCESS | CLEAN |
| âš ï¸ | U+26A0 U+FE0F | REVIEW FIRST | REVIEW FIRST |
| ðŸ“‹ | U+1F4CB | PASTE INTO POWERSHELL | PASTE INTO POWERSHELL |
| âš¡ | U+26A1 | POWERSHELL ACTION | POWERSHELL ACTION |

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

## Compact HUD Layout

Use compact HUDs in docs, chat examples, or narrow terminals.

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

Do not implement terminal rendering, tab color changes, launcher edits, runtime behavior, or worker banner output from this document without a separate approved APPLY task.



