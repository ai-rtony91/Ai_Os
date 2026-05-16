# Supervisor Assignment Bootstrap

This bootstrap note connects the supervisor planner to the existing manual lane model.

The supervisor assignment system is preview-first. It may inspect the goal, lane registry, validator config, approval gates, and packet schemas. It must not auto-launch Codex, open worker windows, create scheduled tasks, create startup tasks, connect brokers, call APIs, commit, push, or create PRs.

## Bootstrap Inputs

- Work goal from the operator.
- Lane registry: `automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json`
- Validator chain config: `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`
- Work packet schema: `work_packets/schema.json`
- Approval gate files: `automation/orchestration/approval_inbox`
- Commit package files: `automation/orchestration/commit_packages`

## Bootstrap Output

- Worker assignment plan.
- Packet creation preview.
- Lane requirement detection.
- Validator routing.
- Approval gate routing.
- Commit and PR package preview.
- Next safe action.

## Stop Condition

Stop after the DRY_RUN plan is printed and validation status is reported. Do not move any preview packet into an active queue without separate approval.
