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
