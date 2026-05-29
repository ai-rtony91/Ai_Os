# AI_OS Night Supervisor — Autonomy Wiring (Brainstem → Arms → Hands)

Status: scaffolded + coded, **fail-closed (autonomy OFF by default)**
Authority: subordinate to `AGENTS.md`, `RISK_POLICY.md`, Human Owner.
Mode: DRY_RUN unless the operator explicitly arms execution (see §4).

## 1. What this is

This connects the read-only Night Supervisor **brainstem**
(`services/python_supervisor/supervisor_engine.py`) to the existing PowerShell
effector **hands** (`scripts/*.ps1`) through a gated **arm**
(`action_dispatcher.py`). It lets the supervisor *propose* and — once the Human
Owner arms it — *perform* low-risk queue actions overnight, while keeping every
protected action behind a Human-Owner approval gate.

## 2. Anatomy

| Body part | Module | Mutates state? |
|---|---|---|
| Brainstem (decides) | `supervisor_engine.py` + scanner/assignment/escalation | No (read-only) |
| Nerve signal (proposal) | `action_intent.py` → `supervisor_action_intent.schema.json` | No |
| Approval gate (conscience) | `approval_gate.py` (reads `approval_inbox/`) | No — reads only |
| Lock layer (proprioception) | `lock_layer.py` (reads `locks/`) | No — reads only |
| Arm (dispatch chokepoint) | `action_dispatcher.py` | Only when all gates pass |
| Hands/fingers (effectors) | `scripts/write-worker-heartbeat.ps1`, `claim-packet-lock.ps1`, `assign-next-queue-item.ps1`, `mark-queue-item-done.ps1`, `release-packet-lock.ps1` | Yes |
| Cycle (single pass) | `night_supervisor_loop.py` | Orchestrates the above |

## 3. The 10 steps and their status

1. ✅ Wire contract — `schemas/aios/orchestration/supervisor_action_intent.schema.json`.
2. ✅ Brainstem emits intents — `action_intent.build_action_intents` + `supervisor_engine` now returns `action_intents`.
3. ✅ Approval gate — `approval_gate.py`, fail-closed, read-only.
4. ✅ Lock layer — `lock_layer.py`, read-only conflict detection.
5. ✅ Dispatcher (the arm) — `action_dispatcher.py`, six AND-ed gates.
6. ✅ Effector wrapping — dispatcher refuses if no PowerShell runtime (no silent no-op success); each effector maps 1:1 from the catalog.
7. ✅ Supervised loop — `night_supervisor_loop.py` single-pass cycle.
8. ⏳ Scheduling — wire the cycle into the approved scheduler/`Invoke-AiOsOvernightCollect` cadence with a hard per-pass stop (operator task on the Windows runtime).
9. ⏳ Telemetry receipts + rollback — receipts are emitted in-report today; append-only persistence + rollback handle is the next APPLY packet.
10. ✅ Graduated enable — `--ladder-through` / `--enable` allowlist; default empty = all blocked.

## 4. Enablement runbook (Human Owner only, on the Windows runtime)

The dispatcher executes a hand-script **only when all six gates pass at once**:
`kill_switch_clear`, `effector_actionable`, `capability_allowed`,
`execution_enabled`, `env_apply_armed`, `approved`, `lock_clear`.

```powershell
# 0. Dry cycle — verify proposals look right. Executes nothing.
python services\python_supervisor\night_supervisor_loop.py --repo-root . --pretty

# 1. Drop a Human-Owner approval record for each packet you bless into
#    automation\orchestration\approval_inbox\*.json
#    (approval_status: APPROVED, approved_by_human: true)

# 2. Arm the environment (per session, never committed):
$env:AIOS_SUPERVISOR_APPLY = "1"

# 3. Enable ONE rung of the ladder and apply:
python services\python_supervisor\night_supervisor_loop.py `
    --ladder-through heartbeat --apply --pretty

# Kill switch — overrides everything, instantly:
$env:AIOS_NIGHT_SUPERVISOR_DISABLE = "1"
```

Recommended graduation: `heartbeat` → `claim_lock` → `assign` → `mark_done`
→ `release_lock`, one night per rung, reviewing each morning brief before the
next rung.

## 5. Boundaries that remain hard

- No live trading, no broker/OANDA/secrets/credentials paths — ever, from here.
- Commit/push/merge are **not** dispatcher effectors; they stay with the
  human-invoked `Run-AiOsOperatorLoop.APPLY.ps1`.
- The Campaign Registry stays `PLANNING_AUTHORITY_ONLY`; this wiring does not
  grant it apply authority.
- Default state on a fresh checkout is fully blocked: no approvals, empty
  capability allowlist, execution disabled.
