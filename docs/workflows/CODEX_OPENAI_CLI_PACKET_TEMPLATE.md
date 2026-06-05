# Codex OpenAI CLI Packet Template

Status: packet template

Use this template only for instructions meant to be pasted into Codex.

Authority boundary:

- `AGENTS.md` is the authoritative source for all packet governance, routing, execution, identity, validation, and approval requirements.
- Any conflict between this template and `AGENTS.md` must be resolved in favor of `AGENTS.md`.
- Changes to packet law belong in `AGENTS.md`, not this template.

This file is a usage artifact. It helps draft packets; it does not define governance, packet law, execution requirements, identity requirements, validation requirements, or approval requirements.

Use the risk tier from `AGENTS.md` to decide how much packet structure is required. Lower-risk read-only work needs less packet structure; APPLY, promotion, production, live, secret, broker/API, commit, push, merge, and destructive actions remain strict.

```text
CODEX-ONLY PROMPT

AI_OS EXECUTION TOKEN

AI_OS BOOTSTRAP REQUIRED

identity marker: CODEX <TASK NAME>
supervisor identity: Human Owner
packet ID: <PACKET_ID>
mode: DRY_RUN
zone: <zone>
worker identity: EAST_OCC_<ID>
lane: <lane>
branch: resolve after preflight
worktree: C:\Dev\Ai.Os
approval authority: Human Owner approval required for APPLY/protected actions
validator chain: git status, staged-index check, targeted validation
stop point: terminal report only unless APPLY is explicitly approved

Allowed paths:
- <path>

Forbidden paths:
- .env
- secrets/**
- credentials/**
- broker/**
- live trading paths
- runtime state unless explicitly scoped
- any path outside allowed paths

Mission:
<Describe the operator-visible success condition and the exact work.>

Required preflight:
pwd
git status --short --branch
git diff --cached --name-status
git branch --show-current
git remote -v

Proceed only if:
- branch/worktree state matches this packet after preflight.
- staged index is empty unless this packet explicitly handles the staged files.
- dirty files are classified before mutation.
- no shared-checkout worker collision exists.

Packet-specific rules:
- Do not print, write, commit, or request secrets.
- Do not call OpenAI APIs unless explicitly approved.
- Do not start Night Supervisor unless explicitly approved.
- Do not touch live trading or broker paths.
- Do not push unless this packet explicitly authorizes push.
- Do not commit unless this packet explicitly authorizes commit and names exact files plus commit message.
- Night Supervisor output is evidence only, not authority.

Validation:
- <command>
- git diff --check
- git status --short --branch

Final report:
- Use failure format only for actual failure, block, or recovery.
- Use success format for completed APPLY tasks.
- Use DRY_RUN format for completed no-write audits.
- branch/status
- files inspected
- files created
- files updated
- validation result
- blockers
- warnings
- commit status
- push status
- next safe action

Stop condition:
Stop after validation and terminal report. Do not stage, commit, push, merge, or create reports unless explicitly authorized above.
```
