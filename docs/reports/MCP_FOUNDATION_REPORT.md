# MCP Foundation Report

Packet: AIOS-AUTONOMY-DOCS-SYNTHESIS-DRYRUN-001
Mode: DRY_RUN report creation only
Branch inspected: phase-night-supervisor-layer2-memory
Worktree: C:\Dev\Ai.Os

## Bottom Line

AI_OS has MCP doctrine, but no active MCP foundation.

The repo contains a safe read-first MCP prototype plan in `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md` and a Python supervisor skeleton that explicitly says it is not an MCP server in `services/python_supervisor/README.md`. I found no active MCP client config, server config, Inspector runbook, filesystem-server validation record, MCP tool registry, or MCP-specific denylist enforcement wired into AI_OS.

Current status: DOCUMENTED ONLY.

Implementation readiness score: 2/5. The safety model is strong, but no operational MCP path is installed, configured, validated, or connected.

## Current MCP Readiness

| Capability | Status | Evidence | Gap |
|---|---|---|---|
| MCP concept and boundary | PARTIAL | `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md` | Plan exists, no implementation. |
| MCP Inspector procedure | MISSING | No repo runbook found for Inspector | Operator needs a manual validation checklist before install. |
| Filesystem MCP workflow | DOCUMENTED ONLY | Prototype plan names Filesystem MCP | No server config, no read-only proof, no allowed path manifest. |
| Safe read-only local server concept | PARTIAL | Prototype plan requires read-only v1; `services/python_supervisor/README.md` says future MCP must fail closed | No enforcement layer proves write/delete tools are absent. |
| MCP audit receipts | PARTIAL | `schemas/aios/orchestration/command_request.schema.json`, `command_audit_ledger.schema.json` | Contracts exist, no MCP audit writer is wired. |
| MCP approval boundary | PARTIAL | `docs/security/approval-model.md`, `automation/orchestration/policy/AIOS_APPROVAL_TIER_POLICY.json` | Not connected to MCP tool calls. |
| MCP runtime integration | MISSING | No `mcp.json`, no MCP server entry point found in inspected evidence | AI_OS cannot yet inspect itself through MCP. |

## Repository Evidence

- `docs/workflows/AI_OS_MCP_PROTOTYPE_PLAN.md` defines read-first MCP servers for filesystem, Git, shell preview, queue, approval, telemetry, worker registry, and runtime state. It repeatedly states MCP is evidence only and cannot approve or execute.
- `services/python_supervisor/README.md` says the Python supervisor is not an MCP server, command executor, scheduler, daemon, API client, or queue mutator.
- `schemas/aios/orchestration/command_request.schema.json` describes a future command request contract shared by MCP, local runner, approval gate, telemetry, and worker handoff. It blocks arbitrary shell, delete, move, rename, installs, secrets, broker, OANDA, trading, webhooks, and live orders.
- `automation/orchestration/policy/AIOS_APPROVAL_TIER_POLICY.json` defines read-only commands as low-friction, but hard-gates mutation, secrets, trading, runtime, policy, and broad Git actions.
- `AGENTS.md` explicitly says MCP servers may be better for long-term tool coordination, but protected actions remain human-gated.

## MCP Inspector

Question: does MCP Inspector exist in repo docs?

Answer: no active AI_OS Inspector runbook was found. The term "Inspector" appears in role descriptions and in prior generated report text, but not as a canonical workflow that tells Anthony how to install, launch, validate, and stop before connecting MCP to the live repo.

Required before install:

1. A manual MCP Inspector checklist.
2. A local-only stdio explanation.
3. A denylist proving no active repo write/delete/move/rename tools are exposed.
4. A pass/fail capture format under an approved evidence path.
5. A hard stop before connecting write-capable Filesystem MCP to `C:\Dev\Ai.Os`.

## Recommended MCP Installation Sequence

This is a recommendation only. No install was performed.

1. Write an MCP Safe Hands architecture file or workflow file in a separate APPLY packet.
2. Define Phase 0 as manual-only: the operator installs and tests MCP tools, not Codex.
3. Use local stdio first. Do not start remote Streamable HTTP MCP servers in Phase 0.
4. Test MCP Inspector against a harmless target first.
5. Test a filesystem server against a read-only snapshot or OS-protected copy, not the live repo.
6. Confirm visible tools and prove write/delete/move/rename operations are unavailable or blocked.
7. Record the Inspector evidence.
8. Only after manual proof, connect the read-only MCP path to an AI_OS read task.
9. Do not widen to write access until a separate APPLY packet defines safe folders, denylist, validator, and audit receipts.

## Safe Local Read-Only Server Concept

Target Phase 0 shape:

```text
Codex or ChatGPT host
-> MCP client inside the host
-> local stdio filesystem MCP server
-> allowlisted AI_OS evidence paths
-> read/list/search only
-> no write/delete/move/rename/command tools
```

Approved initial read classes should be:

- `AGENTS.md`
- `README.md`
- `WHITEPAPER.md`
- `docs/governance/`
- `docs/workflows/`
- `docs/security/`
- `docs/architecture/`
- `docs/audits/`
- `schemas/aios/orchestration/`
- selected `automation/orchestration/` evidence files
- selected `telemetry/` evidence after retention and privacy policy review

Blocked in Phase 0:

- secrets, credentials, `.env`, API keys
- broker, OANDA, live-order, live trading paths
- active runtime mutation
- queue mutation
- approval mutation
- worker launch
- Git mutation
- package install
- PR creation, merge, commit, push

## Omen vs Pi 5 Placement

Repo-grounded recommendation:

- Omen first. Local stdio MCP must live on the same machine as the agent and the active repo. For AI_OS today, that means HP Omen plus `C:\Dev\Ai.Os`.
- Pi 5 later. The Pi should not run the coding agent in Phase 0. It is only a later candidate for always-on remote read/report services after OAuth 2.1, network hardening, audit logging, and stop controls exist.
- No remote MCP server should be introduced before the local stdio path is proven.

## Steel Door Mapping

The MCP layer must physically omit tools that can reach the steel door.

Steel door actions:

- placing trades or touching the order path, real or paper
- touching keys, passwords, secrets, credentials, OAuth secrets, broker tokens
- pushing to protected main
- merging PRs
- deploying production
- creating startup tasks, scheduled tasks, daemons, or uncontrolled background loops
- mutating approval, queue, lock, worker, or runtime state without a separate approved APPLY packet

Safety principle: do not rely on the agent to avoid danger. Build the MCP tool surface so the dangerous action is unreachable.

## Missing Governance Controls

1. MCP Safe Hands canonical architecture or workflow document.
2. MCP Inspector manual validation checklist.
3. MCP server allowlist and denylist policy.
4. MCP read-only proof format.
5. MCP audit ledger writer or receipt schema usage.
6. MCP tool classification registry.
7. MCP failure response standard.
8. MCP path ownership mapping to `source-of-truth-map.md`.
9. MCP phase gate: snapshot only -> active repo read-only -> approved generated evidence writes.
10. MCP remote-server hardening policy for any future Pi 5 use.

## Risks

- The common filesystem MCP server pattern may expose write-capable tools. AI_OS should not point any write-capable server directly at the live repo until a read-only wrapper, OS-level read-only snapshot, or tool-gated proxy proves writes cannot happen.
- MCP can reduce copy/paste relay work, but it can also become a second command lane if not governed.
- Remote MCP before local stdio proof would add auth, network, service hardening, uptime, and audit complexity too early.
- MCP output must remain evidence. It must not approve APPLY, commit, push, merge, deployment, broker access, or trading.

## Exact Stop Point Before Install

Stop before any install, `npx`, server launch, package download, config write, or MCP connection to the active repo.

The next packet must be an APPLY or operator-manual packet that only creates the MCP Safe Hands document/checklist. It must not install MCP or launch a server.

## Next Safe Packet Recommendation

Recommended first APPLY lane:

```text
Packet: AIOS-MCP-SAFE-HANDS-DOCS-APPLY-001
Mode: APPLY
Allowed paths:
- docs/architecture/toolchain-mcp-safe-hands.md
- one pointer line in the existing autonomy-loop document, if located and explicitly approved
Forbidden:
- MCP install
- package install
- server launch
- active repo MCP connection
Stop:
- after documentation and validation only
```
