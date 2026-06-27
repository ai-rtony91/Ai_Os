# AIOS AEE Governance Validator V1

## Purpose

Provide a deterministic local validator for AEE long-campaign governance doctrine, workflow, and checkpoint artifacts.

It checks required artifacts, required markdown structure, required safety boundaries, cross-links, protected handoff behavior, and checkpoint/report integrity.

## Scope

This validator covers:

- AEE doctrine artifacts.
- AEE workflow artifacts.
- AEE checkpoint and report artifacts.
- Deterministic validator code in `automation/governance/`.
- Deterministic CLI behavior in `scripts/governance/`.
- Fixture coverage and test fixtures under `tests/fixtures/governance/aee_validator/`.
- Validation reports and checkpoint handoff evidence.

This artifact does not authorize broker/API access.  
This artifact does not authorize credential access.  
This artifact does not authorize trading execution.  
This artifact does not authorize money movement.  
This artifact does not authorize commit/push/merge without explicit Human Owner approval.

## Validator Contract

The validator contract is deterministic, local-only, no-network, no-broker, no-credential access, no environment-variable reads, and no subprocess requirement in core checks.

- Input is file content from repository paths.
- Output is one of `PASS`, `PARTIAL`, or `FAIL`.
- Output includes findings with deterministic codes.
- Output supports plain text, JSON, and markdown report rendering.

### Result statuses

- `PASS` - all validations pass.
- `PARTIAL` - only warning-level findings exist.
- `FAIL` - one or more fail findings exist.

## Artifact List

The validator checks these paths by default:

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md`
- `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md`
- `docs/governance/AIOS_FAILURE_MEMORY_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md`
- `docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md`
- `docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md`
- `docs/workflows/AIOS_AEE_GOVERNANCE_VALIDATOR_V1.md`
- `Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_CHECKPOINT.md`
- `Reports/core_delivery/AIOS_AEE_GOVERNANCE_VALIDATOR_V1_REPORT.md`
- `automation/governance/aios_aee_governance_validator_v1.py`
- `scripts/governance/run_aios_aee_governance_validator_v1.py`
- `tests/governance/test_aios_aee_governance_validator_v1.py`
- `tests/fixtures/governance/aee_validator/*`

## Required Checks

1. file existence
2. markdown H1 presence
3. Purpose section
4. Scope section
5. required safety-boundary phrases
6. required cross-links
7. AGENTS.md pointer presence
8. checkpoint/report pairing
9. protected handoff separation
10. no forbidden broad staging phrases in executable handoff blocks
11. no placeholder patterns in executable evidence blocks
12. CI-sensitive assignment-name check in non-fixture governance scope
13. 1312 recovery rule presence when applicable
14. lane/packet/worktree law presence

## Finding Codes

- `AIOS-AEE-V1-1000/1001` - missing artifact or wrong path type
- `AIOS-AEE-V1-1101/1102/1103` - markdown structure failures
- `AIOS-AEE-V1-1201` - missing safety-boundary phrase
- `AIOS-AEE-V1-1301/1302` - cross-link/pointer warnings
- `AIOS-AEE-V1-1401` - checkpoint-report pairing failure
- `AIOS-AEE-V1-1501/1502/1503` - protected handoff checks
- `AIOS-AEE-V1-1601` - placeholder-shaped text found
- `AIOS-AEE-V1-1701` - sensitive assignment name
- `AIOS-AEE-V1-1702` - forbidden broad staging commands
- `AIOS-AEE-V1-1801` - `1312` recovery rule missing
- `AIOS-AEE-V1-1901` - lane/packet/worktree law missing

## CLI Usage

```text
python scripts/governance/run_aios_aee_governance_validator_v1.py
python scripts/governance/run_aios_aee_governance_validator_v1.py --write-report
python scripts/governance/run_aios_aee_governance_validator_v1.py --json
python scripts/governance/run_aios_aee_governance_validator_v1.py --strict
python scripts/governance/run_aios_aee_governance_validator_v1.py --write-report --strict
```

## Owner PowerShell Usage

```text
cd C:\Dev\Ai.Os
python scripts/governance/run_aios_aee_governance_validator_v1.py --strict
python scripts/governance/run_aios_aee_governance_validator_v1.py --write-report --strict
```

## Integration with AEE Long Campaign Doctrine

This validator operationalizes the doctrine from:

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`

## Integration with Protected Publishing Handoff

Validation confirms publish/check and merge/sync handoff separation and confirms the two-block handoff pattern required by protected action governance.

## Integration with GitHub CI Failure Recovery

Validation coverage includes a deterministic scan for:

- placeholder-style command text
- assignment-like fragments that trigger `secret`/`broker` scans
- check-watch-to-merge block ordering

## Safety Statement

This validator and workflow remain explicitly non-executive:

This artifact does not authorize broker/API access.  
This artifact does not authorize credential access.  
This artifact does not authorize trading execution.  
This artifact does not authorize money movement.  
This artifact does not authorize commit/push/merge without explicit Human Owner approval.

## Execution Notes

- No network usage.
- No credential lookups.
- No broker, API, or live-order behavior.
- Pure markdown and local path inspection.
- Deterministic outputs for tests and automation.
