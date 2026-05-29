# AI_OS Night Supervisor — Autonomy Wiring (Effector Layer on Codex V2)

Status: effector layer scaffolded, **fail-closed (autonomy OFF by default)**
Authority: subordinate to `AGENTS.md`, `RISK_POLICY.md`, Human Owner.
Spine: Codex Night Supervisor V2 is canonical. This layer is downstream only.

## 1. What this is

The Codex V2 spine *decides and previews* (read-only). This layer adds the one
capability the spine does not have: actually invoking the PowerShell effector
**hands** — and it keeps that capability OFF by default, behind an explicit
allowlist, an env arm, and a kill switch.

## 2. Architecture

```
Codex V2 Safety Spine (canonical, read-only / preview):
  queue_scanner
    → worker_route_recommender / worker_assignment
      → lock_manager        (lock evidence; never claims/releases)
        → approval_officer   (approval evidence; never grants)
          → packet_dispatcher (DRY_RUN preview + receipt)
            → telemetry_preview
              → supervisor_engine_v2  ──►  routing_contracts[]

Claude Effector Layer (additive, OFF by default), strictly downstream:
  routing_contract WHERE dispatch_status==DRY_RUN_PREVIEW
                     AND approval_status IN {APPROVED, NOT_REQUIRED}
                     AND lock_status==FREE
    → effector_intent      (derive proposal from the contract)
      → effector_dispatcher (six AND-ed gates)         ── DISABLED by default
        → scripts/*.ps1     (the hands)
```

| Body part | Module | Owner | Mutates? |
|---|---|---|---|
| Brainstem / decision + preview | `supervisor_engine_v2.py` + spine modules | Codex | No |
| Routing contract (shared state) | `packet_routing_contract.v1.json` | Codex | No |
| Lock evidence | `lock_manager.py` | Codex | No |
| Approval evidence | `approval_officer.py` | Codex | No |
| Dispatch preview / receipt | `packet_dispatcher.py` | Codex | Only `apply_enabled` JSON receipts |
| Effector proposal | `effector_intent.py` | Claude | No |
| Effector dispatch (the hands) | `effector_dispatcher.py` | Claude | Only when all gates pass |
| Single-pass stage | `effector_stage.py` | Claude | Orchestrates above |

## 3. The six execution gates

`effector_dispatcher` executes a hand-script only when ALL are true at once:
`kill_switch_clear`, `effector_actionable`, `capability_allowed`,
`execution_enabled`, `env_apply_armed`, `contract_cleared`. The first five are
the Claude layer's own controls; `contract_cleared` simply trusts the Codex
spine verdict — this layer never re-judges approval or locks.

## 4. Enablement runbook (Human Owner only, on the Windows runtime)

```powershell
# 0. Dry pass — verify proposals. Executes nothing.
python services\python_supervisor\effector_stage.py --repo-root . --pretty

# 1. Codex spine must already mark the contract DRY_RUN_PREVIEW
#    (approved in approval_inbox + lock FREE). The effector layer trusts that.

# 2. Arm the environment (per session, never committed):
$env:AIOS_SUPERVISOR_APPLY = "1"

# 3. Enable ONE rung of the ladder and apply:
python services\python_supervisor\effector_stage.py --ladder-through heartbeat --apply --pretty

# Kill switch — overrides everything, instantly:
$env:AIOS_NIGHT_SUPERVISOR_DISABLE = "1"
```

Graduation order: `heartbeat` → `claim_lock` → `assign` → `mark_done` →
`release_lock`, one night per rung, reviewing each pass before the next.

## 5. Boundaries that remain hard

- No live trading; no broker/OANDA/secrets/credentials paths — ever.
- Commit/push/merge are NOT effectors; they stay with the human-invoked
  `Run-AiOsOperatorLoop.APPLY.ps1`.
- No scheduler and no daemon: `effector_stage.py` is a single pass.
- No duplication of Codex authority: approval and lock decisions are read from
  the spine, never recomputed here.
- Default state on a fresh checkout is fully blocked.
