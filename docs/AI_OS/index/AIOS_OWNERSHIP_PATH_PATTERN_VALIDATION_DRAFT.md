> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Ownership Path Pattern Validation Draft

## Purpose

This draft reviews ownership path patterns from Stage 47-50 and proposes validator checks for future path-pattern enforcement.

No protected root files are edited by this draft. Human approval is required before enforcing new ownership rules. This file creates no live automation.

## Approved Path Classes

- `Reports/health/` for checkpoint reports.
- `automation/status/` for DRY_RUN status validators.
- `docs/AI_OS/index/` for index and mapping drafts.
- `docs/AI_OS/audits/` for audit drafts and decision matrices.
- `docs/AI_OS/roadmap/` for roadmap drafts.
- `docs/AI_OS/validators/` for validator convention drafts.
- `docs/AI_OS/operator/` for operator guidance drafts.
- `docs/AI_OS/runbooks/` for runbook coverage and procedure drafts.
- `docs/AI_OS/governance/` for governance drafts.
- `docs/AI_OS/checkpoints/` for human checkpoint drafts.

## Blocked Path Classes

- `.git/`
- credential files
- browser profiles
- broker/API secrets
- live trading execution code
- protected root files without approval
- startup task locations
- registry, firewall, VPN, browser policy, BIOS, UEFI, BitLocker, or security settings

## Recommended Validator Checks

- Confirm every expected file is under an approved path prefix.
- Fail if any staged file is under a blocked path class.
- Fail if protected root files are staged without explicit approval.
- Fail if expected files are missing.
- Fail if any file path suggests credentials, broker secrets, browser profiles, or live trading execution.
- Print repo root, branch, git status, checks performed, PASS/FAIL summary, and stop condition.
- Exit 0 only on full PASS.

## Boundary

This document does not activate enforcement, does not approve edits to protected root files, does not grant human approval, and creates no live automation.
