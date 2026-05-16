param(
    [switch]$Preview
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoPath = "C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN"
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$preflightScript = Join-Path $scriptRoot "Show-AiOsLauncherPreflight.ps1"
$menuScript = Join-Path $scriptRoot "Show-AiOsOperatorMenu.ps1"
$commandDeck = Join-Path $scriptRoot "Start-AiOsCommandDeck.ps1"
$buildEngine = Join-Path $scriptRoot "Start-AiOsBuildEngine.ps1"
$validationDeck = Join-Path $scriptRoot "Start-AiOsValidationDeck.ps1"
$border = "#" * 100

function Start-Deck {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if ($Preview) {
        Write-Host "PREVIEW: would open $Name with $Path" -ForegroundColor Yellow
        return
    }

    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-NoExit",
        "-File",
        $Path
    ) -WindowStyle Normal
}

if (-not (Test-Path -LiteralPath $repoPath -PathType Container)) {
    throw "AI_OS repo path not found: $repoPath"
}

Set-Location -LiteralPath $repoPath
$Host.UI.RawUI.WindowTitle = "AI_OS ONE-COMMAND LAUNCHER"

Write-Host $border -ForegroundColor Cyan
Write-Host "AI_OS ONE-COMMAND LAUNCHER" -ForegroundColor Cyan
Write-Host "Opens the Command Deck, Build Engine, and Validation Deck safely." -ForegroundColor Gray
Write-Host "Codex launch remains manual. PowerToys/FancyZones placement remains manual." -ForegroundColor Yellow
Write-Host $border -ForegroundColor Cyan
Write-Host ""

& $preflightScript
Write-Host ""
& $menuScript
Write-Host ""

Write-Host "Deck launch plan:" -ForegroundColor Cyan
Write-Host "  1. Ai_Os COMMAND DECK" -ForegroundColor Magenta
Write-Host "  2. Ai_Os BUILD ENGINE" -ForegroundColor Green
Write-Host "  3. Ai_Os VALIDATION DECK" -ForegroundColor Cyan
Write-Host ""

Start-Deck -Name "Ai_Os COMMAND DECK" -Path $commandDeck
Start-Deck -Name "Ai_Os BUILD ENGINE" -Path $buildEngine
Start-Deck -Name "Ai_Os VALIDATION DECK" -Path $validationDeck

Write-Host ""
Write-Host "Exact next safe action:" -ForegroundColor Yellow
if ($Preview) {
    Write-Host "Preview complete. Run without -Preview only when you are ready to open the three deck windows." -ForegroundColor Gray
} else {
    Write-Host "Place windows manually with PowerToys/FancyZones. Launch Codex manually only inside the Build Engine." -ForegroundColor Gray
}
