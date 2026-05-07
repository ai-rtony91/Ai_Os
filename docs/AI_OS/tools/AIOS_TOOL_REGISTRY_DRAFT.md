# AI_OS Tool Registry Draft

## Purpose

This draft defines the future AI_OS Tool Registry for approved generated work packets. The registry is planning-only and does not connect real tools, APIs, credentials, background services, persistence, broker systems, or live order paths.

## Tool Registry Role

The Tool Registry describes which tools may assist the operator, what each tool may output, what each tool must not do, and which approvals are required before any APPLY work can happen.

The registry supports the Work Table by making tool use visible before a project packet is approved.

## Registry Fields

- `tool_name`: Human-readable tool name.
- `tool_purpose`: Why the tool exists in AI_OS.
- `allowed_use`: Safe uses in DRY_RUN or approved APPLY modes.
- `blocked_use`: Actions the tool must not perform.
- `credential_boundary`: Credential and private data restrictions.
- `approval_required`: Human approval requirements.
- `input_allowed`: Inputs the tool may inspect or receive.
- `output_allowed`: Outputs the tool may create or propose.
- `validation_required`: Checks required before commit or promotion.
- `notes`: Additional safety or workflow context.

## Initial Tools

### ChatGPT

Purpose: planning, explanation, workflow design, operator help, and draft work packets.

Allowed use: produce DRY_RUN plans, architecture notes, validation plans, and beginner-readable instructions.

Blocked use: no direct execution, no credential access, no backend/API connection from the dashboard, no live order path, no order approval, and no trading automation.

### Codex

Purpose: approved code and file implementation inside the active repo.

Allowed use: inspect files, apply approved patches, run validators, stage/commit/push only after explicit approval.

Blocked use: no protected root edits without approval, no deletes/moves/renames, no credentials, no broker/trading automation, no live order path, and no unapproved persistence.

### Claude

Purpose: optional review/planning lane for future multi-assistant workflows.

Allowed use: review summaries, alternative planning, documentation critique, and non-executing design feedback.

Blocked use: no autonomous execution, no credential access, no broker/trading activity, and no protected file edits.

### GitHub

Purpose: source control, commits, pushes, PRs, and repository publishing review.

Allowed use: git status, scoped staging, approved commits, approved pushes, and future approved PR workflows.

Blocked use: no force push, no destructive reset, no secret exposure, no unauthorized workflow activation, and no unapproved deployment secrets.

### PowerShell

Purpose: local validation, file existence checks, static scans, git status, and controlled operator commands.

Allowed use: DRY_RUN validators, safe read-only inspection, approved static file creation, and approved git commands.

Blocked use: no registry/security/system setting changes, no startup tasks, no credential access, no destructive file operations, and no trading execution.

### Web/Research

Purpose: source research and documentation lookup.

Allowed use: public documentation research, citation gathering, and current best-practice review.

Blocked use: no private account scraping, no credential capture, no broker account access, no private browser profile access, and no trading action.

### Files/OneDrive

Purpose: approved local file inspection within allowed project paths.

Allowed use: inspect active repo files and approved archive notes when explicitly requested.

Blocked use: no private user data access, no browser profiles, no credential stores, no delete/move/rename, and no wrong-remote workspace use.

### Reports

Purpose: display or plan report outputs.

Allowed use: read approved reports, show checkpoint state, and propose report packets.

Blocked use: no active report writer, no hidden report mutation, no protected root edits, and no persistence activation.

### Telemetry

Purpose: future fixture-only health/event visibility.

Allowed use: display planned telemetry schemas and static mock telemetry fixtures.

Blocked use: no active telemetry writer, no production telemetry, no persistence, no private data, no broker data, and no live market execution data.

## Safety Boundary

This registry is static/planning only. It grants no approval to activate tools, connect APIs, store data, register service workers, create startup tasks, touch credentials, or touch broker/trading automation.
