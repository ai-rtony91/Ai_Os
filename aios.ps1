param(
    [ValidateSet("help","daily","morning","swarm","status","resume","workers","runtime","supervisor","mission","runner","queue","telemetry","packet","layout","control","finish-pr","hud","operator-relief","bridge")]
    [Parameter(Position=0)]
    [string]$Mode = "help",
    [string]$Goal = "Build next AIOS runtime loop step",
    [string]$MissionName = "",
    [int]$WorkerCount = 4,
    [ValidateSet("auto","compact","wide","dual-monitor")]
    [string]$Preset = "auto",
    [switch]$ApplyMission,
    [string]$MissionPath = "",
    [string]$TaskId = "",
    [string]$TaskJson = "",
    [int]$Pr = 0,
    [switch]$ShowPrompt,

    # packet command params — used with: .\aios.ps1 packet <worker> <preset>
    [Parameter(Position=1)]
    [string]$Worker = "",
    [Parameter(Position=2)]
    [string]$PacketPreset = "",
    [ValidateSet("DRY_RUN","APPLY")]
    [string]$ExecutionMode = "DRY_RUN"
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

Write-Host "AIOS SHORTCUT START" -ForegroundColor Cyan
Write-Host "Mode: $Mode"

function Show-AiOsCrewRecommendation {
    $crewHelper = "automation/orchestration/crew/Get-AiOsCrewIntegrationRecommendation.DRY_RUN.ps1"

    Write-Host ""
    Write-Host "== Crew Recommendation ==" -ForegroundColor Yellow
    Write-Host "Mode: DRY_RUN_READ_ONLY"
    Write-Host "Authority: evidence only; Human Owner approval is required before APPLY, commit, push, merge, lock, or approval changes."

    if (-not (Test-Path -LiteralPath $crewHelper -PathType Leaf)) {
        Write-Host "Crew helper: unavailable" -ForegroundColor Yellow
        Write-Host "Next safe action: continue with existing status checks; do not infer Crew readiness."
        return
    }

    try {
        $rawOutput = powershell -NoProfile -File $crewHelper -OutputJson 2>&1
        $crew = ($rawOutput | Out-String) | ConvertFrom-Json

        Write-Host "overall_readiness: $($crew.overall_readiness)"
        Write-Host "next_safe_action: $($crew.next_safe_action)"
        Write-Host "recommended_worker: $($crew.recommended_worker)"
        Write-Host "recommended_lane: $($crew.recommended_lane)"
        Write-Host "recommended_validators:"
        if (@($crew.recommended_validators).Count -eq 0) {
            Write-Host "  NONE"
        } else {
            @($crew.recommended_validators) | ForEach-Object { Write-Host "  $_" }
        }
        Write-Host "approval_summary: pending=$($crew.approval_state_summary.pending_approvals); approved=$($crew.approval_state_summary.approved_actions); blocked=$($crew.approval_state_summary.blocked_actions)"
        Write-Host "collision_warning: $($crew.collision_warning)"
        Write-Host "commit_package_preview: status=$($crew.commit_package_preview.status); git_status=$($crew.commit_package_preview.git_status); recommended_files=$($crew.commit_package_preview.recommended_file_count); risks=$($crew.commit_package_preview.risk_count)"
    }
    catch {
        Write-Host "Crew helper: failed" -ForegroundColor Yellow
        Write-Host "Reason: $($_.Exception.Message)"
        Write-Host "Next safe action: continue with existing status checks; do not infer Crew readiness."
    }
}

switch ($Mode) {
    "help" {
        Write-Host ""
        Write-Host "Available commands:"
        Write-Host ".\aios.ps1 -Mode daily    # run normal daily flow"
        Write-Host ".\aios.ps1 -Mode morning  # run morning operations intelligence"
        Write-Host ".\aios.ps1 -Mode status   # show health, next action, inbox"
        Write-Host ".\aios.ps1 -Mode resume   # resume last session"
        Write-Host ".\aios.ps1 -Mode workers  # show worker list and inbox"
        Write-Host ".\aios.ps1 -Mode swarm    # launch worker swarm"
        Write-Host ".\aios.ps1 -Mode runtime  # run goal intake + recommendation + health"
        Write-Host ".\aios.ps1 -Mode supervisor # preview supervised scheduler/runtime events"
        Write-Host ".\aios.ps1 -Mode mission -Goal ""Improve AIOS runtime automation"" # create Mission Control plan DRY_RUN"
        Write-Host ".\aios.ps1 -Mode runner # preview allowlisted command runner"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation # show next safe mission action"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -ShowPrompt # show task prompt"
        Write-Host ".\aios.ps1 -Mode queue # show command queue read-only"
        Write-Host ".\aios.ps1 -Mode telemetry # show telemetry viewer read-only"
        Write-Host ".\aios.ps1 -Mode layout  # show 5-worker terminal layout plan and banner commands"
        Write-Host ".\aios.ps1 -Mode control # show operator control loop cockpit"
        Write-Host ".\aios.ps1 -Mode finish-pr -Pr 273 # preview PR finish steps"
        Write-Host ".\aios.ps1 -Mode hud -Worker CLAUDE # preview worker HUD"
        Write-Host ".\aios.ps1 -Mode operator-relief -TaskJson .\local_task.json # run Full-Auto DRY_RUN only"
        Write-Host ".\aios.ps1 -Mode bridge -TaskJson .\reports\operator_relief\inbox\task.json # run inbox/outbox bridge"
    }

    "daily" {
        powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsDailyFlow.ps1 -RunWorkerPreview
    }
    "morning" {
    powershell -ExecutionPolicy Bypass -File automation/operator/Start-AiOsMorningOperations.ps1
    }

    "swarm" {
        powershell -ExecutionPolicy Bypass -File automation/session/Start-AiOsDailyFlow.ps1 -LaunchSwarm -RunWorkerPreview
    }

    "status" {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/recommendations/Get-AiOsActionRecommendation.DRY_RUN.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1
        Show-AiOsCrewRecommendation
    }

    "resume" {
        powershell -ExecutionPolicy Bypass -File automation/session/Resume-AiOsSession.ps1
    }

    "workers" {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/Get-AiOsWorkerAddressBook.ps1
        powershell -ExecutionPolicy Bypass -File automation/orchestration/workers/inbox/Get-AiOsWorkerInbox.DRY_RUN.ps1
    }

    "control" {
        powershell -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1
    }

    "finish-pr" {
        if ($Pr -le 0) {
            Write-Host "BLOCKED: -Pr must be a positive PR number." -ForegroundColor Red
            exit 1
        }

        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/pr_gates/Invoke-AiOsPrFinisher.DRY_RUN.ps1 -Pr $Pr
    }

    "hud" {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/window_identity/Show-AiOsWorkerHud.DRY_RUN.ps1 -Worker $Worker
    }

    "operator-relief" {
        $moduleName = "automation.operator_relief.run_full_auto_dry_run"

        Write-Host ""
        Write-Host "== AI_OS Operator Relief Full-Auto DRY_RUN ==" -ForegroundColor Cyan
        Write-Host "Mode: DRY_RUN"
        Write-Host "Python module: $moduleName"
        Write-Host "Safety: no commit, no push, no merge, no OpenAI API, no recursive Codex, no telemetry write, no approval queue write, no daemon."

        if ([string]::IsNullOrWhiteSpace($TaskJson)) {
            Write-Host ""
            Write-Host "Usage:" -ForegroundColor Yellow
            Write-Host ".\aios.ps1 -Mode operator-relief -TaskJson .\local_full_auto_task.json"
            Write-Host ""
            Write-Host "BLOCKED: -TaskJson must point to a real FullAutoTask JSON file." -ForegroundColor Red
            exit 1
        }

        if (-not (Test-Path -LiteralPath $TaskJson -PathType Leaf)) {
            Write-Host ""
            Write-Host "Usage:" -ForegroundColor Yellow
            Write-Host ".\aios.ps1 -Mode operator-relief -TaskJson .\local_full_auto_task.json"
            Write-Host ""
            Write-Host "BLOCKED: task JSON file not found: $TaskJson" -ForegroundColor Red
            exit 1
        }

        $resolvedTaskJson = (Resolve-Path -LiteralPath $TaskJson).Path
        Write-Host "Task JSON: $resolvedTaskJson"
        Write-Host "Running: python -m $moduleName --task-json $resolvedTaskJson"
        python -m $moduleName --task-json $resolvedTaskJson
        exit $LASTEXITCODE
    }

    "bridge" {
        $moduleName = "automation.operator_relief.inbox_outbox_bridge"

        Write-Host ""
        Write-Host "== AI_OS Operator Relief Inbox/Outbox Bridge ==" -ForegroundColor Cyan
        Write-Host "Mode: DRY_RUN"
        Write-Host "Python module: $moduleName"
        Write-Host "Safety: no commit, no push, no merge, no OpenAI API, no recursive Codex, no daemon, no watcher, no service, no shell passthrough, no source mutation."

        if ([string]::IsNullOrWhiteSpace($TaskJson)) {
            Write-Host ""
            Write-Host "Usage:" -ForegroundColor Yellow
            Write-Host ".\aios.ps1 -Mode bridge -TaskJson .\reports\operator_relief\inbox\task.json"
            Write-Host ""
            Write-Host "BLOCKED: -TaskJson must point to a real inbox FullAutoTask JSON file." -ForegroundColor Red
            exit 1
        }

        if (-not (Test-Path -LiteralPath $TaskJson -PathType Leaf)) {
            Write-Host ""
            Write-Host "Usage:" -ForegroundColor Yellow
            Write-Host ".\aios.ps1 -Mode bridge -TaskJson .\reports\operator_relief\inbox\task.json"
            Write-Host ""
            Write-Host "BLOCKED: task JSON file not found: $TaskJson" -ForegroundColor Red
            exit 1
        }

        $resolvedTaskJson = (Resolve-Path -LiteralPath $TaskJson).Path
        Write-Host "Task JSON: $resolvedTaskJson"
        Write-Host "Running: python -m $moduleName --task-json $resolvedTaskJson"
        python -m $moduleName --task-json $resolvedTaskJson
        exit $LASTEXITCODE
    }

    "runtime" {

    powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "BLOCKED: proof verification failed" -ForegroundColor Red
        exit 1
    }

    powershell -ExecutionPolicy Bypass -File automation/intake/Start-AiOsRuntimeLoop.ps1 -Goal $Goal -Apply
}

   "supervisor" {
    powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/scheduler/Invoke-AiOsSchedulerPreview.DRY_RUN.ps1
}

   "mission" {
    $missionArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "automation/mission_control/New-AiOsMissionPlan.ps1",
        "-Goal",
        $Goal,
        "-WorkerCount",
        $WorkerCount,
        "-Preset",
        $Preset
    )

    if (-not [string]::IsNullOrWhiteSpace($MissionName)) {
        $missionArgs += @("-MissionName", $MissionName)
    }

    if ($ApplyMission) {
        $missionArgs += "-Apply"
    }

    powershell @missionArgs
}

   "runner" {
    if ([string]::IsNullOrWhiteSpace($MissionPath)) {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/command_runner/Invoke-AiOsCommandRunner.DRY_RUN.ps1
        break
    }

    $runnerArgs = @(
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        "automation/mission_control/Get-AiOsMissionNextAction.ps1",
        "-MissionPath",
        $MissionPath
    )

    if (-not [string]::IsNullOrWhiteSpace($TaskId)) {
        $runnerArgs += @("-TaskId", $TaskId)
    }

    if ($ShowPrompt) {
        $runnerArgs += "-ShowPrompt"
    }

    powershell @runnerArgs
}

   "queue" {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/command_queue/Get-AiOsCommandQueue.DRY_RUN.ps1
}

   "telemetry" {
        powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/telemetry_viewer/Show-AiOsTelemetryViewer.DRY_RUN.ps1
}

   "layout" {
        $sep = "-" * 79
        Write-Host ""
        Write-Host "  AI_OS 5-WORKER TERMINAL LAYOUT" -ForegroundColor Cyan
        Write-Host "  $sep"
        Write-Host ""
        Write-Host "  ZONE MAP (1920x1080 reference)" -ForegroundColor White
        Write-Host "  +-----------------------+---------------------------+"
        Write-Host "  |                       |  2. CODEX BUILD LANE      |"
        Write-Host "  |  1. AI_OS MAIN        +-------------+-------------+"
        Write-Host "  |     CONTROL           | 3. CLAUDE   | 4. VALIDATOR|"
        Write-Host "  |  left, full height    +-------------+-------------+"
        Write-Host "  |  [0,0  960x1080]      |  5. APPROVAL INBOX        |"
        Write-Host "  +-----------------------+---------------------------+"
        Write-Host ""
        Write-Host "  WORKER IDENTITIES" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host "  #  Worker                 Color    Role" -ForegroundColor DarkGray
        Write-Host "  1  AI_OS MAIN CONTROL   " -NoNewline; Write-Host "Cyan   " -NoNewline -ForegroundColor Cyan;    Write-Host "  orchestrator -- NEXT ACTION owner"
        Write-Host "  2  CODEX BUILD LANE     " -NoNewline; Write-Host "Blue   " -NoNewline -ForegroundColor Blue;    Write-Host "  executor     -- file edits, build tasks"
        Write-Host "  3  CLAUDE REVIEWER      " -NoNewline; Write-Host "Magenta" -NoNewline -ForegroundColor Magenta; Write-Host "  reviewer     -- DRY_RUN inspection"
        Write-Host "  4  VALIDATOR WORKER     " -NoNewline; Write-Host "Yellow " -NoNewline -ForegroundColor Yellow;  Write-Host "  validator    -- CI checks, git diff/status"
        Write-Host "  5  APPROVAL INBOX       " -NoNewline; Write-Host "Green  " -NoNewline -ForegroundColor Green;   Write-Host "  approval gate -- operator decisions only"
        Write-Host ""
        Write-Host "  BANNER COMMANDS (run in each worker terminal)" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "AI_OS MAIN CONTROL" -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "CODEX BUILD LANE"   -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "CLAUDE REVIEWER"    -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "VALIDATOR WORKER"   -Mode DRY_RUN'
        Write-Host '  powershell -File automation/operator/Show-AiOsWorkerBanner.ps1 -Worker "APPROVAL INBOX"     -Mode DRY_RUN'
        Write-Host ""
        Write-Host "  WINDOWS TERMINAL PROFILE DRAFT" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host "  docs/AI_OS/interface/WINDOWS_TERMINAL_PROFILES_DRAFT.md"
        Write-Host "  Copy profile entries manually to settings.json -- do not auto-edit."
        Write-Host ""
        Write-Host "  WINDOW SNAPPING" -ForegroundColor White
        Write-Host "  $sep"
        Write-Host "  Manual snap recommended until zones are validated."
        Write-Host "  FancyZones scripting deferred to next implementation step."
        Write-Host ""
        Write-Host "  STOP POINT" -ForegroundColor Yellow
        Write-Host "  $sep"
        Write-Host "  DRY_RUN display only. No windows launched. No files changed." -ForegroundColor Yellow
        Write-Host "  Open each worker manually in a new Windows Terminal tab." -ForegroundColor Yellow
        Write-Host ""
    }

   "packet" {
    # Validate worker
    $supportedWorkers = @("claude")
    if ([string]::IsNullOrWhiteSpace($Worker) -or $supportedWorkers -notcontains $Worker) {
        Write-Host ""
        Write-Host "BLOCKED: unknown or missing worker." -ForegroundColor Red
        Write-Host "  Supported workers : $($supportedWorkers -join ', ')"
        Write-Host "  Usage             : .\aios.ps1 packet <worker> <preset>"
        Write-Host "  Example           : .\aios.ps1 packet claude audit-docs"
        Write-Host ""
        exit 1
    }

    # Validate preset
    $supportedPresets = @("audit-docs")
    if ([string]::IsNullOrWhiteSpace($PacketPreset) -or $supportedPresets -notcontains $PacketPreset) {
        Write-Host ""
        Write-Host "BLOCKED: unknown or missing preset." -ForegroundColor Red
        Write-Host "  Supported presets for '$Worker' : $($supportedPresets -join ', ')"
        Write-Host "  Usage                          : .\aios.ps1 packet <worker> <preset>"
        Write-Host "  Example                        : .\aios.ps1 packet claude audit-docs"
        Write-Host ""
        exit 1
    }

    # APPLY mode — not yet supported
    if ($ExecutionMode -eq "APPLY") {
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Red
        Write-Host "║  [ APPLY PACKET — NOT SUPPORTED YET ]                           ║" -ForegroundColor Red
        Write-Host "║  APPLY mode is not implemented in packet generation yet.        ║" -ForegroundColor Red
        Write-Host "║  All packets are DRY_RUN only at this stage.                   ║" -ForegroundColor Red
        Write-Host "╚══════════════════════════════════════════════════════════════════╝" -ForegroundColor Red
        Write-Host ""
        Write-Host "Rerun without -ExecutionMode APPLY to generate a DRY_RUN packet." -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }

    $ts  = Get-Date -Format "yyyy-MM-dd HH:mm"
    $sep = "=" * 68

    $packet = @"

$sep
  AI_OS CLAUDE DELEGATION PACKET
  Generated : $ts
  Preset    : $PacketPreset
  Worker    : $Worker
  Mode      : DRY_RUN
  STATUS    : REVIEW BEFORE SENDING -- do not auto-paste
$sep

ROLE:
  Isolated documentation auditor.

MODE:
  DRY_RUN. No files changed. Output is preview-only.

SCOPE:
  Allowed paths:
    docs/AI_OS/
    docs/governance/
    docs/infrastructure/
    docs/workflows/
    docs/audits/
    docs/decisions/
  Blocked paths:
    apps/
    services/
    automation/
    scripts/
    agent/
    aios/
    Reports/  (read allowed, write blocked)
    Any file containing: credentials, secrets, tokens, keys, .env
  Blocked actions:
    No commits. No pushes. No git staging.
    No file edits. No automation creation. No frontend code.
    No live trading. No broker connections.

RULES:
  - DRY_RUN only. Do not edit any file.
  - Report findings first. One finding per line.
  - Mark unverified facts as UNKNOWN.
  - Mark conflicting evidence as MISMATCH.
  - One role. One purpose. One output.

TASK:
  1. Inspect docs/AI_OS/ for files that do not carry a status label
     (DRAFT, CANDIDATE, CURRENT, HISTORICAL, SUPERSEDED).
  2. List files that reference live trading, OANDA, or broker
     execution as an active capability without a HISTORICAL or
     SUPERSEDED label.
  3. List files with no clear stop point or ownership declaration.
  Report only. Do not edit any file.

RETURN FORMAT:
  7-region worker layout per:
  docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md
  Findings: one per line, PASS/WARN/FAIL/UNKNOWN label.
  Next Safe Action: one exact instruction.

STOP POINT:
  Stop after producing the findings report.
  Do not edit files. Do not proceed to APPLY without a separate
  explicit operator instruction.

ESCALATION PATH:
  If a protected governance file (AGENTS.md, RISK_POLICY.md,
  SECURITY.md, COMPLIANCE_BASELINE.md) requires labeling:
  output WARN and stop. Do not edit the file.

APPROVAL STATE:
  NOT_REQUIRED (DRY_RUN -- no files changed).

$sep
  NEXT OPERATOR ACTION:
  Review this packet. Confirm the allowed paths match your intent.
  Copy the text above. Paste into Claude Code manually.
  Do NOT send without reading the full packet.
$sep
"@

    Write-Host $packet
}
}

Write-Host "AIOS SHORTCUT END" -ForegroundColor Green


