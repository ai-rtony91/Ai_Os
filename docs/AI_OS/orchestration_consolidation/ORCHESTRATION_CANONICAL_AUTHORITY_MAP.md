# Orchestration Canonical Authority Map

This map defines the target control authority for future consolidation. It is not an APPLY instruction.

| Authority | Canonical owner | Current canonical or candidate path | Notes |
|---|---|---|---|
| Goal intake | Human owner / AI_OS Manager Control | `AGENTS.md`, `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`, `docs/AI_OS/openai_api_bridge/AIOS_OPENAI_TO_PACKET_GENERATOR_PATH.md` | Goals become packets; casual text is not executable. |
| Packet authority | Tokenized AI_OS packet with identity fields | `AGENTS.md`, `automation/orchestration/work_packets/`, `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md` | Packet must include token, lane, mode, paths, validators, stop point. |
| Dispatcher authority | Dispatch route scoring and blocker classification | `docs/AI_OS/dispatch/`, `schemas/aios/dispatch/`, `automation/orchestration/dispatch/` | Dispatcher routes; it does not grant runtime, commit, push, or merge. |
| Worker assignment authority | Worker registry and packet-scoped lane identity | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`, `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` | Duplicate worker registries should converge here after review. |
| Validator authority | Validator standards and validator runner evidence | `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`, `automation/orchestration/validators/`, `automation/orchestration/validator_chain_runner/` | Validator output is evidence only, never approval. |
| Approval authority | Human Owner approval plus approval gate evidence | `AGENTS.md`, `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`, `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`, `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | Approval must be explicit, exact-scope, current-session, and action-specific. |
| Clean-state authority | Git/worktree clean-state verifier | `automation/orchestration/clean_state/`, `automation/orchestration/clean_state_gate.ps1`, `docs/workflows/AI_OS_PR_LANE_RUNNER.md` | Clean status is a gate, not permission to proceed. |
| Commit/PR authority | Protected main PR lane | `docs/workflows/AI_OS_COMMIT_PUSH_GATE.md`, `docs/workflows/AI_OS_PR_LANE_RUNNER.md`, `automation/orchestration/pr_gates/`, `automation/orchestration/commit_packages/` | Direct protected work on main remains blocked unless separately approved. |
| Night Supervisor authority | Preview/report-only until runtime gates pass | `docs/AI_OS/night_supervisor/`, `docs/AI_OS/autonomy/PHASE_18_13_TO_18_18_NIGHT_SUPERVISOR_RUNWAY.md`, `automation/orchestration/night_supervisor/` | Runtime scripts are protected; no start/resume from consolidation. |
| OpenAI CLI authority | Planner/generator only, supervised | `docs/AI_OS/openai_cli/`, `docs/AI_OS/openai_api_bridge/` | OpenAI output is DRAFT_ONLY until dispatcher, validators, and human approval. |
| Red-team/eval authority | Safety finding pipeline | `docs/AI_OS/red_team/`, future trace/eval docs | Findings feed improvement loop, Codex handoff, and PR. |

## Canonical Target Rule

When two files both appear to grant authority, the active hierarchy is:

```text
AGENTS.md
-> docs/governance and docs/workflows
-> docs/AI_OS phase doctrine
-> schemas/aios contracts
-> automation/orchestration DRY_RUN helpers
-> runtime evidence
```

Runtime evidence, dashboard state, telemetry, validator PASS, queue state, or generated packet state must not override human approval or protected-action gates.

