# AI_OS Operator Consolidation Status

Status:
Legacy scripts copied into the canonical repo for review.

Imported:
- MorningLaunch.LEGACY.ps1
- AM_workflow.LEGACY.ps1
- TradeMode.LEGACY.ps1

Not imported:
- Deploy-AIOS.DISABLED.ps1 remains disabled because it contains unsafe auto deploy, auto add, auto commit, and auto push behavior.

Rules:
- Legacy imports are reference copies only.
- Do not run legacy imports directly.
- Build clean governed replacements from these patterns.
- Use DRY_RUN first.
- Keep human approval before APPLY, commit, push, deploy, network changes, or trading execution.

Next Build Target:
Create a governed Morning Boot v2 using the useful window layout logic without old repo paths or unsafe deployment behavior.
