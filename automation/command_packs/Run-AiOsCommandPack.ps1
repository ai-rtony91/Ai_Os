param(
    [Parameter(Mandatory = $true)][string]$Pack,
    [switch]$Apply
)

Set-StrictMode -Off
$ErrorActionPreference = "Stop"

$packPath = "automation/command_packs/packs/$Pack.json"
$commandValidatorPath = "automation/orchestration/validators/Test-AiOsRecommendedCommand.ps1"

function Invoke-AiOsValidatedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Command
    )

    if (-not (Test-Path -LiteralPath $commandValidatorPath -PathType Leaf)) {
        throw "Command validator missing: $commandValidatorPath"
    }

    powershell -NoProfile -ExecutionPolicy Bypass -File $commandValidatorPath $Command
    if ($LASTEXITCODE -ne 0) {
        throw "Command validator blocked command: $Command"
    }

    $normalizedCommand = $Command.Trim()

    if ($normalizedCommand -match "(?i)^git\s+(status|diff|log|show)\b(.*)$") {
        $gitArgs = @($Matches[1])
        if (-not [string]::IsNullOrWhiteSpace($Matches[2])) {
            $gitArgs += @($Matches[2].Trim() -split "\s+")
        }

        & git @gitArgs
        return
    }

    if ($normalizedCommand -notmatch "(?i)^powershell(?:\.exe)?(?:\s+-NoProfile)?\s+-ExecutionPolicy\s+Bypass\s+-File\s+((?:'[^']+')|(?:`"[^`"]+`")|(?:\S+))(.*)$") {
        throw "Only validated read-only git commands and repo-scoped PowerShell file commands are executable."
    }

    $scriptPath = $Matches[1].Trim("'`"")
    $argumentText = $Matches[2].Trim()
    $arguments = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $scriptPath)

    if (-not [string]::IsNullOrWhiteSpace($argumentText)) {
        $parseErrors = $null
        $argumentTokens = [System.Management.Automation.PSParser]::Tokenize($argumentText, [ref]$parseErrors) |
            Where-Object { $_.Type -in @("CommandArgument", "String", "Number", "Parameter") } |
            ForEach-Object { $_.Content.Trim("'`"") }
        if ($parseErrors.Count -gt 0) {
            throw "Command arguments are not valid PowerShell syntax."
        }
        $arguments += @($argumentTokens)
    }

    & powershell @arguments
}

Write-Host "COPY START - Run-AiOsCommandPack.ps1"
Write-Host "AI_OS Command Pack Runner" -ForegroundColor Cyan
Write-Host "Mode: $(if ($Apply) { 'APPLY' } else { 'DRY_RUN' })"
Write-Host "Pack: $Pack"

if (-not (Test-Path $packPath)) {
    throw "Command pack not found: $packPath"
}

$packData = Get-Content -Raw $packPath | ConvertFrom-Json

Write-Host ""
Write-Host "Pack title: $($packData.title)"
Write-Host "Steps: $(@($packData.steps).Count)"

foreach ($step in @($packData.steps)) {
    Write-Host ""
    Write-Host "STEP $($step.id): $($step.title)" -ForegroundColor Yellow
    Write-Host "command: $($step.command)"

    if ($step.requires_apply -and -not $Apply) {
        Write-Host "Skipped: requires -Apply"
        continue
    }

    if ($Apply -or -not $step.requires_apply) {
        Invoke-AiOsValidatedCommand -Command ([string]$step.command)
    }
}

Write-Host ""
Write-Host "Commit performed: NO"
Write-Host "Push performed: NO"
Write-Host "COPY END - Run-AiOsCommandPack.ps1"
