# AI_OS Command Center Interface Plan

## Purpose

The AI_OS Command Center is the centralized operator surface for worker visibility, queue supervision, approval readiness, merge readiness, blocked conflict visibility, stale worker monitoring, and next safe actions.

This is orchestration visibility only.

## Placement

The Command Center is integrated into the existing DevOps / Orchestrator dashboard surface. It must not become a separate mega-dashboard or floating panel.

## Required Sections

- Global Status Strip
- Active Worker Grid
- Merge Readiness Queue
- Conflict Center
- Approval Inbox
- Operator Guidance Panel
- Safety Banner

## Display Rules

- Beginner-readable first.
- Advanced details collapsed by default.
- Minimal clutter.
- Compact worker cards.
- Mobile readable.
- Next Safe Action remains visible.
- No duplicate panels or repeated status sections.

## Safety Banner

Always show:

- LIVE EXECUTION BLOCKED
- PAPER / LOCAL DEVELOPMENT ONLY

## Approval Flow

The Command Center displays approval state only. It does not approve work.

Forbidden controls:

- merge buttons
- commit buttons
- push buttons
- autonomous execution buttons
- live agent execution buttons

## Blocked Scope

The Command Center must not touch broker, OANDA, API key, protected root, live trading, startup task, background daemon, merge execution, auto-commit, or auto-push logic.

## Validation

Use:

```powershell
node --check apps/dashboard/js/aios-static-preview.js
git diff --check
git status --short --branch
```
