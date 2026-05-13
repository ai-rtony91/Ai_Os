# AI_OS Morning Boot v2

Purpose:
Governed AI_OS startup orchestration layer.

Status:
DRAFT_V2

Rules:
- No auto push.
- No auto deploy.
- No broker execution.
- No live trading.
- No git add -A.
- DRY_RUN-first workflow.
- Human approval required before APPLY/commit/push/deploy.

Startup Sequence:
1. Validate canonical repo path.
2. Validate git branch.
3. Validate git status.
4. Open operator PowerShell windows.
5. Open DevOps workspace.
6. Open Trading Lab workspace.
7. Open ChatGPT.
8. Open TradingView.
9. Load telemetry/reporting context.
10. Load operator policies.

Planned Future Features:
- worker numbering
- codex worker orchestration
- workspace profiles
- ultrawide layouts
- monitor-aware positioning
- operator telemetry startup
- startup validation gates
- Cloudflare tunnel validation
- Azure environment validation
- local AI_OS dashboard boot
