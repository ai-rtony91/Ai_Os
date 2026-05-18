# Threat Model

Status: baseline scaffold, pending human review.

## Scope

AI_OS includes local automation, orchestration scripts, agent instructions, runtime packets, validation tools, documentation, dashboard code, services, and GitHub workflows.

## Primary Assets

- Source code
- Agent instructions
- Approval records
- Runtime packets
- Validation reports
- Audit logs
- Security and governance documents
- Local configuration

## Trust Boundaries

| Boundary | Risk |
|---|---|
| Human to agent | Misread or over-broad approval |
| Agent to filesystem | Unauthorized modification |
| Local repo to public GitHub | Sensitive data exposure |
| DRY_RUN to APPLY | Unsafe execution transition |
| Runtime packets to scripts | Unvalidated action execution |
| Trading simulation to broker execution | Financial/operational harm |

## Threats and Mitigations

| Threat | Impact | Mitigation |
|---|---|---|
| Secret committed | Credential exposure | secret prevention, review, scanning |
| APPLY without approval | Unsafe modification | DRY_RUN default, explicit approval gate |
| Live trading triggered | Financial harm | no-live-execution rule |
| Runtime packet drift | Unsafe or stale orchestration | validation and lifecycle rules |
| Duplicate launchers | Wrong entrypoint used | canonical path policy |
| Missing audit trail | No accountability | audit logging requirements |
| Public repo leakage | Sensitive details exposed | repo hygiene review |

## Required Controls

- DRY_RUN default
- explicit APPLY approval
- no live broker execution
- repo-scoped command validation
- CI validation
- dependency scanning
- secret prevention
- audit logging
- protected file review
