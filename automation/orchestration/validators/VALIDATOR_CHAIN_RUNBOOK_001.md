# Validator Chain Runbook 001

## Purpose

The validator chain gives AI_OS one repeatable safety path before APPLY, commit, or push.

It reduces manual checking by putting the required checks in a fixed order. A worker can still report context, but the same core checks must run every time.

## Validator Order

1. `git_clean_state`
2. `allowed_paths`
3. `blocked_paths`
4. `identity_spine`
5. `json_integrity`
6. `powershell_syntax`
7. `markdown_exists`
8. `no_secrets`
9. `no_live_trading_enablement`
10. `approval_gate`
11. `commit_package_review`
12. `final_git_status`

## What Each Check Protects

| Validator | Protects |
| --- | --- |
| `git_clean_state` | Prevents new work from hiding unrelated dirty files, staged files, or untracked files. |
| `allowed_paths` | Confirms the worker stays inside the approved scope. |
| `blocked_paths` | Stops edits to protected, dashboard, security, broker, API, or live trading areas. |
| `identity_spine` | Confirms packet identity, supervisor identity, worker identity, zone, approval authority, validator chain, lock identity when needed, and stop point are present. |
| `json_integrity` | Confirms changed JSON files parse before they become runtime inputs. |
| `powershell_syntax` | Confirms changed `.ps1` files parse before any later execution. |
| `markdown_exists` | Confirms required docs and reports are present. |
| `no_secrets` | Blocks secrets, credentials, tokens, private keys, and `.env` material. |
| `no_live_trading_enablement` | Blocks broker, OANDA, webhook, live trading, and real order enablement. |
| `approval_gate` | Confirms APPLY, commit, and push are controlled by human approval. |
| `commit_package_review` | Confirms exact-file commit packaging and blocks blind staging. |
| `final_git_status` | Gives the operator the final changed-file view before any next step. |

## Packet-Aware Path Scope

`Invoke-OrchestrationValidatorChain.DRY_RUN.ps1` supports exact packet scope
flags for validating a specific packet change set:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1 `
  -ChangedPath "apps/trading_lab/trading_lab/watchtower.py" `
  -AllowedPath "apps/trading_lab/trading_lab/watchtower.py" `
  -ForbiddenPath "apps/dashboard/","secrets/",".env"
```

Use `-ChangedPath` for exact packet files when unrelated dirty backlog exists.
Use `-AllowedPath` with one or more PowerShell array values for exact
packet-approved files only. Use `-ForbiddenPath` with one or more PowerShell
array values for packet and security blockers.
Forbidden paths always win over allowed paths. Broad `apps/` packet allowance is
blocked; do not use it to approve Trading Lab changes.

## When To Stop

Stop immediately when a validator reports `FAIL` for:

- protected root files changed without explicit approval
- blocked paths changed
- JSON parse failure
- PowerShell syntax failure
- suspected secrets
- broker, OANDA, API key, webhook, live trading, or real order enablement
- missing approval before APPLY
- missing identity, lane, approval, validator, lock, or stop-point fields before APPLY
- missing commit package before staging or commit
- requested `git add .` or `git add -A`

## West Territory Validator Routing

West territory packets must route through:

- packet identity validation.
- lane identity validation.
- path ownership validation.
- forbidden path validation.
- lock validation when shared or APPLY paths are involved.
- approval-gate validation.
- stop-point validation.
- PR-lane validation before push or PR.
- paper-only trading boundary validation.

West territory validation must block APPLY when West attempts to claim `automation/orchestration/`, `automation/operator/`, `services/`, `telemetry/`, `scripts/`, root authority files outside explicit pointer changes, trading execution paths, broker/OANDA/API-key/live-order paths, or `aios/modules/trader/` before Human Owner decision.

## When Human Review Is Required

Human review is required when:

- the repo is dirty before work starts
- untracked files exist
- changed files are outside the active packet
- two workers may own the same path
- approval state is missing, stale, rejected, or unclear
- a validator reports `WARN`
- stale packet, stale lock, or stale worker state exists
- commit or push is being considered

## Why Failed Validation Blocks Commit And Push

Commit and push publish state for other workers and for GitHub main review.

If validation fails, the package may contain unrelated files, invalid runtime JSON, unsafe PowerShell, missing approval, or blocked trading/security changes. A failed validator therefore blocks commit and push until the operator reviews and corrects the issue.

## Human Control Boundary

This chain does not:

- edit files
- stage files
- commit
- push
- install dependencies
- call external services
- create startup tasks
- create scheduled tasks
- connect to brokers
- place orders
- enable live trading

## Next Safe Action

Run `automation/orchestration/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1`, run `automation/orchestration/validators/Test-ValidatorChainConfig.DRY_RUN.ps1`, then run `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`.

