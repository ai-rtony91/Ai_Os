Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRootResolverPath = Join-Path (Split-Path -Parent $PSScriptRoot) "bootstrap\Resolve-AiOsRepoRoot.ps1"
$roleName = "SAFETY DECK / VAULT GATE"
$border = "#" * 100
$titleIcon = [char]::ConvertFromUtf32(0x1F510)  # Lock - vault gate

if (-not (Test-Path -LiteralPath $repoRootResolverPath -PathType Leaf)) {
    throw "AI_OS repo root resolver not found: $repoRootResolverPath"
}

. $repoRootResolverPath

$repoPath = Resolve-AiOsRepoRoot -StartPath $PSScriptRoot

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = $roleName

Write-Host $border -ForegroundColor White
Write-Host ""
Write-Host "  $titleIcon  SAFETY DECK / VAULT GATE" -ForegroundColor Yellow
Write-Host "  LOOK FOR THIS COLOR TO IDENTIFY THIS WINDOW." -ForegroundColor Yellow
Write-Host ""
Write-Host "  AIOS BASE : #05070b  TEXT #e5f6ff  WARNING #ffd166  DANGER #ff5f7a" -ForegroundColor Gray
Write-Host "  OCC LANE  : WEST_OCC  |  Doctrine and safety inspection lane" -ForegroundColor White
Write-Host "  MODE      : [ DRY_RUN ]  Review only — no mutation" -ForegroundColor Gray
Write-Host "  STATUS    : [ READ-ONLY ]  No commit, no push, no broker access" -ForegroundColor Gray
Write-Host "  Repo      : $repoPath" -ForegroundColor Gray
Write-Host ""
Write-Host $border -ForegroundColor White
Write-Host $border -ForegroundColor White
Write-Host $border -ForegroundColor Yellow
Write-Host "  === COPY START ===" -ForegroundColor Yellow
Write-Host "  Paste terminal output between COPY START and COPY END when sending to Claude." -ForegroundColor White
Write-Host "  === COPY END ===" -ForegroundColor Yellow
Write-Host $border -ForegroundColor Yellow
Write-Host ""
Write-Host "  Manual safety review targets:" -ForegroundColor Green
Write-Host "    [ BLOCKED PATHS ]  broker/, oanda/, webhooks/, live_trading/, secrets/, .env" -ForegroundColor Red
Write-Host "    [ PROTECTED   ]  apps/dashboard/, .git/, .codex_backups/" -ForegroundColor Yellow
Write-Host "    [ GOVERNANCE  ]  README.md, RISK_POLICY.md, AGENTS.md, ARCHITECTURE.md" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Blocked actions:" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  broker, OANDA, API keys, webhooks, real orders, live trading" -ForegroundColor Red
Write-Host "    [ BLOCKED ]  startup tasks, scheduled tasks, commit, push" -ForegroundColor Red
Write-Host ""

$waitScriptPath = Join-Path $PSScriptRoot "Wait-AiOsVisibleTerminal.ps1"
& $waitScriptPath -State "IDLE" -Message "Safety Deck remains visible for vault-gate review."
