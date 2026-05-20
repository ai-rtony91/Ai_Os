> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS_V2 authority. Current operating authority is `AGENTS.md`; current V2 front-door/context authority is `README.md`; current source-of-truth mapping lives under `docs/governance/`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved V2 canonical document explicitly promotes them.

# Safe APPLY Checklist

Use this before any APPLY.

- Confirm the user approved APPLY.
- Confirm the target folder or files are exact.
- Confirm no dashboard files are edited unless dashboard paths are named.
- Confirm no connector or API code is edited unless approved.
- Confirm no secrets, tokens, API keys, credentials, or recovery keys are touched.
- Confirm no broker, OANDA, live trading, real webhook, or real order path is enabled.
- Confirm no files are deleted, moved, or renamed.
- Confirm no installs are run.
- Confirm validation steps are listed.
- Confirm the commit package is one focused topic.
- Confirm `git add .` is not used.
- Confirm commit and push require separate approval.

If any item is unclear, stop and return to DRY_RUN.
