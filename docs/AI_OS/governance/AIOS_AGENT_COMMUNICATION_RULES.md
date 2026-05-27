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
