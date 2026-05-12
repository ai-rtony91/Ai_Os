# Commit Package Rules

A commit package is a group of related files saved together.

Rules:

- Do not use `git add .`.
- Stage exact files or one approved folder only.
- Do not mix unrelated changes.
- Do not commit dashboard leftovers unless dashboard files are explicitly approved.
- Do not commit `.codex_backups/`.
- Do not commit secrets, tokens, API keys, credentials, private keys, or recovery keys.
- Do not commit broker or live trading activation.
- Do not commit generated junk or unknown leftovers.
- Run validation before commit.
- Push only after separate approval.

Good commit examples:

- `Add Trading Lab mock signal fixtures`
- `Add dashboard next-action mock data`
- `Add product overview docs`
- `Add read-only orchestrator validator`

Bad commit examples:

- UI, Trading Lab, product docs, and app code together.
- Dashboard leftovers plus mock strategy files.
- Connector planning plus API keys.
- Validator code plus unrelated CSS.
