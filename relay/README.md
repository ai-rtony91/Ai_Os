# AI_OS Relay — Mailroom Layer 3.5

Temporary, file-based transport so Anthony stops being a courier between
ChatGPT, Claude, Codex, GitHub, PowerShell, and reports. Drop a task in
`inbox\`, get a report in `outbox\`. No screen scraping, no autoclickers,
no browser automation — just files moving through folders.

This is **scaffolding**. AI_OS replaces it once it can self-build.

## The flow

```
inbox\ -> running\ -> outbox\ (report) -> done\        (success)
                                       -> error\ + approvals\ (blocked/failed)
```

## Folders

| folder       | meaning                                         |
|--------------|-------------------------------------------------|
| inbox\       | drop `*.task.txt` / `*.task.json` here          |
| running\     | file lives here while a worker processes it     |
| outbox\      | worker reports land here                        |
| done\        | task file after success                         |
| error\       | task + `.error.txt` after failure               |
| approvals\   | blocker alerts that need Anthony's sign-off     |
| reports\     | daily roll-ups and night-supervisor reports     |
| logs\        | append-only `runner.log` / `night.log`          |
| packets\     | reusable task templates                         |
| handoffs\    | worker-to-worker handoff packets                |

## Task format

**Plain text** `*.task.txt` — body is the prompt. Filename starting with
`claude-` routes to Claude; otherwise Codex.

**JSON** `*.task.json`:
```json
{ "id": "task-001", "worker": "codex", "mode": "exec",
  "prompt": "the instructions", "context": ["C:\\path\\file"], "output": "text" }
```

## One-drop goal flow (easiest path)

Write a plain goal — no packets, no worker choice, no handoff authoring:

```powershell
'Build a validator for worker packet ownership.' |
  Out-File relay\goals\my-goal.goal.txt -Encoding utf8
```

With the watcher running (`relay-runner.ps1 -Watch`), the relay does the rest:

```
goals\*.goal.txt
  -> goal-intake.ps1   (decides who/what/worker/approval level)
  -> handoffs\*.handoff.json
  -> packetize.ps1     -> inbox\*.task.json
  -> relay-runner.ps1  -> outbox\*.report.txt -> done\
```

Routing the intake applies automatically:
- analyze verbs (review/inspect/audit/plan…)  -> Claude plan only      (TIER_0)
- build verbs (build/create/fix/wire…)         -> Claude plan + Codex   (TIER_1)
- blocker words (commit/push/trade/secret/merge/delete…) -> STOP, write
  an approval packet only, NO worker packet                            (TIER_2)

## Run it

Safe by default (DRY_RUN — no model is called, only plumbing moves):
```powershell
pwsh -File relay\relay-runner.ps1            # one pass, dry run
pwsh -File relay\relay-runner.ps1 -Report    # write today's summary
pwsh -File relay\relay-runner.ps1 -Watch     # follow inbox\ (dry run)
```

Go live (real `codex` / `claude` calls) only when you're ready:
```powershell
pwsh -File relay\relay-runner.ps1 -Live          # one live pass
pwsh -File relay\relay-runner.ps1 -Live -Watch   # live, follow inbox\
```

## Safety / blocker gates

The runner refuses to execute any task containing words like `trade`, `order`,
`buy`, `sell`, `broker`, `oanda`, `api key`, `secret`, `git commit`, `merge`,
`rebase`, `delete`. Such tasks go to `error\` and an item is written to
`approvals\` with a plain-English reason and the exact proposed action. Nothing
runs until you move that file to `approvals\approved\`.

The relay only ever writes inside `relay\`. It never commits, pushes, merges,
deletes, or overwrites repo source.

## Night Supervisor

```powershell
pwsh -File relay\night-supervisor.ps1            # inspect + report only
pwsh -File relay\night-supervisor.ps1 -Apply     # also create missing relay folders
```

Reads the repo, sorts the relay, detects stale/duplicate/dirty state, and writes
a report. Any risky condition (dirty tree, needed commit) produces an approval
item instead of acting.

### Night Supervisor Goal Feeder

The Night Supervisor is a safe **goal creator**, not an executor. It never calls
Codex/Claude directly and never writes results. With `-GenerateGoals` it writes
plain goal files into `relay\goals\`; the normal relay chain takes it from there.

```powershell
pwsh -File relay\night-supervisor.ps1                  # report-only (no goals)
pwsh -File relay\night-supervisor.ps1 -GenerateGoals   # write safe goals
pwsh -File relay\relay-runner.ps1                      # process the goals
```

Flow:
```
night-supervisor.ps1 -GenerateGoals
  -> relay\goals\night-<ts>-*.goal.txt
  -> goal-intake -> handoffs -> packetize -> inbox -> runner -> outbox result
  -> approvals catches anything risky
```

Each goal is classified before it is written:
- **GREEN**  read-only summary/checks ....... auto-created
- **YELLOW** relay-only packets/reports ...... auto-created
- **ORANGE** suggests a future change ........ approval only
- **RED**    source change outside relay ..... approval only
- **BLACK**  commit/push/merge/delete/trade/secret/etc. ... approval only

Only GREEN/YELLOW are auto-created; everything else (and anything uncertain)
becomes an approval item in `relay\approvals\` with reason, proposed action, and
a "no action taken" statement. Generated goals are also re-checked by goal-intake,
so a blocker word is caught twice.

**Why this reduces copy/paste:** overnight, Anthony no longer hand-writes
maintenance packets. The supervisor proposes safe goals, the relay turns them
into worker results, and only genuine decisions surface as approvals. Anthony
reads outbox results and approvals in the morning instead of authoring packets.

Still blocked (always): commits, pushes, merges, rebases, deletes, scheduled
tasks, background services, source edits outside `relay\`, trading/broker/OANDA,
API keys, and secrets.
