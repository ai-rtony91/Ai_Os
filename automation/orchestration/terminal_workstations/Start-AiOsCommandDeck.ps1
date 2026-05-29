Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot
$roleName = "MAIN CONTROL / COMMAND THRONE"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F451)
$orchestratorIcon = [char]::ConvertFromUtf32(0x1F9ED)
$gateIcon = [char]::ConvertFromUtf32(0x1F6E1)
$routingIcon = [char]::ConvertFromUtf32(0x1F4E1)
$nextActionIcon = [char]::ConvertFromUtf32(0x26A1)

function Write-AiOsAnsiBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [string]$ForegroundCode = "97",

        [string]$BackgroundCode = "45"
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

function Write-AiOsStatusBadge {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Text,

        [string]$Code = "96"
    )

    $escape = [char]27
    Write-Host "$($escape)[$Code`m[$Text]$($escape)[0m" -NoNewline
}

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor Magenta
Write-Host ""
Write-AiOsAnsiBlock -Text "  $titleIcon  MAIN CONTROL · COMMAND THRONE  " -BackgroundCode "48;5;93"
Write-AiOsAnsiBlock -Text "  $orchestratorIcon  ORCHESTRATOR  " -BackgroundCode "48;5;24"
Write-AiOsAnsiBlock -Text "  $gateIcon  HUMAN-GATED  " -BackgroundCode "48;5;220" -ForegroundCode "30"
Write-AiOsAnsiBlock -Text "  $routingIcon  WORKER ROUTING  " -BackgroundCode "48;5;45" -ForegroundCode "30"
Write-AiOsAnsiBlock -Text "  $nextActionIcon  NEXT SAFE ACTION  " -BackgroundCode "48;5;33"
Write-Host ""
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Magenta
Write-Host ""
Write-AiOsPanelLine -Label "PALETTE" -Text "base #05070b | text #e5f6ff | violet #a855f7 | cyan #38bdf8 | glow #00a3ff"
Write-AiOsPanelLine -Label "SIGNALS" -Text "green=PASS/OCC | amber=warning/gate | red=blocked/danger | gold=command authority" -ForegroundCode "93"
Write-AiOsPanelLine -Label "OCC LANE" -Text "MAIN_CONTROL | persistent deck remains open for operator session" -ForegroundCode "95"
Write-AiOsPanelLine -Label "MODE" -Text "[ MANUAL ] operator control only - no auto-launch" -ForegroundCode "96"
Write-AiOsPanelLine -Label "STATUS" -Text "[ READ-ONLY ] no Codex auto-launch, no scheduled/startup tasks" -ForegroundCode "96"
Write-AiOsPanelLine -Label "REPO" -Text $repoPath -ForegroundCode "96"
Write-AiOsPanelLine -Label "WINDOWS" -Text "Acrylic/transparent appearance is template-only; this script edits no settings." -ForegroundCode "37"
Write-Host ""
Write-Host "  STATUS STRIP  " -NoNewline -ForegroundColor DarkCyan
Write-AiOsStatusBadge -Text "CI" -Code "96"
Write-Host "  " -NoNewline
Write-AiOsStatusBadge -Text "GATED" -Code "93"
Write-Host "  " -NoNewline
Write-AiOsStatusBadge -Text "WORKING" -Code "38;5;208"
Write-Host "  " -NoNewline
Write-AiOsStatusBadge -Text "COMPLETE" -Code "92"
Write-Host "  " -NoNewline
Write-AiOsStatusBadge -Text "BLOCKED" -Code "91"
Write-Host ""
Write-Host ""
Write-Host $border -ForegroundColor Magenta
Write-Host $border -ForegroundColor Magenta
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Allowed actions:" -ForegroundColor Green
Write-Host "    [ PASS ]  git status --short --branch" -ForegroundColor Green
Write-Host "    [ PASS ]  git log --oneline -5" -ForegroundColor Green
Write-Host "    [ PASS ]  gh --version" -ForegroundColor Green
Write-Host "    [ PASS ]  gh issue list --state open" -ForegroundColor Green
Write-Host "    [ PASS ]  gh pr list --state open" -ForegroundColor Green
Write-Host "    [ GATE ]  selective commit/merge only after explicit Human Owner approval" -ForegroundColor Yellow
Write-Host "    [ ROUTE ]  route temporary OCC workers; workers remain IDLE, COMPLETE, BLOCKED, or CLOSED" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Worker activity row:" -ForegroundColor Cyan
Write-AiOsPanelLine -Label "OCC ACTIVE" -Text "reuse the same worker lane through APPLY -> validate -> commit -> push/sync -> final COMPLETE" -ForegroundCode "92"
Write-AiOsPanelLine -Label "OCC BLOCKED" -Text "park visibly for operator review; do not stack unlimited new worker windows" -ForegroundCode "91"
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  Codex auto-launch, extra windows, startup/scheduled tasks" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  dashboard edits" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host ""

$waitScriptPath = Join-Path $PSScriptRoot "Wait-AiOsVisibleTerminal.ps1"
& $waitScriptPath -State "IDLE" -Message "MAIN CONTROL remains visible for human-gated routing and next safe action review."
