# Codex Work-Packet Sequence — Close the Bridged Autonomy Loop

Drafted by Claude (overwatch). Dispatch in order. Each packet is one Codex lane,
one branch/worktree, one task. DRY_RUN first; Anthony approves every APPLY.

Critical path to a closed loop = Packet 1 → Packet 3.
Packets 2/4/5 make it visible. Packets 6–8 make it durable.

---

## SHARED SAFETY PREAMBLE (paste at the top of every packet)

```
You are Codex, a scoped repo worker for AI_OS_V2 (repo: ai-rtony91/Ai_Os).
Rules you must obey:
- DRY_RUN before APPLY. Show the full diff/preview first. Do not APPLY until told.
- Touch ONLY the allowed paths listed. Anything outside = STOP and report.
- Never git add ., never commit, never push, never merge/reset/clean/delete branches.
- Never touch broker, OANDA, wallet, secrets, .env, credentials, deployments, or live trading.
- Never create a scheduled task or background service unless the packet explicitly authorizes it.
- Preserve Protected Action Gate flags; never downgrade a blocker to auto.
- If you hit any ultimate blocker, STOP and write an approval item; do not work around it.
- One lane, one task, one output. Report what you did and did NOT do.
```

---

## PACKET 1 — Track the live relay runner  [FOUNDATIONAL — DO FIRST]

```
<SAFETY PREAMBLE>

TASK: The script that writes relay/logs/runner.log and relay/logs/night.log is
not in version control. Find it, bring it under git, and document it — with NO
behavior change.

STEPS:
1. Locate the untracked script driving the relay cycle (writes runner.log / night.log,
   does goal-intake -> handoffs -> packetize -> inbox -> done).
2. Move/copy it into automation/orchestration/relay/ with a clear name
   (e.g. Invoke-AiOsRelayRunner.ps1). Keep behavior byte-for-byte identical.
3. Add a header doc block: purpose, inputs, outputs, tier rules.
4. Write docs/governance/RELAY_RUNNER.md: one page — what it reads, what it writes,
   tier definitions (TIER_0_AUTO etc.), and the standing safety rule.

ALLOWED PATHS: automation/orchestration/relay/, docs/governance/
FORBIDDEN: any behavior change, any path outside those, commit/push.
OUTPUT: DRY_RUN diff of the tracked script + RELAY_RUNNER.md for review.
DONE = Anthony has reviewed the diff. (Anthony performs the commit.)
```

---

## PACKET 2 — Bridge ingests Operation Glue + approval queue

```
<SAFETY PREAMBLE>

TASK: services/python_supervisor/autonomy_bridge.py is blind to Operation Glue.
Make the bridge see Glue state so it reaches dashboard_cards and must_see.

STEPS:
1. In collect_source_files(), add patterns for:
   - control/operation_glue/ (*.json)
   - telemetry/operation_glue/ (**/*.json)
2. Ensure Glue approval-inbox items classify as NEEDS_APPROVAL and surface in must_see.
3. Update/extend the bridge test to assert a Glue approval item appears in must_see.
4. Keep module local-only, stdlib-only, evidence-only. No new write targets.

ALLOWED PATHS: services/python_supervisor/autonomy_bridge.py and its test file.
FORBIDDEN: new write targets, network, shell, git writes, classification of
           Glue items as PASS when blocked_count > 0.
OUTPUT: updated module + passing test. Run Test-AiOsAutonomyBridge.DRY_RUN.ps1 green.
DONE = test green + DRY_RUN receipt shows Glue items. Anthony approves.
```

---

## PACKET 3 — Approval -> Resume executor  [THE LOOP-CLOSER — HIGHEST RISK]

```
<SAFETY PREAMBLE>

TASK: Today an approved decision goes nowhere — the loop is a "U", not an "O".
Build a DRY_RUN executor that turns an APPROVED decision back into queued work.
It RE-QUEUES only; it NEVER performs the approved action itself.

STEPS:
1. Create automation/orchestration/approval_runner/Invoke-AiOsApprovedActionResume.DRY_RUN.ps1
2. Read relay/approvals/approved/ . For each approved item:
   - find its original blocked packet/handoff (match by id/slug),
   - build a "resume packet" preview destined for relay/inbox/.
3. DRY_RUN (default): print the approved->resume mapping. Write NOTHING.
4. -Apply: write resume packets into relay/inbox/ ONLY. Nothing else.
5. If an approved item has no matching origin packet -> STOP, list it as unresolved.

ALLOWED PATHS: automation/orchestration/approval_runner/;
               write relay/inbox/ ONLY when -Apply is passed.
FORBIDDEN: executing the approved action, any git op, any protected action,
           writing outside relay/inbox/. This script re-queues, never performs.
OUTPUT: DRY_RUN mapping table for Anthony to review the matching logic.
DONE = matching logic reviewed and trusted before any -Apply. THIS IS THE RISKY ONE.
```

---

## PACKET 4 — Dashboard reads live bridge state

```
<SAFETY PREAMBLE>

TASK: apps/dashboard still reads mock-data/*.sample.json. Point it at the real
bridge output, with graceful fallback.

STEPS:
1. Read telemetry/night_supervisor/AUTONOMY_BRIDGE_STATE.json when present.
2. Fall back to the existing .sample.json when the live file is missing.
3. Render dashboard_cards (status, plain_summary, metrics, next_action).
4. No backend/runtime changes; no new network calls.

ALLOWED PATHS: apps/dashboard/
FORBIDDEN: runtime/services changes, new network calls, git writes.
OUTPUT: DRY_RUN screenshot or diff showing live data + fallback path.
DONE = Anthony confirms live card renders.
```

---

## PACKET 5 — Blocker alert / digest delivery

```
<SAFETY PREAMBLE>

TASK: Doctrine promises "Anthony is alerted only when a blocker is hit," but the
morning digest is just written to disk. Add the simplest possible alert sink.

STEPS:
1. When the bridge/night cycle produces status = BLOCKED (or NEEDS_APPROVAL),
   write relay/reports/ALERT_LATEST.md summarizing the blocker(s) + next safe action.
2. No external channels yet (no email/SMS/webhook) — local file only.

ALLOWED PATHS: automation/orchestration/night_supervisor/; write relay/reports/.
FORBIDDEN: email/SMS/webhook/any external service (separate future approval),
           git writes, protected actions.
OUTPUT: DRY_RUN preview of ALERT_LATEST.md content.
DONE = Anthony approves the local alert behavior.
```

---

## PACKET 6 — Real scheduler trigger  [SEPARATE APPROVAL — ULTIMATE BLOCKER]

```
<SAFETY PREAMBLE>

NOTE: A scheduled task is an ULTIMATE BLOCKER under AI_OS doctrine. This packet
only PROPOSES the trigger. Creating the actual scheduled task requires a distinct,
explicit Anthony approval — do NOT register it yourself.

TASK: Turn Invoke-AiOsSchedulerPreview.DRY_RUN.ps1 into a concrete, reviewable
proposal for a nightly trigger of the relay runner.

STEPS:
1. Produce the exact scheduled-task definition (command, trigger time, working dir)
   as a preview/spec file. Do NOT register it.
2. Document rollback (how to remove it) in the same spec.

ALLOWED PATHS: automation/orchestration/scheduler/
FORBIDDEN: registering/creating/enabling any scheduled task or service, git writes.
OUTPUT: DRY_RUN task spec + rollback doc.
DONE = Anthony reviews; registration is a separate explicit approval.
```

---

## PACKET 7 — Unify the three approval stores

```
<SAFETY PREAMBLE>

TASK: There are 3 approval representations: relay/approvals/*.md|json,
control/operation_glue/APPROVAL_INBOX.json, and
services/python_supervisor/approval_queue.py. Define ONE canonical queue and a
read adapter for the others. Migration is preview-only.

STEPS:
1. Propose one canonical schema + location for approval items.
2. Build a DRY_RUN projector that reads all three and emits the unified view.
3. Do NOT delete or move the existing stores yet — projection only.

ALLOWED PATHS: services/python_supervisor/, automation/orchestration/approval_runner/
FORBIDDEN: deleting/overwriting existing approval files, git writes.
OUTPUT: DRY_RUN unified approval view + migration proposal doc.
DONE = Anthony approves the canonical design before any migration.
```

---

## PACKET 8 — Harden bridge classification

```
<SAFETY PREAMBLE>

TASK: autonomy_bridge.py classifies status by fragile substring matching
("place a buy order", "live now"). Replace with explicit status fields.

STEPS:
1. Define an explicit status/risk field contract for packets and approval items.
2. Make classify_item() prefer the explicit field; keep substring matching only
   as a last-resort fallback that defaults to the SAFER status (never downgrade).
3. Extend tests with cases that previously misclassified.

ALLOWED PATHS: services/python_supervisor/autonomy_bridge.py + test, schemas/aios/
FORBIDDEN: behavior that downgrades a blocker to PASS, git writes.
OUTPUT: updated module + tests proving safer classification.
DONE = tests green; Anthony approves.
```
