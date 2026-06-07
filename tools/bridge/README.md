# AI_OS Dual-Review Bridge — User Guide

**What it is:** the bridge that ends the copy-paste loop. You give it a goal once.
It runs **Codex** (the coder), sends Codex's report to **ChatGPT and Claude** for a
cross-checked second opinion, reconciles them into one next instruction, **buzzes
your phone (ADB SOS)**, and **stops for your decision**. You say go — it loops.
No more pasting between Codex and ChatGPT.

```
  YOU give a goal
        │
        ▼
   ┌─► Codex does the work ──► report
   │                              │
   │        ┌──────── ChatGPT review ─┐
   │        ├──────── Claude review ──┤  (cross-reference)
   │        └──── reconcile → ONE next step
   │                              │
   │   📱 ADB SOS wakes your phone │
   │        ⏸  STOPS for YOU ──────┘
   └──── you press [a]pprove / [e]dit / [q]uit
```

---

## Before first run (one time)

1. **Codex CLI** installed and on PATH:
   ```
   npm install -g @openai/codex      # needs Node 22+
   codex --version                   # confirm it works
   ```
2. **API keys** in your PowerShell session (values are never logged or printed):
   ```powershell
   $env:OPENAI_API_KEY    = "sk-..."
   $env:ANTHROPIC_API_KEY = "sk-ant-..."
   ```
3. (Optional) **ADB SOS** already works in your repo — nothing to set up. To run
   *without* buzzing your phone, add `-NoSos`.

---

## Run it

```powershell
.\tools\bridge\Invoke-DualReviewBridge.ps1 -Goal "Fix the failing forex backtest adapter tests"
```

Each round prints Codex's report, both reviews, and the reconciled next step,
then waits:

```
Decision -> [a]pprove & continue | [e]dit next instruction | [q]uit
>
```

- **`a`** → run Codex on the reconciled instruction (next round).
- **`e`** → type your own next instruction instead.
- **`q`** → stop now.

That's the whole workflow: **approve, approve, approve… done.**

---

## Options

| Flag | Default | What it does |
|------|---------|--------------|
| `-Goal` | *(required)* | The engineering goal. |
| `-Repo` | `C:\Dev\Ai.Os` | Working dir Codex runs in. |
| `-MaxRounds` | `10` | Safety cap on rounds. |
| `-CodexCmd` | `codex exec` | Headless Codex command. |
| `-OpenAiModel` | `gpt-5.1` | The "ChatGPT" reviewer model. |
| `-AnthropicModel` | `claude-sonnet-4-6` | The "Claude" reviewer model. |
| `-NoSos` | off | Don't fire the ADB SOS wake. |

> If `gpt-5.1` / `claude-sonnet-4-6` aren't the exact model strings on your
> account, pass the right ones with `-OpenAiModel` / `-AnthropicModel`.

---

## What it logs

- **Every round** → `telemetry/operator_relief/dual_review_rounds.jsonl`
  (goal, instruction, Codex report tail, both reviews, reconciled next step).
- **Each approval prompt** → your existing operator-relief notification log via
  `notification_gate` (classification `approval_needed`), which also fires the
  ADB SOS wake.

---

## Boundaries (by design — matches AI_OS governance)

- **You stay approval authority.** It stops *every* round. It never auto-continues.
- **ADB SOS only** for the wake. No Telegram / Tasker.
- It **never commits, pushes, merges, or writes protected paths.** It only runs
  Codex (which has its own sandbox/approvals) and asks the two reviewers.
- **Secrets are presence-checked only** — never read, printed, or logged.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Missing required API key(s)` | Set `$env:OPENAI_API_KEY` / `$env:ANTHROPIC_API_KEY` in *this* session. |
| `[codex launch error … on PATH?]` | Install the Codex CLI / open a new shell so PATH refreshes. |
| Reviewer says `[skipped: … not set]` | That key isn't set in this session. |
| `[OpenAI/Claude reviewer error …]` | Bad/expired key, wrong model string, or no internet. |
| Phone didn't buzz | Check `logs\android\adb_sos_wake.log`; confirm the phone's ADB target is reachable. Use `-NoSos` to run without it. |

---

## Tip

Keep goals **bounded** ("fix these tests", "add validation to X", "refactor Y").
The bridge shines on focused, iterative work where the cross-review catches what
a single agent misses — and you stay in the driver's seat the whole way.
