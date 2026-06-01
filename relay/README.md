# AI_OS Relay

The relay is the local file bridge between AI_OS planning and worker execution.

## Worker

`automation/orchestration/relay/Invoke-AiOsRelayRunner.ps1` is the intake side. It reads goals and handoffs, classifies risk, and creates task packets in `relay/inbox/`.

`automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1` is the execution side. It polls `relay/inbox/`, moves one `*.task.json` packet at a time through `running/`, and finishes in `done/` or `error/` with a report in `outbox/`.

This is a universal AI_OS relay bridge. Claude is the current tested default provider for TIER_0 acceptance tests, but the architecture is provider-neutral. OpenAI/ChatGPT support is planned through explicit provider configuration, not hardcoded API calls. Codex and custom providers can be added later when their commands, arguments, authentication model, and safety rules are scoped.

Provider-aware task fields:

```json
{
  "id": "task-001",
  "worker": "claude",
  "provider": "claude",
  "provider_command": "claude",
  "provider_args": ["--permission-mode", "plan", "--output-format", "text"],
  "tier": "TIER_0_AUTO",
  "mission": "Read-only relay inspection.",
  "allowed_paths": ["relay/"]
}
```

If `provider` is omitted, the worker defaults it from `worker`. Current built-in defaults are:

- `claude`: `claude --permission-mode plan --output-format text`
- `codex`: `codex exec --sandbox workspace-write -`
- `openai`: reserved; requires an explicit `provider_command` before dispatch
- `custom`: reserved; requires an explicit `provider_command` before dispatch

Unknown providers, missing provider commands, or provider commands containing blocked shell metacharacters fail safely into `relay/error/` before any CLI call.


### Worker Cost Ledger

Successful APPLY worker invocations append `control/mode/cost_ledger.jsonl` after the provider command returns. The worker uses `AIOS_CYCLE_ID` when present and falls back to a UTC date cycle id when it is not set. If provider output does not expose parseable cost or token usage, the worker records a conservative nonzero estimate with `estimated=true` and `estimate_reason=fallback_nonzero_worker_invocation` so the existing cost ceiling can still fail closed.
### Worker Safety Shields

The worker now starts with a local tool preflight for `codex`, `claude`, `gh`, and `git`. Missing tools or version-check failures log `PREFLIGHT_FAILED` and exit code `2` before packet execution.

Provider CLI calls run through `automation/orchestration/timeout/Invoke-AiOsCliWithTimeout.ps1`. A hung command is killed after `timeout_sec` from the packet, or 600 seconds by default, and the packet moves to `relay/error/` with `WORKER_TIMEOUT`.

Successful worker exits are checked by `automation/orchestration/validators/output/Test-AiOsWorkerOutput.DRY_RUN.ps1` before `running/` advances to `done/`. Files written outside `allowed_paths`, or writes to protected paths such as `AGENTS.md`, `RISK_POLICY.md`, `.git/`, or `.codex_backups/`, fail closed into `relay/error/`.

Run one dry-run pass:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1 -MaxPackets 1
```

Run the worker loop in dry-run mode:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1 -Watch -IntervalSeconds 5
```

Run real CLI dispatch for bounded packets:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay/Invoke-AiOsRelayWorker.ps1 -Apply -MaxPackets 1
```

Read results:

- `relay/outbox/{id}.report.txt` has worker stdout, stderr, provider, provider command, exit code, timing, and allowed paths.
- `relay/done/` holds successful original packets.
- `relay/error/` holds malformed packets or packets whose worker exited non-zero.
- `relay/approvals/` holds packets that require Human Owner approval.
- `relay/logs/runner.log` records every transition with UTC timestamps.
- `relay/reports/{YYYY-MM-DD}-summary.md` is written with `-Report`.

TIER_2 is a hard stop. If a packet declares `TIER_2`, reclassifies as `TIER_2`, or contains protected terms such as commit, push, broker, OANDA, webhook, or live trading, the worker moves it to `relay/approvals/` before any CLI call.

Packet 11 should run only after provider-neutral relay validation passes in the same environment that will launch the worker.

Kill switch:

```powershell
New-Item -ItemType File -Path relay/STOP.flag -Force
```

At the top of each poll loop, the worker exits cleanly when `relay/STOP.flag` exists. Delete the file before starting the next worker run.
