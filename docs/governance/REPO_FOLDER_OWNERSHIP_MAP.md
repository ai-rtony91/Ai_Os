# AI_OS Repo Folder Ownership Map

Status: canonical governance map
Source: `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md`

## Purpose

This map defines owner categories, allowed contents, and blocked contents for high-value AI_OS folders. It is a governance reference, not permission to automate.

## Fail-Closed Standard

- If folder ownership is unclear, do not write.
- If file placement is ambiguous, create a proposal report only.
- If a file already exists, do not overwrite it outside explicit scope.
- If protected files need edits, stop and request approval.
- If a task asks for secrets, API keys, broker execution, or order placement, block it.
- If a task asks for live code in a planning folder, block it.
- If a task asks for planning docs in an automation folder, block it.

## Ownership Table

| Folder path | Owner category | Allowed contents | Blocked contents | Risk |
| --- | --- | --- | --- | --- |
| `docs/` | Canonical documentation | Governance, workflows, concepts, architecture, specs, security, roadmap, audits | Secrets, executable live trading, unreviewed implementation | MEDIUM |
| `docs/AI_OS/` | Legacy active planning source | Historical and active AI_OS planning docs until repointed | New source-of-truth sprawl, secrets, live execution logic | MEDIUM |
| `automation/` | Automation scripts | DRY_RUN/APPLY helpers, validators, local checks | Final source policy, secrets, unapproved broker execution | HIGH |
| `Reports/` | Generated outputs | Daily reports, checkpoints, health reports, evidence outputs | Canonical policy, implementation code, secrets | MEDIUM |
| `apps/dashboard/` | Dashboard UI and mock data | Dashboard code, assets, static preview, local fixtures | Broker execution, secrets, live trading buttons, unapproved telemetry persistence | HIGH |
| `services/` | Backend services | Approved backend code | Broker/OANDA code, secrets, live execution without approval | HIGH |
| `agent/` | Agent instructions/runtime | Approved agent runtime material | Autonomous execution logic, secrets, broker execution | HIGH |
| `docs/concepts/` | Canonical concepts | Compact doctrine summaries and conceptual models | Runtime fixtures, generated reports | LOW |
| `docs/workflows/` | Canonical workflows | Operator and process workflows | Hidden automation, credential handling | MEDIUM |
| `docs/governance/` | Canonical governance | Placement, ownership, promotion, policy summaries | Protected root replacements without approval | HIGH |
| `docs/security/` | Canonical security | Security, privacy, access, credential-exclusion doctrine | Secrets, live credential configuration | HIGH |
| `docs/specs/` | Canonical specs | Data contracts, schemas, interface specs | Runtime data capture without approval | MEDIUM |
| `archive/` | Historical material | Legacy docs preserved by `git mv` | Active source-of-truth references | LOW |

## Topic Ownership

- Telemetry schemas and privacy planning: canonical summaries under `docs/concepts/` or `docs/specs/`; legacy active drafts may remain under `docs/AI_OS/telemetry/` until validators are repointed.
- Telemetry scripts: `automation/telemetry/` only after approval.
- Trading Lab review-only docs: keep separate from broker execution and live order paths.
- Broker/OANDA boundary planning: documentation only until separate approval.
- Legal/compliance/monetization: placeholders only until reviewed.
- Dashboard requirements and data contracts: canonical specs under `docs/specs/`; dashboard implementation under `apps/dashboard/`.

## Protected Root Boundary

Protected root files such as `README.md`, `AGENTS.md`, `RISK_POLICY.md`, `SOURCE_LOG.md`, `ERROR_LOG.md`, `HALLUCINATION_LOG.md`, `AAR.md`, and `DAILY_REPORT.md` require explicit approval and backup before edits.

## Cleanup Rule

Archive before delete:

1. Identify current authority.
2. Extract useful doctrine.
3. Repoint safe live wires.
4. Move legacy files with `git mv` only after scans are clear.
5. List delete candidates for later review.

