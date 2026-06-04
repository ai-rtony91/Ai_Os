> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AIOS Recovery Workflow Draft

Status: Draft planning doc
Stage: 12.9

## Workflow

1. Stop current action.
2. Capture error.
3. Identify affected files.
4. Read latest checkpoint.
5. Propose recovery DRY_RUN.
6. Wait for approval.

## Boundary

Recovery does not delete, reset, or overwrite automatically.
