# AI_OS Agent Communication Rules

Status: Governance rule
Scope: AI_OS agent, Codex, Claude, ChatGPT, worker, and operator-facing communication

## Purpose

AI_OS communication must separate executable work from discussion and operator copy/paste blocks.

This rule reduces malformed packets, accidental bad copy/paste, relay friction, execution mistakes, noisy prompts, and mixed execution contexts across EAST, WEST, validator, and operator flows.

## Required Classification

Before responding, AI_OS agents must mentally classify each response section as one of these lanes:

- `CODEX / AGENT PROMPT`
- `CHAT EXPLANATION`
- `OPERATOR MESSAGE BOX`

If more than one lane appears in the same response, each lane must have a visible heading. The lanes must remain separated.

## CODEX / AGENT PROMPT

Use this lane for executable workload packets intended for Codex, Claude, agents, validators, or worker windows.

Executable prompts must be:

- operational
- runnable
- copy/paste clean
- bounded
- validation-aware
- low-noise

Executable prompts should include:

- mode
- objective
- allowed paths
- forbidden paths
- exact tasks
- validation steps
- stop point
- final report format

Executable prompts must not include:

- casual discussion
- architecture explanation
- brainstorming
- motivational commentary
- unrelated operator chatter

Explanations must stay outside runnable prompts.

## AI_OS Token Conservation and Prompt Delta Rule

AI_OS agents must protect operator token and credit usage.

When a prior Codex, Claude, validator, or worker prompt needs only a small correction, the agent must not reprint the full prompt. The agent must send the smallest usable correction only.

Patch-only corrections must be used for:

- branch name corrections
- worktree/path corrections
- missing AI_OS EXECUTION TOKEN
- missing CODEX-ONLY marker
- missing identity field
- missing allowed path
- missing forbidden path
- missing validator command
- typo corrections
- small rule insertions
- small safety insertions
- follow-up instructions that belong with a longer prior prompt

Patch-only corrections must include:

- `CODEX-ONLY PROMPT` when intended for Codex
- `AI_OS EXECUTION TOKEN` when executable
- the exact line to replace, add, or remove
- the phrase: `PASTE WITH LONGER PROMPT I PROVIDED PRIOR`
- a short note that all other prior instructions remain unchanged

Full prompt resend is allowed only when:

- the operator explicitly asks for the full prompt again
- more than 25 percent of the prompt changed
- the prior prompt is unavailable or unsafe to reuse
- the correction would be ambiguous without full context
- the original prompt mixed unrelated lanes and must be rebuilt cleanly

Before generating any executable prompt, the agent must check the latest visible path and branch from the user's terminal output. If path or branch is missing, the agent must either ask for git status or write a patch-only placeholder instead of guessing.

## CHAT EXPLANATION

Use this lane for normal assistant/user discussion.

This lane may include:

- architecture explanation
- brainstorming
- strategy
- comparison
- summaries
- teaching
- discussion

This lane is not executable. Do not bury terminal commands, validator commands, or workload-packet instructions inside discussion text.

## OPERATOR MESSAGE BOX

Use this lane for operator-facing copy/paste operational sections.

This lane is for:

- terminal commands
- PowerShell commands
- git commands
- validator commands
- launch commands
- safe next actions

Operator message boxes must remain:

- concise
- operational
- terminal-friendly
- low-noise
- copy/paste clean

Keep notes and explanations outside command blocks. Commands must not be buried inside discussion text.

## Mixed Response Rule

When a response needs multiple lanes:

- use visible headings
- keep executable prompts clean
- keep chat explanation outside runnable sections
- keep operator commands in concise copy/paste blocks
- do not blend commands with conversation
- do not place unrelated commentary inside workload packets

## Authority Boundary

This document governs communication structure only. It does not authorize runtime changes, router changes, validator changes, policy engine changes, trading logic, broker work, OANDA work, API-key handling, webhook work, live-order logic, dashboard work, commits, or pushes.
