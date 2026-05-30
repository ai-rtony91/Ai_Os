# Relay Packet Formats (Mailroom Layer 3.5)

Three packet types move work through the relay with zero manual copy/paste.
All are JSON so scripts can read them; all carry the same `id` so a goal can be
traced end to end.

```
handoffs\*.handoff.json   (Claude writes)   --packetize.ps1-->  inbox\*.task.json
inbox\*.task.json         (runner consumes) --relay-runner.ps1->  outbox\*.result.json
                          (on blocker)      ------------------->  approvals\*.approval.json
```

## 1. HANDOFF packet  — `handoffs\<id>.handoff.json`
Produced by Claude (or any planner). Says *what* to do and *who* should do it.
The relay turns it into a runner task automatically; Anthony never copies it.

```json
{
  "packet": "handoff",
  "id": "h-001",
  "from": "claude",
  "to": "codex",
  "mode": "exec",
  "lane": "relay-demo",
  "allowed_paths": ["relay/"],
  "forbidden_paths": ["outside relay/"],
  "goal": "One plain-language objective.",
  "prompt": "The exact instructions Codex executes.",
  "context": [],
  "stop_condition": "When the result packet is written.",
  "approval_required": false
}
```

## 2. RESULT packet — `outbox\<id>.result.json`
Produced by the worker (Codex/Claude) via the runner. Says *what happened*.

```json
{
  "packet": "result",
  "id": "h-001",
  "worker": "codex",
  "status": "success",
  "files_changed": [],
  "summary": "What was done, plain language.",
  "validation": "PASS | FAIL | n/a",
  "blockers": [],
  "next_safe_action": "What Anthony can do next."
}
```

## 3. APPROVAL packet — `approvals\<id>.approval.json`
Produced when a blocker is hit. Work STOPS; Anthony decides.

```json
{
  "packet": "approval",
  "id": "h-002",
  "raised_by": "relay",
  "risk": "HIGH",
  "reason": "Plain-English why this stopped.",
  "proposed": "Exact command or change that is blocked.",
  "needs": "What Anthony must approve.",
  "status": "WAITING"
}
```

## The operator loop (success criteria)
1. Anthony drops ONE handoff packet (or a plain goal) into `handoffs\`.
2. `packetize.ps1` converts it to an `inbox\` task.
3. `relay-runner.ps1` runs it → `outbox\<id>.result.json`.
4. Anthony reads ONE result file. No manual relaying between Claude and Codex.
