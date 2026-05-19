# AI_OS C Drive Multi-Clone Workflow

GitHub `main` remains the source of truth.

OneDrive is not the source of truth for multi-worker collaboration.

## Recommended Local Layout

```text
C:\AI_OS\
  main-clean\
  your-work\
  friend-work\
  staging-review\
  telemetry\
  packets\
  workers\
  validators\
  recovery\
  logs\
  backups\
```

## Folder Roles

- `main-clean`: tracks GitHub `main` and stays clean.
- `your-work`: active branch workspace for the user.
- `friend-work`: active branch workspace for the friend.
- `staging-review`: review branches before merge.
- `telemetry`: local-only external telemetry exports if needed.
- `packets`: external packet copies if needed.
- `workers`: external worker notes if needed.
- `validators`: external validator outputs if needed.
- `recovery`: crash or reboot recovery notes if needed.
- `logs`: local logs.
- `backups`: manual backup copies only when approved.

## Branch Examples

- `feature/phase-15-telemetry-worker-core`
- `worker/user-packet-core-YYYYMMDD`
- `worker/friend-validator-core-YYYYMMDD`
- `review/staging-phase-15-worker-core`

## Rules

- Sync through GitHub branches only.
- Do not directly overwrite between clones.
- Do not file-copy merge between user and friend workspaces.
- Do not auto-merge to `main`.
- Do not use `main-clean` for experimental edits.
- Use `staging-review` for review and conflict inspection.
- Commit and push require separate explicit approval.
