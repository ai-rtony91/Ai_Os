# AIOS Protected Publishing Handoff V1

## Purpose

Define the exact owner PowerShell handoff format for AIOS lanes that finish local APPLY work but must stop before protected publishing actions such as staging, committing, pushing, PR creation, check watching, merging, or local main sync.

## Scope

This workflow applies when Codex has completed approved local work and must hand off protected Git or GitHub actions to the Human Owner.

This artifact does not authorize broker/API access. This artifact does not authorize credential access. This artifact does not authorize trading execution. This artifact does not authorize money movement. This artifact does not authorize commit/push/merge without explicit Human Owner approval. It does not authorize PR creation, scheduler activation, webhook activation, daemon activation, production activation, reset, clean, stash, deletion, or file movement.

## When Codex Must Stop And Hand Off To Owner PowerShell

Codex must stop and hand off when the next action is:

- `git add`
- `git commit`
- `git push`
- `gh pr create`
- `gh pr checks --watch` when the packet classifies check watching as protected
- `gh pr merge`
- local main sync after merge
- branch deletion
- reset or clean
- any protected action after Codex has hit `CreateProcessAsUserW failed: 1312`

Codex must also hand off when GitHub authentication, CI state, branch protection, or shell launch reliability cannot be verified inside Codex.

## Exact PowerShell Handoff Format

### Git Status

```powershell
cd C:\Dev\Ai.Os
git status --short --branch
```

### Exact-File Git Add

```powershell
git add -- "AGENTS.md" "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md" "docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md" "docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md" "docs/governance/AIOS_FAILURE_MEMORY_V1.md" "docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md" "docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md" "docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md" "docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md" "docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md" "docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md" "Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_CHECKPOINT.md" "Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_REPORT.md"
```

Exact-file staging must name only approved files. Do not use `git add .`.

### Git Diff Cached Check

```powershell
git diff --cached --check
git diff --cached --name-only
```

### Git Commit

```powershell
git commit -m "docs(aios): add autonomous execution long campaign foundation"
```

### Git Push

```powershell
git push -u origin lane/aios-aee-long-campaign-foundation-v1
```

### GitHub PR Create

```powershell
gh pr create --base main --head lane/aios-aee-long-campaign-foundation-v1 --title "docs(aios): add autonomous execution long campaign foundation" --body-file Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_REPORT.md
```

### GitHub PR Checks

```powershell
gh pr checks --watch
```

### GitHub PR Merge

```powershell
gh pr merge --squash
```

Merge requires separate explicit Human Owner approval after checks pass.

### Git Pull Fast-Forward Only

```powershell
git switch main
git pull --ff-only origin main
git status --short --branch
```

Local main sync requires separate explicit Human Owner approval.

## 1312 Protected Action Rule

If Codex hits `CreateProcessAsUserW failed: 1312` on protected Git/GitHub actions, do not route those actions back to Codex. Move that protected publishing lane to owner PowerShell.

Do not ask Codex to retry protected Git/GitHub publishing commands after known process-launch failure. Preserve the exact file list and command block in the final report.

## Check Watch And Merge Separation Rule

Do not put merge commands immediately after check-watch commands unless the script stops hard on failed checks.

Check watching can end with failed, pending, skipped, missing, or blocked checks. Passing checks are evidence only and do not approve merge.

## Separate Fix/Check Block From Merge/Sync Block

Publishing handoff must separate:

- fix/check block: status, exact-file staging, cached diff check, commit, push, PR create, check watch.
- merge/sync block: merge only after checks pass and Human Owner approves merge, then sync local main only after merge approval and success.

## Example Safe Publish Block

```powershell
cd C:\Dev\Ai.Os
git status --short --branch
git add -- "AGENTS.md" "docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md" "docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md" "docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md" "docs/governance/AIOS_FAILURE_MEMORY_V1.md" "docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md" "docs/governance/AIOS_CAMPAIGN_ARBITRATION_DOCTRINE_V1.md" "docs/workflows/AIOS_ISOLATED_WORKTREE_CAMPAIGN_EXECUTION_V1.md" "docs/workflows/AIOS_LONG_CAMPAIGN_CODEX_OPERATING_MODE_V1.md" "docs/workflows/AIOS_PROTECTED_PUBLISHING_HANDOFF_V1.md" "docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md" "Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_CHECKPOINT.md" "Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_REPORT.md"
git diff --cached --check
git commit -m "docs(aios): add autonomous execution long campaign foundation"
git push -u origin lane/aios-aee-long-campaign-foundation-v1
gh pr create --base main --head lane/aios-aee-long-campaign-foundation-v1 --title "docs(aios): add autonomous execution long campaign foundation" --body-file Reports/core_delivery/AIOS_AEE_LONG_CAMPAIGN_FOUNDATION_V1_REPORT.md
gh pr checks --watch
```

Stop after checks. Do not merge from this block.

## Example Failed-Check Recovery Block

```powershell
cd C:\Dev\Ai.Os
gh pr checks
gh run list --branch lane/aios-aee-long-campaign-foundation-v1 --limit 5
gh run view --log
git status --short --branch
```

After identifying the failing check, create a focused repair packet or owner-approved scoped fix. Do not merge failing checks.

## Merge And Sync Block

Run only after checks pass and Human Owner separately approves merge and local sync:

```powershell
cd C:\Dev\Ai.Os
gh pr merge --squash
git switch main
git pull --ff-only origin main
git status --short --branch
```

## Related Doctrine And Workflows

- `docs/governance/AIOS_AUTONOMOUS_EXECUTION_AND_FAILURE_RECOVERY_DOCTRINE_V1.md`
- `docs/governance/AIOS_FAILURE_MEMORY_V1.md`
- `docs/workflows/AIOS_AUTONOMOUS_EXECUTION_ENGINE_V1.md`
- `docs/workflows/AIOS_FAILURE_RECOVERY_PLAYBOOKS_V1.md`
- `docs/workflows/AIOS_CAMPAIGN_CHECKPOINT_AND_RESUME_V1.md`
- `docs/workflows/AIOS_GITHUB_CI_FAILURE_RECOVERY_V1.md`
- `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`
- `docs/workflows/AI_OS_PR_LANE_RUNNER.md`
