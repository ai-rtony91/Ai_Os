# AIOS GitHub CI Failure Recovery V1

## Purpose

Define a safe inspection and recovery workflow for GitHub CI failures in AIOS PR lanes so workers inspect the failing job and step before changing files.

## Scope

This workflow applies to AIOS pull requests and lane branches when CI, validation, or GitHub checks fail after a protected publishing handoff.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize PR creation, scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## CI Failure Inspection Workflow

1. Confirm the PR and branch.
2. Inspect check summary.
3. Fetch the failing run metadata.
4. Inspect the failing job.
5. Inspect the failing step.
6. Inspect the workflow rule, regex, or command that failed.
7. Reproduce locally only when the command is safe and inside scope.
8. Create a focused repair plan.
9. Apply only if a packet approves the exact files.
10. Validate locally and through CI.

Do not guess from the check name alone.

## How To Fetch Failing Job

Owner PowerShell or approved GitHub CLI inspection may use:

```powershell
cd C:\Dev\Ai.Os
gh pr checks
gh run list --branch lane/aios-aee-long-campaign-foundation-v1 --limit 10
$RunId = "1234567890"
gh run view $RunId --json jobs
```

Use the actual run ID from GitHub output. If the run ID is unknown, do not invent it.

## How To Inspect Failing Step

```powershell
$RunId = "1234567890"
$JobId = "9876543210"
gh run view $RunId --job $JobId --log
```

Read the failing step name, command, file path, line number, and exact error text. If logs include secrets or private data, stop and sanitize before adding evidence to any repo report.

## How To Inspect Workflow Regex

When a governance, placeholder, secret, or structure scan fails:

1. Identify the workflow file and step command from the failing log.
2. Read the regex or scanner command.
3. Identify the exact matched file and text.
4. Decide whether it is a real violation, false positive, or unclear.
5. Repair source text only when the packet allows that path.

Do not edit GitHub workflow files in a docs-only repair unless a separate packet explicitly allows it.

## How To Reproduce CI Locally

Run the smallest safe command that matches the failing step. Examples:

```powershell
git diff --check
rg -n "pattern from failing workflow" docs/governance docs/workflows Reports/core_delivery
```

Do not run broad test suites, install dependencies, or execute scripts outside the packet scope unless the repair packet approves them.

## How To Avoid Guessing

- Use GitHub run logs, not memory.
- Use exact failing file and line when available.
- Distinguish true violation from parser false positive.
- Confirm local reproduction before editing when practical.
- Keep repair scope to the failing rule.
- Do not rewrite unrelated docs to make CI pass.

## Playbook: Secret-Assignment Scan

- Detection signature: CI flags a source/config assignment using exact words api_key, apikey, secret, token, password, or broker with quoted non-placeholder values.
- Classification: `CI_SECRET_ASSIGNMENT_REVIEW`.
- Recovery: Rename non-sensitive example/status variable names and remove assignment-looking prose if safe. Use `broker_status` instead of `broker` when assigning quoted status values.
- Forbidden recovery: Add secrets, print credentials, disable the scan, or weaken secret-prevention policy.
- Validator: rerun local text scan and GitHub CI.
- Stop condition: real sensitive value may be present or CI still fails.

## Playbook: Placeholder Identity Scan

- Detection signature: CI flags unresolved placeholder identity, fake branch, fake path, missing owner, or example-only packet content as executable.
- Classification: `PLACEHOLDER_IDENTITY_REVIEW`.
- Recovery: Replace with real packet fields or label content as non-executable reference. Remove unresolved placeholders from executable packet examples.
- Forbidden recovery: Leave placeholders in Codex-executable prompts or ask the owner to repair malformed packets manually.
- Validator: local placeholder scan and packet completeness review.
- Stop condition: placeholder remains in executable content.

## Playbook: PowerShell Syntax Failure

- Detection signature: CI reports PowerShell parse error, unexpected token, missing brace, invalid parameter, or execution-policy issue.
- Classification: `POWERSHELL_SYNTAX_REVIEW`.
- Recovery: Inspect exact script and line. Repair only if the packet allows scripts; otherwise document and stop.
- Forbidden recovery: Run unreviewed scripts, broaden execution policy, or edit automation in a docs-only lane.
- Validator: PowerShell parser check for the exact script when allowed.
- Stop condition: script path is outside allowed paths or parser still fails.

## Playbook: Python Compile Failure

- Detection signature: CI reports Python syntax error, import failure, missing module, or compile error.
- Classification: `PYTHON_COMPILE_REVIEW`.
- Recovery: Inspect exact file and line. Repair only if code paths are allowed; otherwise create a focused code packet recommendation.
- Forbidden recovery: Install dependencies, edit runtime/trading logic, or change code in a docs-only lane.
- Validator: targeted Python compile or test command when allowed.
- Stop condition: code path is forbidden or failure touches safety-critical runtime/trading behavior.

## Playbook: Governance Check Failure

- Detection signature: CI reports missing H1, missing Purpose, missing Scope, missing safety language, forbidden placeholder, duplicate authority, or protected path drift.
- Classification: `GOVERNANCE_CHECK_REVIEW`.
- Recovery: Repair exact governance/doc structure inside approved paths and rerun the check.
- Forbidden recovery: Duplicate authority, remove safety boundaries, or edit root/protected authority outside packet approval.
- Validator: structural markdown check, source-of-truth review, and `git diff --check`.
- Stop condition: repair requires authority expansion or protected root changes not approved.

## Specific Prevention Rule

Avoid source/config assignments using exact words api_key, apikey, secret, token, password, or broker with quoted non-placeholder values.

Use neutral names for non-sensitive status examples. Example: Use `broker_status` instead of `broker` when assigning quoted status values.

## Owner PowerShell Handoff For CI Fixes

Inspection block:

```powershell
cd C:\Dev\Ai.Os
gh pr checks
gh run list --branch lane/aios-aee-long-campaign-foundation-v1 --limit 10
$RunId = "1234567890"
$JobId = "9876543210"
gh run view $RunId --json jobs
gh run view $RunId --job $JobId --log
```

Repair block after a focused packet approves exact files:

```powershell
cd C:\Dev\Ai.Os
git status --short --branch
git diff --check
git add -- "docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md"
git diff --cached --check
git commit -m "docs(aios): repair github ci recovery workflow"
git push
gh pr checks --watch
```

Do not run example values directly. Replace run ID, job ID, file, and commit message with exact owner-approved values before execution.

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_FAILURE_MEMORY_V1.md`
- `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md`
- `docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md`
- `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`
- `docs/workflows/AI_OS_PR_LANE_RUNNER.md`
- `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`
