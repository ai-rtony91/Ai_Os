# AI_OS Skill Registry Boundary

Purpose:
Define the boundary for a future AI_OS skill registry.

## Registry Role

The skill registry is a catalog of approved skill records. It does not execute skills, upload skills, install packages, call OpenAI, or grant runtime authority.

Each registry entry must identify:

- skill id
- workflow mapped
- version
- status
- owner
- risk class
- allowed paths
- forbidden paths
- required approvals
- required validators
- review evidence
- stop point

## Registry Status Values

- `PROPOSED`
- `REVIEWED`
- `APPROVED_LOCAL_ONLY`
- `BLOCKED`
- `RETIRED`

Hosted or network-enabled skills remain blocked until a separate human-approved governance packet defines upload, execution, security, audit, and rollback behavior.

## User Attachment Rule

End users must not freely attach arbitrary skills to AI_OS. Skill attachment must be registry-driven, reviewed, versioned, and bounded to a specific workflow.

## Protected Boundary

The registry must never authorize secret access, `.env` creation, broker/OANDA execution, live trading, Pi GPIO/motor control, Night Supervisor runtime modification, telemetry writes, control writes, approval inbox writes, commit, push, merge, rebase, or force push without separate explicit approval.
