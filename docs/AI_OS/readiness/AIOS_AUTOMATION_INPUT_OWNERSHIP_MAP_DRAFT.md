# AI_OS Automation Input Ownership Map Draft

## Purpose

This draft explains which party should eventually fill or maintain AI_OS file types.

Future automated writers must have contracts and validators first.

## Ownership Categories

### Human Operator

The Human Operator owns approvals, final review, protected governance changes, checkpoint decisions, and permission to move from DRY_RUN to APPLY.

Protected root governance files require human approval.

### ChatGPT Architect

The ChatGPT Architect may draft architecture, contracts, prompts, boundary language, and review instructions for human approval.

### Codex Worker

The Codex Worker may create approved files, run validators, and perform scoped APPLY work after permission.

Codex must not make random direct edits outside the approved file list.

### Validator Scripts

Validator Scripts may inspect but not write protected files.

Validators should report PASS/WARN/FAIL and remain console-output-only unless separately approved.

### Future Report Writers

Future Report Writers may write health reports only after a separate report-writer contract and approval.

Report writers must be separately approved before writing.

### Future Telemetry Writers

Future Telemetry Writers may write production telemetry only after a separate telemetry-writer contract, validator, and approval.

Telemetry writers must be separately approved before writing.

### Future Dashboard UI

Future Dashboard UI may display approved contract fields and validator states.

Dashboard UI must not trigger execution, broker routing, webhook firing, credential access, or strategy activation without separate approval.

### Future Trading Engine

Future Trading Engine work is outside the current AI_OS readiness scope.

Trading engine logs are not approved yet.

## File Type Ownership Map

| File Type | Primary Owner | Boundary |
| --- | --- | --- |
| root governance files | Human Operator | Protected; human approval required. |
| dashboard contracts | ChatGPT Architect / Codex Worker | Drafted and validated before UI use. |
| telemetry roadmap | ChatGPT Architect / Codex Worker | Production telemetry requires separate approval. |
| Morning Brief contracts | ChatGPT Architect / Codex Worker | Display/report contract only until approved writers exist. |
| approval queue docs | ChatGPT Architect / Codex Worker | Must preserve human approval gates. |
| screener/trading contracts | ChatGPT Architect / Codex Worker | Execution remains blocked. |
| Mean Machine contracts | ChatGPT Architect / Codex Worker | Advisory/visibility-only until separate approval. |
| health reports | Future Report Writers / Codex Worker | Report writers must be separately approved before writing. |
| daily metrics | Future Report Writers | Protected from edits in current stages. |
| checkpoint index | Human Operator / Future Report Writers | Protected from edits in current stages. |
| production telemetry | Future Telemetry Writers | Not implemented; separate approval required. |
| trading execution logs | Future Trading Engine | Not approved yet. |

## Restrictions

Protected root governance files require human approval.

Validators may inspect but not write protected files.

Report writers must be separately approved before writing.

Telemetry writers must be separately approved before writing.

Trading engine logs are not approved yet.

Future automated writers must have contracts and validators first.
