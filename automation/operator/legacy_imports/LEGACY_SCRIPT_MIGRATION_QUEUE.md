# AI_OS Legacy Script Migration Queue

Purpose:
Track old operator scripts discovered during consolidation audit.

Discovered Legacy Scripts:
- C:\Scripts\MorningLaunch.ps1
- C:\Scripts\AM workflow.ps1
- C:\Scripts\TradeMode.ps1
- C:\Scripts\Deploy-AIOS.DISABLED.ps1

Migration Rules:
- No direct auto-push logic.
- No blind git add -A usage.
- No direct production deployment.
- All migrated scripts must support DRY_RUN-first workflow.
- Canonical repo path only:
  C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN

Planned Categories:
- workspace_profiles
- deployment_controls
- network_modes
- codex_worker_boot
- operator_layouts
- telemetry_startup
