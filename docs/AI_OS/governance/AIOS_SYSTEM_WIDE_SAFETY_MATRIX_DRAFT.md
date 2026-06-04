> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AIOS System-Wide Safety Matrix Draft

Status: Draft planning doc

## Purpose

Define a single draft matrix for AI_OS safety boundaries.

## Safety Matrix

| Area | Rule | Default |
| --- | --- | --- |
| Secrets | Do not add secrets, keys, tokens, credentials, or recovery keys | BLOCKED |
| Broker execution | Do not connect live brokers or place trades | BLOCKED |
| Destructive repair | Do not delete, move, rename, overwrite, reset, or clean automatically | BLOCKED |
| Protected governance | Do not modify protected root governance files without explicit approval | BLOCKED |
| Workflow | DRY_RUN before APPLY | REQUIRED |
| Approval | Human approval before protected actions | REQUIRED |

## Boundary

This draft does not modify protected root governance files and is not canonical until approved in a later promotion workflow.
