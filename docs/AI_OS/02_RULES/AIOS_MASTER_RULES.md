# AIOS Master Rules

## Purpose

This file defines the operating rules for AI_OS work.

## Core Rules

1. Do not move, delete, rename, or overwrite files without an approval file.
2. Inventory comes before action.
3. Classification comes before merge.
4. Backups come before deletion.
5. GitHub is source control, not a trash bin.
6. OneDrive is for ARCHIVES, EXPORTS, SNAPSHOTS, and DISASTER BACKUPS only.
   Canonical docs belong in C:\Dev\Ai.Os\docs\.
   Operational scripts belong in C:\Dev\Ai.Os\automation\ or D:\AIOS_TERMINAL\scripts\.
   OneDrive must NOT contain live operational scripts, active launchers, or canonical docs.
   Updated: 2026-05-22 — New compartment doctrine (supersedes original Rule 6).
7. Full system images do not belong in OneDrive.
8. Scripts must be beginner-safe and explain their purpose.
9. Every generated script must state whether it edits, moves, deletes, or only reports.
10. If a script fails, stop and inspect the error before creating another script.

## AI Tool Roles

ChatGPT = architect, systems engineer, documentation lead.
Codex = code implementation and repository work.
Claude = codebase reviewer, refactor assistant, secondary engineer.
GitHub = version-controlled project source.
VS Code = editing cockpit.
Windows/OMEN = local workstation.
WSL2 Ubuntu = preferred serious development environment later.
Azure = controlled cloud infrastructure later.

## Locked Safety Rule

No destructive script runs without an approval file in:

C:\Users\mylab\OneDrive\AI-OS-Project\docs\AI_OS\06_APPROVALS

