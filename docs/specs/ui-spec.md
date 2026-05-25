# AI_OS UI Spec (V1)

Status: canonical spec
Source: legacy `docs/specs/ui-spec.md`
See also: `docs/specs/aios-dashboard-data-contracts.md` (canonical data contract)
See also: `docs/concepts/aios-visual-identity.md` (visual direction)
See also: `docs/concepts/aios-dashboard-and-interface-concepts.md` (concept boundary)

## Purpose

The AI_OS UI is the operator control plane: governance visibility, approval
management, validator status, packet tracking, worker status, and
orchestration oversight.

The UI must remain read-only by default. It must not execute APPLY, trigger
commits, connect brokers, place trades, access credentials, or enable live
trading.

For data contract details see: `docs/specs/aios-dashboard-data-contracts.md`
For visual direction see: `docs/concepts/aios-visual-identity.md`

---

## Form Factor

Web dashboard (browser) — V1.

---

## Canonical Status Labels

UI status labels must match the canonical data contract. Do not invent
new status labels.

| Label | Meaning |
|---|---|
| `PASS` | Check passed, evidence confirmed |
| `WARN` | Caution — operator review recommended |
| `FAIL` | Check failed — execution blocked |
| `UNKNOWN` | Evidence absent, partial, or unverified |
| `STALE` | Source present but not recently verified |
| `BLOCKED` | Cannot proceed — approval or validator required |
| `COMPLETE` | Work unit finished |
| `PENDING_APPLY` | Awaiting Human Owner APPLY approval |
| `INVALID DATA` | JSON parse failure or conflicting evidence |
| `REVIEW REQUIRED` | Human Owner review required before advancing |
| `DRY_RUN` | Inspection mode — no mutations |
| `APPLY` | Mutation mode — approved file edits |

---

## Screens (V1)

### 1. Dashboard

- Current mode indicator: `DRY_RUN` or `APPLY`
- System status: `PASS / WARN / FAIL / UNKNOWN / BLOCKED`
- Git branch and clean/dirty state
- Active packet list with status per packet
- Active worker list with zone (`EAST` / `WEST`) and lock status
- Validator health summary: PASS / WARN / FAIL counts
- Pending approvals count
- Next safe action (source-backed — not inferred)
- Protected files status

### 2. Workflow / Packet View

- Pipeline stage timeline:
  `PROPOSED -> QUEUED -> ASSIGNED -> DRY_RUN -> VALIDATOR_RUN ->
   DRY_RUN_COMPLETE -> APPROVAL_REQUESTED -> APPROVED -> LOCK_CLAIMED ->
   APPLY -> DONE / BLOCKED`
- Each stage shows: zone, worker, action, status, timestamps, output
- Validator chain results per stage: validator_id, state, order
- Lock status per packet: lock_id, claimed_paths, status
- Stop point display

### 3. Approvals

- Approval inbox entries from `automation/orchestration/approval_inbox/`
- Per entry: packet_id, requested action, risk level, approval state
- Approve / Deny — Human Owner action only
- Reason required for Deny
- Blocked actions list displayed per entry

### 4. Validator Health

- Per validator: validator_id, label, order, state, command
- Overall chain status: PASS / WARN / FAIL / BLOCKED
- Any FAIL — dashboard shows BLOCKED
- Any WARN — dashboard shows REVIEW REQUIRED
- PASS with zero validators — INVALID DATA

### 5. Logs

- Filter by packet_id / worker_id / zone
- Timestamped entries
- audit_id per entry
- Plain text first (no charts in V1)

### 6. Worker Status

- Worker registry from `automation/orchestration/workers/`
- Per worker: worker_id, zone (EAST/WEST), lane, assigned packet, lock status
- Lock registry status from `automation/orchestration/locks/`

---

## Layout

```
Top bar:    current mode (DRY_RUN/APPLY) | git branch | system status | emergency stop
Left nav:   Dashboard / Packets / Approvals / Validators / Workers / Logs / Settings
Main:       selected view
Right panel: inspector — packet details, validator results, lock status,
             approval actions, raw logs
```

---

## Visual Direction

Follow `docs/concepts/aios-visual-identity.md`:

- Deep space / midnight background
- Neon blue and violet glow indicators
- High-contrast dark UI
- Clean card-based layout
- Strong visual hierarchy
- BLOCKED and FAIL states use red/amber indicators
- PASS states use blue/green indicators

---

## Non-Goals (V1)

- Voice UI
- Drag/drop builders
- Multi-user RBAC UI (future)
- Live broker integration (permanently blocked unless separate governance approves)
- Dashboard-triggered APPLY (future, approval-gated only)
- AI assistant panel with live API connection (future)

---

## Safety Boundaries

The UI must stay:

- Read-only by default — no dashboard-triggered APPLY in V1
- Fixture-only until approved live sources exist
- Explicit about DRY_RUN vs APPLY mode at all times
- Explicit about UNKNOWN, STALE, INVALID DATA, BLOCKED states
- Free of credentials, API keys, broker data, live market data

Out of scope permanently unless separate governance change approves:

- Live broker execution
- OANDA or broker account connections
- Real webhooks or real orders
- Live trading panel
- Credential entry forms

---

## Standardization

- Status labels must match the canonical label set above — no custom labels
- UI follows the packet pipeline stage order exactly
- All displayed actions require an `audit_id`
- Approvals must block execution — the UI must never imply an action
  is approved when it is not
- DRY_RUN and APPLY must be visually distinct at all times
- Missing data is `UNKNOWN` — never displayed as `PASS` or empty
