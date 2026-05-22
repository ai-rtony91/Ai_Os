> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS_V2 authority. Current operating authority is `AGENTS.md`; current V2 front-door/context authority is `README.md`; current source-of-truth mapping lives under `docs/governance/`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved V2 canonical document explicitly promotes them.

# AIOS_CODEX_ORCHESTRATION_PLAYBOOK

## PURPOSE
Defines Codex orchestration standards, execution boundaries, and workflow sequencing for AI_OS.

## CODEX EXECUTION MODEL
- Plan first
- DRY_RUN preferred
- Human approval before APPLY
- Validate outputs before commit
- Preserve evidence and reports
- Maintain rollback capability

## STANDARD EXECUTION CHAIN
1. Repository verification
2. Branch verification
3. Clean-state verification
4. DRY_RUN planning
5. Validator execution
6. Human review
7. APPLY execution
8. Post-apply validation
9. Git commit
10. Git push
11. Final clean verification

## REQUIRED VALIDATION TYPES
- Path validation
- File existence validation
- Protected-file validation
- JSON parse validation
- Markdown/report generation validation
- Git clean-state validation

## FORBIDDEN BEHAVIORS
- Silent overwrites
- Unverified deletes
- Hidden automation activation
- Live broker execution changes
- Unauthorized startup tasks
- LLM placement in live trading path

## REPOSITORY STANDARD
Active repo:
C:\Dev\Ai.Os
