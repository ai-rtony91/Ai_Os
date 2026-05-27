# AI_OS End-to-End Preview Chain Workflow

This workflow defines the single-command Stage 2 preview chain for AI_OS self-build planning.

The chain is preview-only. It is not autonomy execution, not a daemon, not a scheduled task, not a background loop, and not an API-driven runtime. It creates no approval, starts no worker, mutates no queue, stages no files, commits nothing, pushes nothing, creates no PR, and performs no merge.

## Flow

The end-to-end preview command runs one single pass:

1. Morning brief evidence.
2. Morning brief packet preview.
3. Fixture-only API planner adapter preview.
4. Approval-gated handoff preview.
5. Loop-engine preview.
6. Commit/push/PR controller preview.
7. Unified end-to-end preview output.

The unified output is evidence only. It can help a human decide the next safe packet, but it does not approve or execute the packet.

## Authority Boundary

The chain is limited to Level 1 and Level 2 under `docs/governance/AI_OS_AUTONOMY_LEVELS.md`.

Allowed:

- read local fixture evidence
- call existing DRY_RUN preview helpers
- aggregate helper output
- print JSON preview evidence

Blocked:

- API key usage
- `.env` usage
- external model API calls
- subprocess Codex execution
- scheduled or background loops
- auto APPLY
- auto commit
- auto push
- auto PR creation
- auto merge
- approval mutation
- queue mutation
- worker launch
- broker/OANDA/live trading/webhook/secrets/dashboard scope

## API Boundary

APIs remain blocked in this stage.

OpenAI, Claude, Tasker, Azure, and Bitwarden integrations may be represented by fixtures and preview schemas only. No live provider call, cloud authentication, vault read, secret access, deployment, webhook, or remote mutation is authorized by this workflow.

## Approval Boundary

Level 3, Level 4, and Level 5 remain gated.

Commit, push, and PR creation still require explicit approval markers:

- `APPROVE_COMMIT`
- `APPROVE_PUSH`
- `APPROVE_PR_CREATE`

Merge remains separately protected. Trading, broker, OANDA, secrets, credentials, key rotation, real webhooks, and real orders remain hard-gated.

## Failure Behavior

If any helper fails, the chain marks `chain_state` as `BLOCKED` and preserves the helper error as evidence. The chain does not create execution authority.

Next safe action: review the unified preview output, then issue a separate scoped packet for any future APPLY work.
