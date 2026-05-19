param(
    [ValidateSet("help","daily","morning","swarm","status","resume","workers","runtime","supervisor","mission","runner","packet","layout","control")]
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
        Write-Host ".\aios.ps1 -Mode supervisor # run repeated runtime self-routing cycles"
        Write-Host ".\aios.ps1 -Mode mission -Goal ""Improve AIOS runtime automation"" # create Mission Control plan DRY_RUN"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation # show next safe mission action"
        Write-Host ".\aios.ps1 -Mode runner -MissionPath automation/mission_control/missions/improve-aios-runtime-automation -TaskId MC-01 -ShowPrompt # show task prompt"
        Write-Host ".\aios.ps1 -Mode layout  # show 5-worker terminal layout plan and banner commands"
        Write-Host ".\aios.ps1 -Mode control # show operator control loop cockpit"
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

    powershell -ExecutionPolicy Bypass -File checkpoints/verify_success.ps1

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "BLOCKED: proof verification failed" -ForegroundColor Red
        exit 1
    }

    powershell -ExecutionPolicy Bypass -File automation/orchestration/runtime/Start-AiOsPersistentRuntimeSupervisor.ps1 -Cycles 3 -Apply
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
        Write-Host "BLOCKED: -MissionPath is required for runner mode." -ForegroundColor Red
        exit 1
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


