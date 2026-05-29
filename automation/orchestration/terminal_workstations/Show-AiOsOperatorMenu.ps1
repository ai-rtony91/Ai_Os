Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F451)  # Crown - MAIN CONTROL / COMMAND THRONE
$orchestratorIcon = [char]::ConvertFromUtf32(0x1F9ED)
$gateIcon = [char]::ConvertFromUtf32(0x1F6E1)
$routingIcon = [char]::ConvertFromUtf32(0x1F4E1)
$nextActionIcon = [char]::ConvertFromUtf32(0x26A1)

function Write-AiOsAnsiBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [string]$ForegroundCode = "97",

        [string]$BackgroundCode = "46"
    )

    $escape = [char]27
    Write-Host "$($escape)[$BackgroundCode;$ForegroundCode`m $Text $($escape)[0m"
}

function Write-AiOsPanelLine {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,

        [Parameter(Mandatory = $true)]
        [string]$Text,

        [string]$ForegroundCode = "97",

        [string]$BackgroundCode = "48;5;24"
    )

    $escape = [char]27
    $line = ("  {0,-14} {1}" -f $Label, $Text)
    Write-Host "$($escape)[$BackgroundCode;$ForegroundCode`m$line$($escape)[0m"
}

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = "AI_OS OPERATOR MENU"

Write-Host $border -ForegroundColor Cyan
Write-Host ""
Write-AiOsAnsiBlock -Text "  $titleIcon  MAIN CONTROL · COMMAND THRONE  " -BackgroundCode "48;5;93"
Write-AiOsAnsiBlock -Text "  $orchestratorIcon  ORCHESTRATOR  " -BackgroundCode "48;5;24"
Write-AiOsAnsiBlock -Text "  $gateIcon  HUMAN-GATED  " -BackgroundCode "48;5;220" -ForegroundCode "30"
Write-AiOsAnsiBlock -Text "  $routingIcon  WORKER ROUTING  " -BackgroundCode "48;5;45" -ForegroundCode "30"
Write-AiOsAnsiBlock -Text "  $nextActionIcon  NEXT SAFE ACTION  " -BackgroundCode "48;5;33"
Write-Host ""
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Cyan
Write-Host ""
Write-AiOsPanelLine -Label "PALETTE" -Text "base #05070b | text #e5f6ff | action #38bdf8 | glow #00a3ff | violet #a855f7"
Write-AiOsPanelLine -Label "SIGNALS" -Text "gold #ffd166 | red #ff5f7a | green reserved for PASS/OCC activity" -ForegroundCode "93"
Write-AiOsPanelLine -Label "OCC LANE" -Text "ALL LANES | persistent decks remain open for operator session" -ForegroundCode "96"
Write-AiOsPanelLine -Label "MODE" -Text "[ DRY_RUN ] simple read-only commands only" -ForegroundCode "96"
Write-AiOsPanelLine -Label "STATUS" -Text "[ READ-ONLY ] no destructive actions" -ForegroundCode "96"
Write-AiOsPanelLine -Label "REPO" -Text $repoPath -ForegroundCode "96"
Write-AiOsPanelLine -Label "WINDOWS" -Text "Acrylic/transparent appearance is template-only; this script edits no settings." -ForegroundCode "37"
Write-Host ""
Write-Host $border -ForegroundColor Cyan
Write-Host ""

Write-Host "  [ LAUNCH ]  Workstation (master launcher):" -ForegroundColor Green
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1"
Write-Host ""
Write-Host "  [ LAUNCH ]  Preview workstation:" -ForegroundColor Green
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsOneCommandLauncher.ps1 -Preview"
Write-Host ""
Write-Host "  [ STATUS ]  Repo status:" -ForegroundColor Cyan
Write-Host "    git status --short --branch"
Write-Host ""
Write-Host "  [ STATUS ]  GitHub preflight:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1"
Write-Host ""
Write-Host "  [ STATUS ]  Supervisor:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/supervisor/Start-AiOsSupervisor.ps1"
Write-Host ""
Write-Host "  [ STATUS ]  Operator control loop:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1"
Write-Host ""
Write-Host "  [ MAGENTA ]  MAIN CONTROL / COMMAND THRONE  — Git, GitHub CLI, commits, merges:" -ForegroundColor Magenta
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsCommandDeck.ps1"
Write-Host ""
Write-Host "  [ GREEN   ]  BUILD ENGINE / BUILDER FORGE  — temporary OCC worker lane:" -ForegroundColor Green
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsBuildEngine.ps1"
Write-Host ""
Write-Host "  [ CYAN    ]  VALIDATION DECK / EVIDENCE SHIELD  — validators, queue checks, repo checks:" -ForegroundColor Cyan
Write-Host "    powershell -ExecutionPolicy Bypass -File automation/orchestration/terminal_workstations/Start-AiOsValidationDeck.ps1"
Write-Host ""
Write-Host "  Next safe action:" -ForegroundColor Yellow
Write-Host "  Run preflight, then work from Command Deck, Build Engine, or Validation Deck."
Write-Host "  Launch Codex manually only inside the Build Engine."
Write-Host "  Keep persistent decks open all day unless the operator closes them."
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  commit, push, merge, branch creation, PR/issue creation" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  installs, scheduled tasks, startup tasks, Codex auto-launch" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, live trading" -ForegroundColor Red

$waitScriptPath = Join-Path $PSScriptRoot "Wait-AiOsVisibleTerminal.ps1"
& $waitScriptPath -State "IDLE" -Message "Operator menu remains visible for command routing."
